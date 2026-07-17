"""Companion 1: Every Pen of One Machine (the dual of the hero).

The hero shows three machines drawing ONE curve. Here: ONE machine (the very
same four-bar as the hero), every possible pen. Each coupler point mu traces
its own sextic; brightness = the machine's clock (uniform crank speed, equal
light per second), so big fast signatures are faint and slow dwells blaze.
The hero's actual pen mu* is the one near-white curve. Warm shore = pens below
the coupler line AB, cool shore = pens above."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from scipy.ndimage import gaussian_filter
from fourbar import trace
from rkit import Canvas

def mu_color(mu):
    """2-D curated ramp on the coupler plane."""
    tre = np.clip((mu.real + 0.45)/1.9, 0, 1)
    if mu.imag >= 0:   # cool shore
        c0 = np.array([0.30, 0.82, 1.00]); c1 = np.array([0.52, 0.42, 1.00])
    else:              # warm shore
        c0 = np.array([1.00, 0.72, 0.28]); c1 = np.array([0.95, 0.42, 0.85])
    col = c0*(1-tre) + c1*tre
    # desaturate softly near the coupler line (pens ON the rod)
    fade = np.clip(abs(mu.imag)/0.25, 0, 1)
    pale = np.array([0.85, 0.88, 0.92])
    return col*fade + pale*(1-fade)*0.55

def render(prm, S=1280, SS=2, nmu=(64, 52), nsamp_base=2600, variant='A',
           mu_sigma=0.38, gain=1.0, hero_gain=1.0, frame_half=None,
           fname='proto/pen_proto.png', k=1.5, gamma=1.9, seed=0):
    OA, OB = 0+0j, prm['g']+0j
    a, b, c = prm['a'], prm['b'], prm['c']
    mu_hero = prm['mu_re'] + 1j*prm['mu_im']
    # one shared motion, many pens: P(mu) = A + mu*(B-A)
    W = S*SS
    nsamp = int(nsamp_base*(W/2048.0))
    t = trace(OA, OB, a, b, c, 0.5, nsamp, +1)
    assert t['ok'].all()
    A, B = t['A'], t['B']
    D = B - A

    # framing: central mass of the family
    if frame_half is None:
        # pens in the box [-0.45..1.45] x [-1.05..1.05]
        pass
    mu_hero_c = mu_hero
    rng = np.random.RandomState(seed)
    # build the pen list per variant
    pens = []          # (mu, color, mass_factor)
    if variant == 'A':
        mre = np.linspace(-0.2, 1.2, nmu[0])
        mim = np.linspace(-0.75, 0.75, nmu[1])
        jre = (mre[1]-mre[0]); jim = (mim[1]-mim[0])
        for m_i in mim:
            for m_r in mre:
                mu = (m_r + rng.uniform(-.5,.5)*jre) + 1j*(m_i + rng.uniform(-.5,.5)*jim)
                d = abs(mu - mu_hero_c)
                w = np.exp(-d*d/(2*mu_sigma**2)) + 0.06
                pens.append((mu, mu_color(mu), w))
    else:              # 'B': concentric pen-families around the rod midpoint
        STOPS = np.array([[0.15,0.26,1.00],   # deep indigo
                          [0.50,0.32,1.00],   # violet
                          [0.95,0.40,0.90],   # orchid
                          [1.00,0.50,0.30],   # ember
                          [1.00,0.76,0.22]])  # amber
        radii = np.linspace(0.24, 1.06, 6)
        for ri, r in enumerate(radii):
            tt = ri/(len(radii)-1)*(len(STOPS)-1)
            i0 = int(np.floor(tt)); f = tt-i0
            col = STOPS[i0]*(1-f) + STOPS[min(i0+1, len(STOPS)-1)]*f
            npen = int(40 + 26*r/0.24)
            for q in range(npen):
                th = 2*np.pi*(q + 0.5*(ri%2))/npen
                mu = 0.5 + r*np.exp(1j*th)
                pens.append((mu, col, 1.0))
    # frame on the central mass of the family
    sample_pts = [A[::37] + mu*D[::37] for mu, _, _ in pens[::5]]
    allz = np.concatenate(sample_pts + [np.array([OA, OB])])
    cx = np.median(allz.real); cy = np.median(allz.imag)
    half = frame_half or 1.15*np.percentile(np.abs(allz - (cx+1j*cy)), 78)
    cv = Canvas(S, SS, cx, cy, half)

    m0 = gain*(0.0135 if variant == 'A' else 0.045)
    for mu, col, wf in pens:
        ph = rng.randint(nsamp)
        Pm = np.roll(A + mu*D, ph)
        cv.splat(Pm, col, m0*wf)
    # the machine's two ground pivots
    for z in (OA, OB):
        cv.glow_points([z], np.array([1.0,0.93,0.75]), amp=2.8, sigma=3.2*SS*(W/2048.0)/2)
        cv.glow_points([z], np.array([1.0,0.85,0.55]), amp=0.8, sigma=11*SS*(W/2048.0)/2)
    # crank circle + follower arc: the two degenerate pens (mu=0, mu=1)
    for Q, amp in ((A, 1.0), (B, 1.0)):
        cv.lines(Q[::16], np.roll(Q,-16)[::16], np.array([1.0,0.95,0.85]),
                 mass_per_px=0.09*amp*(W/2048.0))
    # the frozen machine + its pen-wheel: one faint pose, rings of pens visible
    if variant == 'B':
        i0 = int(0.42*nsamp)
        Ai, Bi = A[i0], B[i0]
        rodc = (Ai+Bi)/2
        bars0 = np.array([OA, Ai, OB])
        bars1 = np.array([Ai, Bi, Bi])
        cv.wide_lines(bars0, bars1, np.array([1.0,0.9,0.7]),
                      mass_per_px=0.85, width_px=3.6*(W/2048.0))
        th = np.linspace(0, 2*np.pi, 220)
        for r in np.linspace(0.24, 1.06, 6):
            ring = rodc + r*np.abs(D[i0])*np.exp(1j*(th+np.angle(D[i0])))
            cv.splat(ring[::3], np.array([1.0,0.9,0.7]), 0.065*(W/2048.0))
        cv.glow_points([Ai, Bi], np.array([1.0,0.9,0.7]), amp=0.9,
                       sigma=2.2*SS*(W/2048.0)/2)
    # hero pen: near-white blazing curve
    Ph = A + mu_hero*D
    hbuf = Canvas(S, SS, cx, cy, half)
    hbuf.splat(Ph, np.array([1.0,0.88,0.55]), hero_gain*0.10)
    hb = hbuf.img
    sig = 1.0*SS*(W/2048.0)
    h = gaussian_filter(hb, (sig, sig, 0))
    pc = np.percentile(hb.max(-1), 99.9); ph = np.percentile(h.max(-1), 99.9)
    hb += h*(0.75*pc/max(ph, 1e-9))          # amplitude-restored halo
    cv.img += hb
    cv.glow_points([Ph[int(0.42*nsamp)]], np.array([1.0,0.97,0.9]), amp=2.2,
                   sigma=2.8*SS*(W/2048.0)/2)

    cv.tightbloom(0.30, 2.2*SS*(W/2048.0)/2)
    cv.widebloom(0.10)
    im = cv.out(k=k, gamma=gamma)
    im.save(os.path.join(os.path.dirname(__file__), fname))
    return fname

if __name__ == '__main__':
    cands = json.load(open(os.path.join(os.path.dirname(__file__),
                                        'proto/candidates2.json')))
    render(cands[3], fname='proto/pen_proto.png')
    print('saved')
