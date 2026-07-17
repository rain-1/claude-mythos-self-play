"""Hero: The Three Cognates — one coupler curve, three machines, three clocks.

Machine 1 (OA,OB): motor at OA drives alpha. Machine 2 (OA,OC): motor at OC
drives gamma. Machine 3 (OB,OC): motor at OB drives beta. Same curve; the
three dwell measures |d alpha|, |d gamma|, |d beta| disagree -> hue tells
which clock lingers where; brightness = the three-clock mean dwell."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from scipy.ndimage import gaussian_filter
from fourbar import trace, cognates
from rkit import Canvas, lines_scalar
from scipy.ndimage import zoom as ndzoom

HUES = dict(m1=np.array([1.00, 0.72, 0.28]),   # gold
            m2=np.array([0.30, 0.82, 1.00]),   # cyan
            m3=np.array([0.95, 0.42, 0.85]))   # rose-violet

def machine_joints(t, OA, OB, a, b, c, mu):
    al, be, ga = t['alpha'], t['beta'], t['gamma']
    OC = OA + mu*(OB - OA)
    A, B, P = t['A'], t['B'], t['P']
    J1 = OA + mu*b*np.exp(1j*be); J2 = OC + mu*c*np.exp(1j*ga)
    K1 = OB + (mu-1)*b*np.exp(1j*be); K2 = OC + (1-mu)*a*np.exp(1j*al)
    return OC, dict(m1=(A, B), m2=(J1, J2), m3=(K1, K2))

def render(prm, S=1024, SS=2, ncurve=400000, nexpo=12, nfog=500,
           curve_gain=1.0, ghost_gain=1.0, fog_gain=1.0, orbit_gain=1.0,
           frame_pad=1.42, sat_q=1.6, fname='proto/hero_proto.png',
           k=1.35, gamma=1.9):
    OA, OB = 0+0j, prm['g']+0j
    a, b, c, mu = prm['a'], prm['b'], prm['c'], prm['mu_re']+1j*prm['mu_im']
    t = trace(OA, OB, a, b, c, mu, ncurve, +1)
    assert t['ok'].all(), 'need full-rotation branch'
    P = t['P']
    OC, joints = machine_joints(t, OA, OB, a, b, c, mu)

    # ---- framing: the CURVE is the hero; pivots may sit near edges
    allz = np.concatenate([P[::7], [OA, OB, OC]])
    xmin, xmax = allz.real.min(), allz.real.max()
    ymin, ymax = allz.imag.min(), allz.imag.max()
    cx, cy = (xmin+xmax)/2, (ymin+ymax)/2
    half = 0.5*frame_pad*max((xmax-xmin), (ymax-ymin))
    cv = Canvas(S, SS, cx, cy, half)
    W = cv.W
    rs = W/2048.0            # resolution scale vs accepted proto

    # ---- machine ghost fog: dense coupler-edge exposures (envelope mist)
    # rendered at LOW resolution as scalar mass per machine, then upsampled.
    # mass = gain*C*fogW/nfog makes field brightness independent of nfog & res;
    # nfog only sets grain. C calibrated to the accepted proto look.
    fogW = W//2 if S <= 1536 else W//4
    fog = fog_gain*0.01504*fogW/nfog
    rngf = np.random.RandomState(11)
    for mk in ('m1','m2','m3'):
        Ja, Jb = joints[mk]
        fidx = (rngf.rand(nfog)*len(P)).astype(int)   # jitter kills aliasing rays
        piv = dict(m1=(OA,OB), m2=(OA,OC), m3=(OB,OC))[mk]
        buf = np.zeros((fogW, fogW), np.float32)
        # coupler triangle edges (the moving body) — these envelope the curve
        f0 = np.concatenate([Ja[fidx], Jb[fidx], Ja[fidx]])
        f1 = np.concatenate([P[fidx],  P[fidx],  Jb[fidx]])
        lines_scalar(fogW, cx, cy, half, f0, f1, fog, buf=buf)
        # crank/follower lines much fainter (they fan around the pivots)
        g0 = np.concatenate([np.full(nfog, piv[0]), np.full(nfog, piv[1])])
        g1 = np.concatenate([Ja[fidx], Jb[fidx]])
        lines_scalar(fogW, cx, cy, half, g0, g1, fog*0.30, buf=buf)
        up = ndzoom(buf, W/fogW, order=1)[:W, :W]
        cv.img += up[:, :, None]*HUES[mk][None, None, :]
        del buf, up

    # ---- ONE bold physical pose per machine: caught drawing the same line
    barw = 4.2*(W/2048.0)
    ghost = ghost_gain*1.1
    pivots = dict(m1=(OA,OB), m2=(OA,OC), m3=(OB,OC))
    # auto-pick poses: all joints well inside frame, machines mutually spread
    def centroid(mk, i):
        Ja, Jb = joints[mk]
        return (Ja[i] + Jb[i] + P[i])/3
    def pose_score(mk, i, taken):
        Ja, Jb = joints[mk]
        pts = np.array([Ja[i], Jb[i], P[i]])
        Xp, Yp = cv.to_px(pts)
        margin = min(Xp.min(), Yp.min(), W-Xp.max(), W-Yp.max())/W
        s = margin
        for (omk, j) in taken:
            s += 0.30*min(abs(P[i]-P[j])/half, 1.0)
            s += 0.45*min(abs(centroid(mk,i)-centroid(omk,j))/half, 0.8)
        return s if margin > 0.02 else -1e9
    pose_at = prm.get('poses')
    taken = []
    for mk in ('m1','m2','m3'):
        if pose_at:
            i = int(pose_at[mk]*len(P)) % len(P)
        else:
            cand_i = (np.arange(96)*len(P))//96
            i = max(cand_i, key=lambda ii: pose_score(mk, ii, taken))
        taken.append((mk, i))
        Ja, Jb = joints[mk]
        piv = pivots[mk]
        hue = HUES[mk]
        # ground link: faint chord between this machine's two pivots
        cv.lines(np.array([piv[0]]), np.array([piv[1]]), hue,
                 mass_per_px=ghost*0.08)
        # crank + follower bars
        segs0 = np.array([piv[0], piv[1]])
        segs1 = np.array([Ja[i],  Jb[i]])
        cv.wide_lines(segs0, segs1, hue, mass_per_px=ghost, width_px=barw)
        # coupler body: translucent glass triangle + faint edge outline
        cv.fill_tri(Ja[i], Jb[i], P[i], hue, mass_per_px2=ghost*0.035)
        e0 = np.array([Ja[i], Jb[i], Ja[i]])
        e1 = np.array([Jb[i], P[i],  P[i]])
        cv.lines(e0, e1, hue, mass_per_px=ghost*0.38)
        # joint beads + pen-on-curve spark
        cv.glow_points([Ja[i], Jb[i]], hue*1.15, amp=1.1, sigma=2.4*SS*rs)
        cv.glow_points([P[i]], np.array([1.0,0.97,0.9]), amp=1.5, sigma=2.8*SS*rs)

    # ---- moving-joint orbits (thin arcs)
    orb = orbit_gain*0.05*(W/2048.0)
    for mk in ('m1','m2','m3'):
        Ja, Jb = joints[mk]
        for Q in (Ja, Jb):
            cv.lines(Q[::40], np.roll(Q,-40)[::40], HUES[mk]*0.9, mass_per_px=orb)

    # ---- the shared curve: own buffer, fraction-hue x mean-dwell luminance
    def dvar(th):
        d = np.angle(np.exp(1j*(np.roll(th,-1)-th)))
        return np.abs(d)
    dm = np.array([dvar(t['alpha']), dvar(t['gamma']), dvar(t['beta'])])
    dm /= dm.sum(1, keepdims=True)           # each clock = probability measure
    ds = np.abs(np.roll(P,-1)-P)
    ds_px = ds*W/(2*half)
    lum = dm.sum(0)/np.maximum(ds_px, 1e-9)  # total dwell per curve-pixel
    lum /= np.percentile(lum, 35)            # median-ish -> 1
    frac = dm/np.maximum(dm.sum(0, keepdims=True), 1e-30)
    fq = frac**sat_q; fq /= fq.sum(0, keepdims=True)
    colhues = np.stack([HUES['m1'], HUES['m2'], HUES['m3']])
    col = (fq[:,:,None]*colhues[:,None,:]).sum(0)
    curve_buf = Canvas(S, SS, cx, cy, half)
    base = curve_gain*0.62
    curve_buf.splat(P, col, base*np.minimum(lum, 24.0)*ds_px)
    cb = curve_buf.img
    # fatten with AMPLITUDE-RESTORED halos (blur dilutes peak ~sigma^2; rescale
    # each halo back to a fraction of the core's peak so the stroke survives
    # any downscale)
    if rs <= 1.01:
        cb += 0.85*gaussian_filter(cb, (1.0*SS, 1.0*SS, 0))
    else:
        pc = np.percentile(cb.max(-1), 99.9)
        raw = cb.copy()
        for sig, fr in ((2.2*SS, 0.9), (1.0*SS*rs, 0.5)):
            h = gaussian_filter(raw, (sig, sig, 0))
            ph = np.percentile(h.max(-1), 99.9)
            if ph > 1e-9:
                cb += h*(fr*pc/ph)
    cv.img += cb

    # ---- ground pivots
    for z in (OA, OB, OC):
        cv.glow_points([z], np.array([1.0,0.93,0.75]), amp=2.4, sigma=3.2*SS*rs)
        cv.glow_points([z], np.array([1.0,0.85,0.55]), amp=0.9, sigma=11*SS*rs)

    cv.tightbloom(0.32, 2.2*SS*rs)
    cv.widebloom(0.10)
    im = cv.out(k=k, gamma=gamma)
    im.save(os.path.join(os.path.dirname(__file__), fname))
    return fname

if __name__ == '__main__':
    with open(os.path.join(os.path.dirname(__file__), 'proto/candidates.json')) as f:
        cands = json.load(f)
    which = [int(x) for x in sys.argv[1:]] or [0]
    for w in which:
        prm = cands[w]
        out = render(prm, fname=f'proto/hero_c{w}.png')
        print('saved', out)
