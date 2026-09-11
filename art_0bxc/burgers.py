"""burgers.py — 'The Tree of Shocks': one-dimensional sticky dust in space–time, exactly.

u_t + u u_x = 0 with sticking (Burgers at zero viscosity).  Each particle q flies straight,
x = q + t u0(q), until it meets its neighbour; then the two stick, and the lump moves with the MEAN
initial velocity of everything it has eaten (momentum is conserved on the hull edge):
    x_s(t) = (q_a + q_b)/2 + t * mean(u0 on [q_a, q_b]).
At every time the free particles are the vertices of the lower convex hull of (q, q^2/2t - phi0(q));
every gap between consecutive vertices is a shock.  Time runs UP the sheet: fine roots of many small
shocks at the bottom merging into a few trunks at the top — a dendrite that gravity would draw.
Warm threads: dust moving right; cool threads: dust moving left; ink: the shocks, width by mass;
coral: the birth of each shock (the instant two neighbours first touch).
"""
import numpy as np, sys, json, time
from scipy.ndimage import gaussian_filter
from scipy.spatial import ConvexHull
from PIL import Image, ImageDraw
sys.path.insert(0, '.')
from pastel import Sheet, PIG, absorb, text_density, finish, text_width, discs_density, lowfreq


def velocity_field(n, seed, n_index=0.0, k_cut=None, k_low=1.0, amp=1.0):
    """periodic u0 on n points of [0,1) with energy spectrum E(k) ~ k^n_index exp(-(k/k_cut)^2),
    phi0 with u0 = -phi0'.  amp = rms of u0."""
    rng = np.random.default_rng(seed)
    k = np.fft.rfftfreq(n, d=1.0 / n)          # in units of 2pi
    with np.errstate(divide='ignore', invalid='ignore'):
        P = np.where(k > 0, k ** n_index, 0.0)
    k_cut = k_cut or n / 8
    P = P * np.exp(-(k / k_cut) ** 2) * (1 - np.exp(-(k / k_low) ** 2))
    uk = np.fft.rfft(rng.standard_normal(n)) * np.sqrt(P)
    u = np.fft.irfft(uk, n=n)
    u -= u.mean(); u *= amp / u.std()
    # phi0: u = -phi', so phi_k = -u_k/(i k 2pi)
    uk = np.fft.rfft(u)
    with np.errstate(divide='ignore', invalid='ignore'):
        pk = np.where(k > 0, -uk / (1j * 2 * np.pi * k), 0.0)
    phi = np.fft.irfft(pk, n=n)
    return u, phi


def hull_row(q, phi, t):
    """1-D lower hull of (q, q^2/2t - phi): returns sorted vertex indices."""
    psi = q * q / (2 * t) - phi
    pts = np.column_stack([q, psi])
    # monotone chain would do; scipy's 2-D hull is C and fast
    hull = ConvexHull(pts)
    v = hull.vertices
    # lower part: vertices between the leftmost and rightmost, going along the lower side
    v = np.sort(v)
    # keep those on the lower hull: test against chord-based criterion via equations
    eq = hull.equations  # a x + b y + c = 0, outward normal (a,b)
    low = eq[:, 1] < 0
    lv = np.unique(hull.simplices[low].ravel())
    return np.sort(lv)


