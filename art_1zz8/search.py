"""Search crank-rocker linkage space for hero coupler curves.
Contact sheet of candidates with metrics: self-crossings, aspect, dwell contrast."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from fourbar import trace, grashof, cognates
from PIL import Image, ImageDraw, ImageFont

def curve_metrics(OA, OB, a, b, c, mu, n=4000):
    t = trace(OA, OB, a, b, c, mu, n, +1)
    if not t['ok'].all():           # want a full-rotation crank branch (closed curve)
        return None
    P = t['P']
    al, be, ga = t['alpha'], t['beta'], t['gamma']
    # arc-length + dwell densities
    dP = np.abs(np.roll(P, -1) - P)
    L = dP.sum()
    if L < 1e-6: return None
    ds = np.maximum(dP, 1e-12)
    dal = np.abs(np.angle(np.exp(1j*(np.roll(al,-1)-al))))
    dbe = np.abs(np.angle(np.exp(1j*(np.roll(be,-1)-be))))
    dga = np.abs(np.angle(np.exp(1j*(np.roll(ga,-1)-ga))))
    w1, w2, w3 = dal/ds, dga/ds, dbe/ds      # machine 1/2/3 dwell densities
    # normalize to probability measures on the curve
    for w in (w1, w2, w3): w /= (w*ds).sum()
    # measure disagreement: mean total-variation-ish contrast
    tot = w1+w2+w3
    frac = np.array([w1, w2, w3]) / np.maximum(tot, 1e-12)
    contrast = float(np.mean(frac.std(0)))
    # self-intersections on decimated polyline
    Q = P[::n//600]
    m = len(Q)
    x1, y1 = Q.real, Q.imag
    x2, y2 = np.roll(x1,-1), np.roll(y1,-1)
    def seg_int_count():
        cnt = 0
        for i in range(m):
            j = np.arange(i+2, m - (1 if i==0 else 0))
            d1 = (x2[i]-x1[i])*(y1[j]-y1[i]) - (y2[i]-y1[i])*(x1[j]-x1[i])
            d2 = (x2[i]-x1[i])*(y2[j]-y1[i]) - (y2[i]-y1[i])*(x2[j]-x1[i])
            d3 = (x2[j]-x1[j])*(y1[i]-y1[j]) - (y2[j]-y1[j])*(x1[i]-x1[j])
            d4 = (x2[j]-x1[j])*(y2[i]-y1[j]) - (y2[j]-y1[j])*(x2[i]-x1[j])
            cnt += int(np.sum((d1*d2 < 0) & (d3*d4 < 0)))
        return cnt
    nx = seg_int_count()
    # bbox aspect of curve+pivots ensemble
    OC = cognates(OA, OB, a, b, c, mu)[2]
    allpts = np.concatenate([P[::10], [OA, OB, OC]])
    W = allpts.real.max()-allpts.real.min(); H = allpts.imag.max()-allpts.imag.min()
    aspect = W/max(H,1e-9)
    # curve size relative to pivot triangle spread
    curveW = max(P.real.max()-P.real.min(), P.imag.max()-P.imag.min())
    return dict(P=P, w=(w1,w2,w3), ds=ds, L=L, nx=nx, aspect=aspect,
                contrast=contrast, OC=OC, curveW=curveW,
                spread=max(W,H))

def render_thumb(mtr, OA, OB, size=360):
    P, OC = mtr['P'], mtr['OC']
    allpts = np.concatenate([P[::5], [OA, OB, OC]])
    cx, cy = allpts.real.mean(), allpts.imag.mean()
    half = 0.56*max(allpts.real.max()-allpts.real.min(), allpts.imag.max()-allpts.imag.min())
    img = np.zeros((size, size, 3), np.float32)
    def to_px(z):
        x = (z.real-cx)/half*0.5+0.5; y = 0.5-(z.imag-cy)/half*0.5
        return x*size, y*size
    w1, w2, w3 = mtr['w']
    hues = np.array([[1.0,0.78,0.35],[0.35,0.85,1.0],[0.9,0.5,1.0]])
    X, Y = to_px(P)
    ix, iy = X.astype(int), Y.astype(int)
    okm = (ix>=0)&(ix<size)&(iy>=0)&(iy<size)
    ds = mtr['ds']
    for w, h in zip((w1,w2,w3), hues):
        val = (w*ds)[okm]
        np.add.at(img, (iy[okm], ix[okm]), h[None,:]*val[:,None]*size*2.2)
    for z, col in ((OA,(1,.9,.6)),(OB,(1,.9,.6)),(OC,(1,.9,.6))):
        x, y = to_px(np.array(z))
        xi, yi = int(x), int(y)
        if 1<=xi<size-1 and 1<=yi<size-1: img[yi-1:yi+2, xi-1:xi+2] += np.array(col)*0.8
    out = 1-np.exp(-img*1.4)
    return (np.clip(out,0,1)**(1/1.9)*255).astype(np.uint8)

def main():
    rng = np.random.RandomState(20260717)
    cands = []
    tries = 0
    while len(cands) < 60 and tries < 4000:
        tries += 1
        g = 4.0
        a = rng.uniform(0.5, 1.6)
        b = rng.uniform(1.5, 5.0)
        c = rng.uniform(1.5, 5.0)
        cls, ex = grashof(g, a, b, c)
        if cls != 'crank-rocker' or ex > -0.15:   # comfortably Grashof
            continue
        mu = rng.uniform(0.15, 1.1) + 1j*rng.uniform(-1.5, 1.5)
        if abs(mu) < 0.25 or abs(mu-1) < 0.25:    # avoid near-degenerate triangles
            continue
        OA, OB = 0+0j, g+0j
        mtr = curve_metrics(OA, OB, a, b, c, mu)
        if mtr is None: continue
        if not (0.6 < mtr['aspect'] < 1.6): continue
        if mtr['curveW'] < 0.45*mtr['spread']: continue    # curve must not be a dot
        if mtr['nx'] < 1: continue
        score = mtr['contrast']*3 + min(mtr['nx'],3)*0.15 - abs(np.log(mtr['aspect']))*0.3
        cands.append((score, dict(a=a,b=b,c=c,mu=mu,g=g), mtr))
    cands.sort(key=lambda t: -t[0])
    print(f'{len(cands)} candidates from {tries} tries')
    cols, rows = 6, 8
    N = min(cols*rows, len(cands))
    thumb = 360
    sheet = Image.new('RGB', (cols*thumb, rows*(thumb+22)), (8,8,10))
    dr = ImageDraw.Draw(sheet)
    for k in range(N):
        score, prm, mtr = cands[k]
        im = Image.fromarray(render_thumb(mtr, 0+0j, prm['g']+0j, thumb))
        r, ccol = divmod(k, cols)
        sheet.paste(im, (ccol*thumb, r*(thumb+22)))
        dr.text((ccol*thumb+4, r*(thumb+22)+thumb+2),
                f"#{k} s={score:.2f} nx={mtr['nx']} ctr={mtr['contrast']:.2f} a={prm['a']:.2f} b={prm['b']:.2f} c={prm['c']:.2f} mu={prm['mu']:.2f}",
                fill=(200,200,190))
    sheet.save(os.path.join(os.path.dirname(__file__), 'proto', 'search_sheet.png'))
    # persist params
    import json
    with open(os.path.join(os.path.dirname(__file__), 'proto', 'candidates.json'), 'w') as f:
        json.dump([dict(score=float(s), a=p['a'], b=p['b'], c=p['c'], g=p['g'],
                        mu_re=p['mu'].real, mu_im=p['mu'].imag,
                        nx=int(m['nx']), contrast=float(m['contrast']))
                   for s, p, m in cands[:N]], f, indent=1)
    print('sheet saved')

if __name__ == '__main__':
    main()
