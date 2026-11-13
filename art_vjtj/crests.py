"""Crests in cut gold (kirikane): knots made of equal sticks, one roundel per knot type.
Every stick has length exactly 1 in space; what you see is its shadow on the lid, so the short ones
are the ones pointing at you.  Nearer gold is brighter; each joint that is not hidden is a pearl."""
import sys, json, numpy as np
from PIL import Image, ImageDraw
from makie import *

SUB = {'3_1': '3₁', '4_1': '4₁', '5_1': '5₁', '5_2': '5₂', '6_1': '6₁', '6_2': '6₂',
       '6_3': '6₃', '8_19': '8₁₉', '3_1#3_1 / 8_20': '(t²−t+1)²'}
POLY = {6: 'hexagons', 7: 'heptagons', 8: 'octagons'}

def render(size=1024, out='crests.png', seed=11, data='knots/crests.json', extra=None):
    u = size / 1024.0
    K = json.load(open(data))
    P = Panel(size, seed=seed, ss=2, sheen=0.8)
    s = P.ss
    Sb = size * s
    M = Image.new('L', (Sb, Sb), 0); Z = Image.new('L', (Sb, Sb), 0)
    dm, dz = ImageDraw.Draw(M), ImageDraw.Draw(Z)
    ring = Image.new('L', (Sb, Sb), 0); dr = ImageDraw.Draw(ring)
    pearl = Image.new('L', (Sb, Sb), 0); dp = ImageDraw.Draw(pearl)
    cxs = [0.20, 0.50, 0.80]; cys = [0.128, 0.415, 0.702]
    R = 0.100 * size
    w = 0.0072 * size            # stick width
    gap = 0.0042 * size
    texts = []
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    dust = np.zeros((size, size), np.float32)
    for idx, k in enumerate(K):
        cx = cxs[idx % 3] * size; cy = cys[idx // 3] * size
        rr = np.hypot(xx - cx, yy - cy)
        dust += 0.011 * np.clip((R - rr) / (2 * u), 0, 1) * (0.35 + 0.65 * (rr / R) ** 3)
        for rad, wd in [(R + 0.010 * size, 2.2 * u), (R + 0.0165 * size, 1.0 * u)]:
            dr.ellipse([(cx - rad) * s, (cy - rad) * s, (cx + rad) * s, (cy + rad) * s], outline=255, width=max(1, int(wd * s)))
        name = SUB[k['name']]
        ty = cy + R + 0.047 * size
        if not k['found']:
            texts.append((cx, ty, name, 17 * u, False, 'ms'))
            texts.append((cx, ty + 0.022 * size, k.get('note', 'not met'), 10.5 * u, True, 'ms'))
            continue
        V = np.array(k['V']); n = len(V)
        sc = 0.80 * R / np.hypot(V[:, 0], V[:, 1]).max()
        X = cx + sc * V[:, 0]; Y = cy + sc * V[:, 1]; Zc = V[:, 2]
        z0, z1 = Zc.min(), Zc.max()
        # under-crossing gaps, stick by stick
        import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "knots")); from alex import crossings
        Xc = crossings(np.ascontiguousarray(V))
        gaps = {i: [] for i in range(n)}
        for (eo, so, eu, su, sg) in Xc:
            eo, eu = int(eo), int(eu)
            do = np.array([X[(eo + 1) % n] - X[eo], Y[(eo + 1) % n] - Y[eo]]); du = np.array([X[(eu + 1) % n] - X[eu], Y[(eu + 1) % n] - Y[eu]])
            Lu = np.hypot(*du); sin = abs(do[0] * du[1] - do[1] * du[0]) / (np.hypot(*do) * Lu)
            half = (w / 2 + gap) / max(sin, 0.25) / Lu
            gaps[eu].append((su - half, su + half))
        for i in range(n):
            j = (i + 1) % n
            iv = [(0.0, 1.0)]
            for (g0, g1) in gaps[i]:
                nv = []
                for (a, b) in iv:
                    if g1 <= a or g0 >= b: nv.append((a, b)); continue
                    if g0 > a: nv.append((a, g0))
                    if g1 < b: nv.append((g1, b))
                iv = nv
            for (a, b) in iv:
                dm.line([((X[i] + (X[j] - X[i]) * a) * s, (Y[i] + (Y[j] - Y[i]) * a) * s), ((X[i] + (X[j] - X[i]) * b) * s, (Y[i] + (Y[j] - Y[i]) * b) * s)], fill=255, width=int(round(w * s)))
            r = w / 2
            dm.ellipse([(X[i] - r) * s, (Y[i] - r) * s, (X[i] + r) * s, (Y[i] + r) * s], fill=255)
        pieces = []
        mm = 40
        for i in range(n):
            j = (i + 1) % n
            for q in range(mm):
                a, b = q / mm, (q + 1) / mm
                pieces.append((Zc[i] * (1 - (a + b) / 2) + Zc[j] * (a + b) / 2, X[i] + (X[j] - X[i]) * a, Y[i] + (Y[j] - Y[i]) * a, X[i] + (X[j] - X[i]) * b, Y[i] + (Y[j] - Y[i]) * b))
        pieces.sort()
        for (z, xa, ya, xb, yb) in pieces:
            tone = int(255 * (0.12 + 0.88 * (z - z0) / (z1 - z0)))
            dz.line([(xa * s, ya * s), (xb * s, yb * s)], fill=tone, width=int((w + 1.2 * gap) * s))
            rz = (w + 1.2 * gap) / 2
            dz.ellipse([(xb - rz) * s, (yb - rz) * s, (xb + rz) * s, (yb + rz) * s], fill=tone)
        # pearls at visible joints
        for i in range(n):
            hidden = False
            for a in range(n):
                b = (a + 1) % n
                if a == i or b == i: continue
                ax, ay, bx, by = X[a], Y[a], X[b], Y[b]
                t = ((X[i] - ax) * (bx - ax) + (Y[i] - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)
                t = min(1, max(0, t))
                d = np.hypot(X[i] - ax - t * (bx - ax), Y[i] - ay - t * (by - ay))
                if d < w * 1.1 and Zc[a] + t * (Zc[b] - Zc[a]) > Zc[i]: hidden = True
            if not hidden:
                r = w * 0.95
                dp.ellipse([(X[i] - r) * s, (Y[i] - r) * s, (X[i] + r) * s, (Y[i] + r) * s], fill=255)
        texts.append((cx, ty, name, 17 * u, False, 'ms'))
        cnt, tot = k['unconf']
        if cnt:
            line = "%d equal sticks \u00b7 %s in %s random %s" % (n, format(cnt, ","), format(tot, ","), POLY[n])
        else:
            pc, pt, pr = k["press"]
            line = "%d equal sticks \u00b7 none in %s random; %d in %s squeezed" % (n, format(tot, ","), pc, format(pt, ","))
        texts.append((cx, ty + 0.022 * size, line, 10.5 * u, True, 'ms'))
    down = lambda im: np.asarray(im.resize((size, size), Image.LANCZOS), np.float32) / 255.0
    Mf, Zf, Rf, Pf = down(M), down(Z), down(ring), down(pearl)
    P.dust(dust, KIN, grain=0.42 * max(1, u ** 0.75), sparkle=0.08, gain=0.8)
    P.leaf(Rf, KIN, height=1.2 * u, tone=0.75, burnish=0.3, glow=0.15)
    tone = 0.25 + 0.95 * Zf
    P.leaf(Mf, KIN, height=1.8 * u, tone=tone, burnish=0.75, glow=0.0)
    P.glow += (Mf * tone * 0.22)[..., None] * KIN.astype(np.float32)
    P.raden(Pf, cell=4.5 * u, sat=0.75, val=1.15, crack=0.25)
    tl = [(0.045 * size, 0.948 * size, k_title(K), 21 * u, False, 'ls'),
          (0.045 * size, 0.972 * size, "knots made of equal sticks, found by folding random polygons and kept when the Alexander polynomial said so", 12.5 * u, True, 'ls'),
          (0.955 * size, 0.948 * size, "every stick has length 1 in space; nearer gold is brighter; each joint is a pearl", 11 * u, True, 'rs'),
          (0.955 * size, 0.972 * size, "MO 394427: is the fewest equal sticks always the fewest sticks?", 11 * u, True, 'rs')]
    P.leaf(P.text_mask(texts + tl), AOKIN, height=0.8 * u, tone=0.8, burnish=0.1, glow=0.1)
    P.finish().save(out)
    print(out)

def k_title(K):
    return "Nine Crests in Cut Gold" if all(k['found'] for k in K) else "Eight Crests and an Empty Ring"

if __name__ == '__main__':
    render(int(sys.argv[1]), sys.argv[2])