def run(n=4096, seed=1, T=1.0, n_index=0.0, k_cut=None, amp=1.0, rows=2048, margin=None, t_min=None):
    """march time in `rows` equal steps; returns per-row shocks and per-particle absorption times."""
    margin = margin or n // 4
    u, phi = velocity_field(n, seed, n_index, k_cut, amp=amp)
    idx = np.arange(-margin, n + margin)
    q = idx / n
    U = u[idx % n]; PH = phi[idx % n] - (idx // n) * (phi[0] - phi[0])   # phi periodic (mean-zero u => periodic)
    # phi periodic only if the mean of u is zero (it is); no drift term needed
    m_ins = (idx >= 0) & (idx < n)
    tc = np.full(len(q), np.inf)
    shocks = []          # per row: (t, xs array, mass array, umean array, born mask)
    ts = np.geomspace(t_min, T, rows) if t_min else T * (np.arange(1, rows + 1)) / rows
    stats = []
    t0 = time.time()
    for r, t in enumerate(ts):
        v = hull_row(q, PH, t)
        free = np.zeros(len(q), bool); free[v] = True
        newly = ~free & np.isinf(tc)
        tc[newly] = t
        # gaps between consecutive vertices
        a, b = v[:-1], v[1:]
        gap = (b - a) > 1
        a, b = a[gap], b[gap]
        mass = (b - a)                            # particles swallowed + boundary pair => interval [a,b]
        umean = -(PH[b] - PH[a]) / (q[b] - q[a])
        xs = 0.5 * (q[a] + q[b]) + t * umean
        # born now: every particle strictly inside (a,b) got tc == t (nothing inside was stuck before)
        born = np.array([np.all(tc[a_ + 1:b_] == t) for a_, b_ in zip(a, b)], bool) if len(a) else np.zeros(0, bool)
        keep = (q[a] >= -0.02) & (q[b] <= 1.02)
        shocks.append((t, xs[keep], mass[keep].astype(float), umean[keep], born[keep]))
        if r % max(1, rows // 64) == 0 or r == rows - 1:
            ins = m_ins
            nsh = int(((q[a] >= 0) & (q[a] < 1)).sum())
            E = 0.5 * (np.sum(U[ins & free] ** 2) + np.sum((mass * umean ** 2)[(q[a] >= 0) & (q[a] < 1)])) / n
            stats.append(dict(t=float(t), n_shocks=nsh, energy=float(E), free_fraction=float(free[ins].mean())))
    print(f'march {time.time() - t0:.1f}s; final shocks {stats[-1]["n_shocks"]}', flush=True)
    return dict(q=q, u=U, phi=PH, tc=tc, shocks=shocks, ts=ts, stats=stats, n=n, T=T, m_ins=m_ins, t_min=t_min)


def render(FINAL_W=1280, FINAL_H=2048, SS=2, tag='proto_tree', n=4096, seed=1, T=1.0, n_index=0.0, k_cut=None,
           amp=1.0, rows=None, thread_d=0.55, thread_w=0.6, ink_w0=0.15, ink_pow=0.4, ink_d=0.9, bead_r=1.6, spine_w=0.22, ribbon_d=1.1,
           caption=True, title='The Tree of Shocks', gran=0.1, knee=1.0,
           sub='dust that flies straight and sticks where it meets; every lump moves with the mean speed of all it has eaten',
           x_window=(0.0, 1.0), data=None, t_min=None, wmax=7.0, spine_max=1.2):
    t0 = time.time()
    W, H = FINAL_W * SS, FINAL_H * SS
    rs = FINAL_W / 1024.0 * SS
    rows = rows or H
    d = data or run(n, seed, T, n_index, k_cut, amp, rows=rows, t_min=t_min)
    q, u, tc, ts = d['q'], d['u'], d['tc'], d['ts']
    x0, x1 = x_window
    Sx = W / (x1 - x0)

    def X(x):
        return (x - x0) * Sx

    def Y(t):
        if t_min:
            t = np.maximum(t, t_min)
            return H - 1 - np.log(t / t_min) / np.log(T / t_min) * (H - 1)
        return H - 1 - t / T * (H - 1)

    sheet = Sheet(W, H, seed=seed + 3)
    cert = dict(n=n, seed=seed, T=T, n_index=n_index, amp=amp, rows=int(rows), stats=d['stats'])
    # ---- threads: free flight of every particle until it sticks (straight lines), warm right / cool left
    umax = np.percentile(np.abs(u), 99)
    fam = {}
    for name in ['lemon', 'apricot', 'mint', 'cornflower']:
        fam[name] = Image.new('F', (W, H), 0.0)
    drs = {k: ImageDraw.Draw(v) for k, v in fam.items()}
    sel = np.nonzero((q >= x0 - 0.3) & (q <= x1 + 0.3))[0]
    for i in sel:
        te = tc[i] if np.isfinite(tc[i]) else T
        if t_min:
            tt = np.geomspace(t_min, max(te, t_min * 1.0001), 24)
        else:
            tt = np.linspace(0.0, te, 2)
        pts = [(float(X(q[i] + t_ * u[i])), float(Y(t_))) for t_ in tt]
        s = min(1.0, abs(u[i]) / umax)
        w_slow, w_fast = (1 - s), s
        wd = int(max(1, round(thread_w * rs)))
        if u[i] >= 0:
            drs['lemon'].line(pts, fill=float(thread_d * w_slow), width=wd)
            drs['apricot'].line(pts, fill=float(thread_d * w_fast), width=wd)
        else:
            drs['mint'].line(pts, fill=float(thread_d * w_slow), width=wd)
            drs['cornflower'].line(pts, fill=float(thread_d * w_fast), width=wd)
    tot = None
    fields = {}
    for name, im in fam.items():
        f = gaussian_filter(np.asarray(im, np.float32), 0.6 * rs)
        fields[name] = f
        tot = f if tot is None else tot + f
    scale = np.percentile(tot[tot > 0], 90) if (tot > 0).any() else 1.0
    for name, f in fields.items():
        sheet.wash(np.tanh(f / (knee * scale)) * (f / (tot + 1e-9)) * 1.0, name, granulate=gran)
    # ---- shocks: width by mass; tinted by the lump's mean velocity (warm right / cool left, lighter when
    # slow) so that momentum conservation is visible as colour mixing at every merger; a thin ink spine
    ink = np.zeros((H, W), np.float32)
    tint = {k: np.zeros((H, W), np.float32) for k in ['lemon', 'apricot', 'mint', 'cornflower']}
    births = []
    xx = np.arange(W, dtype=np.float32)
    uref = np.percentile(np.abs(u), 90)
    for (t, xs, mass, um, born) in d['shocks']:
        r = int(round(Y(t)))
        if r < 0 or r >= H:
            continue
        wpx = np.maximum(wmax * rs * np.sqrt(mass / n), 0.45 * rs)
        wsp = np.maximum(spine_max * rs * np.sqrt(mass / n), 0.3 * rs)
        for xsi, wi, wsi, umi, bi in zip(X(xs), wpx, wsp, um, born):
            lo, hi = int(max(0, xsi - 3 * wi - 2)), int(min(W, xsi + 3 * wi + 3))
            if hi <= lo:
                continue
            prof = np.exp(-((xx[lo:hi] - xsi) / max(wi, 0.6)) ** 4)     # flat-topped ribbon
            sp = np.exp(-((xx[lo:hi] - xsi) / max(wsi, 0.5)) ** 2)
            ink[r, lo:hi] += sp
            s_ = min(1.0, abs(umi) / uref)
            if umi >= 0:
                tint['lemon'][r, lo:hi] += prof * (1 - s_); tint['apricot'][r, lo:hi] += prof * s_
            else:
                tint['mint'][r, lo:hi] += prof * (1 - s_); tint['cornflower'][r, lo:hi] += prof * s_
            if bi:
                births.append((xsi, r))
    for k, f in tint.items():
        f = gaussian_filter(f, 0.3 * rs)
        sheet.wash(np.clip(f, 0, 1) * ribbon_d, k, granulate=gran)
    ink = gaussian_filter(ink, 0.35 * rs)
    sheet.wash(np.clip(ink, 0, 1) * ink_d, 'ink')
    # ---- coral beads at the births
    if births:
        bx = np.array([b[0] for b in births]); by = np.array([b[1] for b in births])
        bead = discs_density(W, H, bx, by, np.full(len(bx), bead_r * rs), np.full(len(bx), 1.0), sigma=0.5 * rs)
        sheet.wash(np.clip(bead, 0, 1) * 1.4, 'coral')
    cert['n_births'] = len(births)
    # unfinished edge left/right, and a paper fade at the very top (the future)
    yy, xg = np.mgrid[0:H, 0:W].astype(np.float32)
    dd = np.minimum(xg, W - 1 - xg) / W
    wob = 1 + 0.5 * lowfreq(H, W, max(16, W // 5), seed + 9, 1.0)
    t_ = np.clip(dd / (0.06 * wob), 0, 1); keep = t_ * t_ * (3 - 2 * t_)
    top = np.clip(yy / (0.05 * H), 0, 1); keep *= top * top * (3 - 2 * top)
    sheet.lighten(1 - keep, 1.0)
    if caption:
        ts_ = int(0.030 * W); ss = int(0.0135 * W)
        sheet.caption_strip(0.945, 0.992, f=0.62)
        items = [(title, int(0.045 * W), int(0.958 * H), ts_, 'serif_bold', 'ls')]
        if text_width(sub, ss, 'italic') > 0.9 * W:
            print('CAPTION OVERRUN', text_width(sub, ss, 'italic') / W)
        items.append((sub, int(0.045 * W), int(0.981 * H), ss, 'italic', 'ls'))
        sheet.wash(text_density(W, H, items) * 1.2, 'ink')
    img = sheet.develop()
    finish(img, (FINAL_W, FINAL_H), f'{tag}_{FINAL_H}.png')
    cert['secs'] = time.time() - t0
    json.dump(cert, open(f'{tag}_{FINAL_H}_cert.json', 'w'), indent=1)
    print('stats', json.dumps(d['stats'][::8]))
    return d


if __name__ == '__main__':
    kw = {}
    for a in sys.argv[1:]:
        k, v = a.split('=', 1)
        try:
            v = json.loads(v)
        except Exception:
            pass
        kw[k] = v
    render(**kw)
