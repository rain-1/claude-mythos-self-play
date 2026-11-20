"""ladder.py S out.png — 'Five Digits, Four Ends': the 2 x 9 ladder in base 5 (25 adjacencies)
can never say all 25 pairs; the best possible is 24.  Engraved vignette."""
import sys, numpy as np
from PIL import Image
from intaglio import *
from hero import frame, smooth

# best ladder found (24 of 25 distinct pairs); row 0 = left rail, row 1 = right rail, index = rung (0 = bottom)
G = [[3, 4, 0, 1, 4, 2, 2, 1, 1], [3, 1, 0, 2, 4, 3, 0, 3, 2]]

def fbm(rng, shape, scales, amps):
    out = np.zeros(shape, np.float32)
    for sc, a in zip(scales, amps):
        n = ndi.gaussian_filter(rng.standard_normal(shape).astype(np.float32), sc, mode='wrap'); out += a*n/(n.std() + 1e-6)
    return out

def main():
    S = int(sys.argv[1]); out = sys.argv[2]
    P = Plate(S, seed=11); u = P.u; rng = np.random.default_rng(5)
    px0, py0, px1, py1 = 230*u, 190*u, 3866*u, 3826*u; bw = 110*u
    ix0, iy0, ix1, iy1 = px0 + bw + 26*u, py0 + bw + 26*u, px1 - bw - 26*u, py1 - bw - 26*u
    P.layer('dark'); P.layer('red')
    frame(P, px0, py0, px1, py1, bw)
    for (x, y) in ((px0 + bw/2, py0 + bw/2), (px0 + bw/2, py1 - bw/2), (px1 - bw/2, py0 + bw/2), (px1 - bw/2, py1 - bw/2)):
        medallion(P, x, y, 78*u, 2, 10, numeral=False, w=1.8*u)
    sl, xx, yy = P.box(ix0, iy0, ix1, iy1)
    X = xx/u; Y = yy/u; H, W = X.shape
    # ---------- the scene as a tone map ----------
    sx, sy, sr = 2880.0, 1010.0, 215.0
    ds = np.sqrt((X - sx)**2 + (Y - sy)**2)
    sky = 0.40 - 0.30*np.exp(-ds/900.0) + 0.22*np.clip((1500 - Y)/1500, 0, 1)**1.5*np.clip((3300 - X)/2600, 0.25, 1) - 0.14*np.clip((Y - 1700)/1300, 0, 1)
    # clouds
    nz = fbm(rng, (H, W), [(26*u, 90*u), (12*u, 40*u), (5*u, 16*u)], [1.0, 0.55, 0.25])
    band = np.exp(-((Y - 1560)/330)**2)*1.25 + np.exp(-((Y - 2360)/210)**2)*0.95 + np.exp(-((Y - 760)/170)**2)*0.75 - 0.52
    cl = smooth((nz*0.62 + band - 0.38)/0.34)
    clb = ndi.gaussian_filter(cl, (22*u, 22*u))
    under = np.clip(np.roll(clb, int(-34*u), 0) - clb*0.25, 0, 1)        # shade the undersides
    cloud_tone = 0.015 + 0.30*np.clip(1.6*(clb - np.roll(clb, int(40*u), 0)), 0, 1)
    Tsky = sky*(1 - cl) + cloud_tone*cl
    sun = np.clip((sr - ds)/u + 0.5, 0, 1)
    Tsky = Tsky*(1 - sun)
    Usky = (Y + 5*np.sin(2*np.pi*X/310.0))/13.0
    c_sky = P.engrave_field(Tsky, Usky, wmin=0.07, wmax=0.86)
    # rays: a radial family close to the sun, fading out
    th = np.arctan2(Y - sy, X - sx)
    ray_t = np.clip(1 - (ds - sr)/560.0, 0, 1)*(ds > sr + 16)*(1 - cl)
    Ur = th*96/(2*np.pi)
    gr = 96/(2*np.pi*np.maximum(ds, 1)*u)            # |grad| in px^-1
    dr = np.abs(Ur - np.round(Ur))/gr
    c_ray = aa(dr, 2.0*u*ray_t + 0.1)*(ray_t > 0.03)*(np.round(Ur) % 2 == 0) + aa(dr, 1.3*u*ray_t)*(ray_t > 0.35)*(np.round(Ur) % 2 == 1)
    c_sun = aa(np.abs(ds - sr)*u, 3.0*u)
    cov = np.maximum(c_sky*(1 - np.clip(ray_t*1.5, 0, 0.6)), np.maximum(c_ray, c_sun))
    # hills: each ridge is engraved along its own contour
    xs = X[0]
    def ridge(base, amp, seed, sc):
        r = np.random.default_rng(seed)
        n = ndi.gaussian_filter1d(r.standard_normal(W + 2000).astype(np.float32), sc*u)[1000:1000+W]
        n2 = ndi.gaussian_filter1d(r.standard_normal(W + 2000).astype(np.float32), sc*u/4)[1000:1000+W]
        return base + amp*(n/(n.std() + 1e-6)) + amp*0.18*(n2/(n2.std() + 1e-6))
    ridges = [(ridge(2790, 70, 1, 300), 0.30, 15.0, 0.25), (ridge(2990, 80, 2, 240), 0.44, 14.0, -0.18),
              (ridge(3230, 70, 3, 200), 0.60, 13.0, 0.30), (ridge(3470, 46, 4, 150), 0.74, 12.0, -0.25)]
    for (yr, tone, pitch, slant) in ridges:
        below = np.clip((Y - yr[None, :])/1.0*u + 0.5, 0, 1) if False else np.clip((yy/u - yr[None, :])*u + 0.5, 0, 1)
        depth = (Y - yr[None, :])
        T = tone*(0.55 + 0.45*np.clip(depth/260.0, 0, 1)) + 0.10*np.sin(X/90.0 + depth/40.0)*0
        # light from the sun side: left slopes darker
        slope = np.gradient(ndi.gaussian_filter1d(yr, 110*u))[None, :]/u
        T = np.clip(T*(1 + 2.2*np.clip(slope, -0.5, 0.5)*np.exp(-depth/320.0)), 0.06, 0.93)
        U = (depth*(1 + 0.0) + slant*(X - 2048)*0.35 + 9*np.sin(X/75.0))/pitch
        c = P.engrave_field(T, U, wmin=0.10, wmax=0.90)
        T2 = np.clip((T - 0.5)/0.5, 0, 1)
        U2 = (X*0.86 + depth*0.5)/pitch
        c = np.maximum(c, P.engrave_field(T2*0.55, U2, wmax=0.9)*(T2 > 0.03))
        edge = aa(np.abs(depth)*u, 2.6*u)
        cov = cov*(1 - below) + np.maximum(c, edge)*below
    P.put('dark', sl, cov)
    # a pale tint under the sky
    Ut = (Y - 40*np.sin(X/140.0))/17.0
    P.put('tintC', sl, P.level_lines(Ut, 4.6*u*np.exp(-ds/1500.0)))
    P.put('tintA', sl, P.level_lines((Y + 40*np.sin(X/140.0))/17.0, 4.6*u*np.clip((Y - 1300)/1900.0, 0, 1)*(Y < 2900)))
    P.put('tintB', sl, P.level_lines(Ut + 0.5, 5.2*u*np.clip((1900 - Y)/1700, 0, 1)*(1 - np.exp(-ds/700.0))))
    # inner rule of the vignette
    d = np.minimum(np.minimum(xx - ix0, ix1 - xx), np.minimum(yy - iy0, iy1 - yy))
    P.put('dark', sl, aa(np.abs(d - 3*u), 5*u))
    # ---------- the ladder ----------
    yb, yt = 3600.0, 560.0; xc = 1560.0
    def rail(side, y):      # x of rail centre at height y (slight taper + lean)
        t = (yb - y)/(yb - yt)
        return xc + side*(330 - 95*t) + 150*t
    n = 9; ys = [yb - 250 - k*(yb - yt - 440)/(n - 1) for k in range(n)]
    sl2, x2, y2 = P.box(ix0, iy0, ix1, iy1); X2 = x2/u; Y2 = y2/u
    def strip_cov(dist, half, along_mask, shade_coord):
        inside = np.clip((half - np.abs(dist))*u + 0.5, 0, 1)*along_mask
        outline = aa(np.abs(np.abs(dist) - half)*u, 3.2*u)*along_mask
        grain = aa(np.abs(shade_coord/7.0 - np.round(shade_coord/7.0))*7.0*u, 1.5*u)*(dist > half*0.15)*inside
        return inside, np.maximum(outline, grain)
    # count pairs to find the repeated one
    pairs = {}
    for r in range(2):
        for j in range(n - 1): pairs.setdefault((G[r][j], G[r][j+1]), []).append(('rail', r, j))
    for j in range(n): pairs.setdefault((G[0][j], G[1][j]), []).append(('rung', j))
    rep = [v for v in pairs.values() if len(v) > 1][0]
    missing = [(a, b) for a in range(5) for b in range(5) if (a, b) not in pairs]
    print('distinct', len(pairs), 'repeated', [k for k, v in pairs.items() if len(v) > 1], 'missing', missing)
    def lay(inside, lines, red=False):
        P.cut('dark', sl2, inside); P.cut('tintA', sl2, inside*0.8); P.cut('tintB', sl2, inside*0.8); P.cut('tintC', sl2, inside*0.5)
        P.put('red' if red else 'dark', sl2, lines)
    # rungs first (behind the rails)
    for j in range(n):
        y = ys[j]; xa, xb = rail(-1, y), rail(1, y)
        m = ((X2 > xa) & (X2 < xb)).astype(np.float32)
        ins, ln = strip_cov(Y2 - y, 17.0, m, X2)
        lay(ins, ln, red=('rung', j) in rep)
    for r, side in ((0, -1), (1, 1)):
        xr = rail(side, Y2)
        segs = [(yt, ys[n-1], None)] + [(ys[j+1], ys[j], j) for j in range(n - 1)] + [(ys[0], yb, None)]
        for (ya, yb_, j) in segs:
            m = ((Y2 >= ya) & (Y2 < yb_)).astype(np.float32)
            ins, ln = strip_cov(X2 - xr, 25.0, m, Y2)
            lay(ins, ln, red=(j is not None and ('rail', r, j) in rep))
        # end caps
        for ye in (yt, yb):
            m = (np.abs(X2 - rail(side, ye)) < 25.0)
            P.put('dark', sl2, aa(np.abs(Y2 - ye)*u, 3.2*u)*m)
    # joints: numbered bosses
    for r, side in ((0, -1), (1, 1)):
        for j in range(n):
            x, y = rail(side, ys[j])*u, ys[j]*u; R = 58*u
            b, bx, by = P.box(x - R - 5*u, y - R - 5*u, x + R + 5*u, y + R + 5*u)
            rr = np.sqrt((bx - x)**2 + (by - y)**2)
            disc = np.clip(R - rr + 0.5, 0, 1)
            for t in ('dark', 'red', 'tintA', 'tintB', 'tintC'): P.cut(t, b, disc)
            P.put('dark', b, np.maximum(aa(np.abs(rr - R + 2*u), 3.4*u), aa(np.abs(rr - R + 11*u), 1.3*u)))
            P.text('dark', str(G[r][j]), x, y - 1*u, 74*u, 'b')
    # shadow of the ladder's feet on the near hill: short dense hatch
    # caption
    P.text('dark', 'Five Digits, Four Ends', S/2, 3905*u, 60*u, 'r')
    P.text('dark', 'Nine rungs and sixteen lengths of rail make twenty-five steps, one for each pair of five digits. The best ladder says twenty-four;', S/2, 3975*u, 34*u, 'i')
    P.text('dark', 'the pair in red is said twice and %d%d never, because every digit would need two of the four ends.' % missing[0], S/2, 4022*u, 34*u, 'i')
    img = P.render(INKS, ORDER, plate=(px0 - 30*u, py0 - 30*u, px1 + 30*u, py1 + 30*u))
    Image.fromarray(img).save(out)

if __name__ == '__main__': main()
