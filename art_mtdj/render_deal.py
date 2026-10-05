"""render_deal.py — one set of threads, dealt sixteen ways (MO 515726).

Eleven pearls; a warm necklace T1 (a Hamiltonian cycle) and a cool thread P (a Hamiltonian path
from x to y, sharing no edge with T1) that closes through a coral pearl v outside the ring.
Contract v to an edge and the threads form a 4-regular graph; every way to re-deal its edges into
a warm necklace and a cool thread through v is drawn.  There are 16: the deal and 15 twins.
Because each twin uses exactly the same threads, w(warm) + w(cool) never changes — so the
original deal cannot have both the unique cheapest warm necklace and the unique cheapest cool
one.  (Exhaustive check n <= 10: every deal has an odd number of twins.)

usage: render_deal.py W H out.png [key=val ...]
"""
import sys, json, numpy as np
from PIL import Image, ImageDraw

ARG = dict(a.split('=', 1) for a in sys.argv[4:] if '=' in a)
def P(k, d): return type(d)(ARG.get(k, d))

WARM = [(0.98, 0.45, 0.55), (1.00, 0.62, 0.48), (1.00, 0.80, 0.42), (1.00, 0.62, 0.48)]
COOL = [(0.40, 0.84, 0.66), (0.42, 0.74, 0.98), (0.56, 0.58, 0.98), (0.74, 0.54, 0.96)]
def ramp(stops, t, cyclic):
    stops = np.array(stops); n = len(stops) if cyclic else len(stops) - 1
    x = (t % 1.0 if cyclic else np.clip(t, 0, 1)) * n; i = min(int(x), len(stops) - 1); f = x - int(x)
    a = stops[i % len(stops)]; b = stops[(i + 1) % len(stops)] if cyclic else stops[min(i + 1, len(stops) - 1)]
    return a ** (1 - f) * b ** f


def curve(p, q, centre, bend, perim=None, steps=48):
    """chord bowing toward the centre (quadratic Bezier); perimeter neighbours follow the circle"""
    t = np.linspace(0, 1, steps)[:, None]
    if perim is not None:
        R, a0, a1 = perim
        da = (a1 - a0 + np.pi) % (2 * np.pi) - np.pi
        ang = a0 + da * t[:, 0]
        return centre + R * np.stack([np.cos(ang), np.sin(ang)], 1)
    mid = (p + q) / 2
    ctrl = centre + (mid - centre) * bend
    return (1 - t) ** 2 * p + 2 * (1 - t) * t * ctrl + t ** 2 * q


def main():
    W, H, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    D = json.load(open(P('inst', 'ham_sheet_11_16.json')))
    n = D['n']; x, y = D['P'][0], D['P'][-1]
    SS = 3
    paper = (253, 251, 249)
    im = Image.new('RGB', (W * SS, H * SS), paper); dr = ImageDraw.Draw(im)
    cols = P('cols', 4); cell = P('cell', 590); gap = P('gapc', 22)
    left = (W - cols * cell - (cols - 1) * gap) // 2; top = P('top', 90)
    rot = P('rot', 0.0)
    pearls = []      # (cx, cy, r, kind)
    frames = []
    T1 = set(frozenset((i, (i + 1) % n)) for i in range(n))
    for idx, (cyc, path) in enumerate(D['D']):
        r_, c_ = divmod(idx, cols)
        ox = left + c_ * (cell + gap) + cell / 2; oy = top + r_ * (cell + gap) + cell / 2
        centre = np.array([ox, oy - cell * 0.045])
        R = cell * 0.33
        # vertices: angle so that x,y sit at the bottom and v below them
        mid_ang = np.pi / 2
        base = mid_ang - (x + y) / 2 * 2 * np.pi / n + rot
        if abs(x - y) > n / 2: base += np.pi
        ang = base + 2 * np.pi * np.arange(n) / n
        V = centre + R * np.stack([np.cos(ang), np.sin(ang)], 1)
        vpos = centre + np.array([0, 1.0]) * R * 1.36
        def seg(a, b):
            if (a - b) % n in (1, n - 1):
                return curve(V[a], V[b], centre, 0, perim=(R, ang[a], ang[b]))
            return curve(V[a], V[b], centre, P('bend', 0.42))
        warm = [seg(cyc[i], cyc[(i + 1) % n]) for i in range(n)]
        coolpts = [vpos] + [V[k] for k in path] + [vpos]
        cool = [curve(vpos, V[path[0]], centre, 0.0, steps=24) if True else None]
        cool = [np.linspace(vpos, V[path[0]], 24)]
        cool += [seg(path[i], path[i + 1]) for i in range(n - 1)]
        cool += [np.linspace(V[path[-1]], vpos, 24)]
        lw = cell * P('lw', 0.026)
        def ribbon(segs, stops, cyclic):
            m = len(segs)
            for pass_ in range(3):
                for j, s in enumerate(segs):
                    pts = s * SS
                    for k in range(len(pts) - 1):
                        t = (j + k / (len(pts) - 1)) / m
                        c = np.array(ramp(stops, t, cyclic))
                        if pass_ == 0: col = c * 0.80; w = lw * 1.32
                        elif pass_ == 1: col = c; w = lw
                        else: col = 1 - (1 - c) * 0.35; w = lw * 0.26
                        off = np.array([-1, -1]) * lw * 0.22 * SS if pass_ == 2 else 0
                        a, b = pts[k] + off, pts[k + 1] + off
                        rgb = tuple(int(255 * v) for v in np.clip(col, 0, 1))
                        dr.line([tuple(a), tuple(b)], fill=rgb, width=max(1, int(w * SS)))
                        rr = w * SS / 2
                        dr.ellipse([b[0] - rr, b[1] - rr, b[0] + rr, b[1] + rr], fill=rgb)
        # changed threads: faint coral halo under every warm edge that was cool in the deal
        if idx > 0:
            for i in range(n):
                e = frozenset((cyc[i], cyc[(i + 1) % n]))
                if e not in T1:
                    pts = warm[i] * SS
                    for k in range(len(pts) - 1):
                        dr.line([tuple(pts[k]), tuple(pts[k + 1])], fill=(255, 214, 206), width=int(lw * 2.6 * SS))
        ribbon(cool, COOL, False)
        ribbon(warm, WARM, True)
        for k in range(n): pearls.append((V[k][0], V[k][1], cell * 0.030, 'w'))
        pearls.append((vpos[0], vpos[1], cell * 0.040, 'v'))
        if idx == 0: frames.append((ox, oy - cell / 2))
        changed = sum(1 for i in range(n) if frozenset((cyc[i], cyc[(i + 1) % n])) not in T1)
        D['D'][idx].append(changed)
    im = im.resize((W, H), Image.LANCZOS)
    arr = np.asarray(im).astype(np.float32) / 255
    # pearls (numpy glossy beads)
    for cx, cy, r, kind in pearls:
        x0, x1 = int(cx - r * 2), int(cx + r * 2) + 1; y0, y1 = int(cy - r * 2), int(cy + r * 2) + 1
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        sh = np.exp(-(((xx - cx - 0.25 * r) ** 2 + (yy - cy - 0.35 * r) ** 2) / (1.2 * r) ** 2) ** 2)
        sub = arr[y0:y1, x0:x1] * (1 - 0.25 * sh)[..., None]
        dx, dy = (xx - cx) / r, (yy - cy) / r; q = dx * dx + dy * dy
        inside = np.clip((1 - np.sqrt(q)) * r, 0, 1)[..., None]
        nz = np.sqrt(np.clip(1 - q, 0, 1))
        L = np.array([-0.45, -0.55, 0.70]); L /= np.linalg.norm(L)
        lam = np.clip(dx * L[0] + dy * L[1] + nz * L[2], 0, 1)
        Hh = (L + [0, 0, 1]) / np.linalg.norm(L + [0, 0, 1])
        sp = np.clip(dx * Hh[0] + dy * Hh[1] + nz * Hh[2], 0, 1) ** 60
        base = np.array([0.96, 0.93, 0.97]) if kind == 'w' else np.array([1.0, 0.50, 0.44])
        col = base * (0.62 + 0.42 * lam[..., None]) + 0.6 * sp[..., None]
        arr[y0:y1, x0:x1] = sub * (1 - inside) + np.clip(col, 0, 1) * inside
    im = Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8))
    d = ImageDraw.Draw(im)
    from caption import caption, font
    fs = int(cell * 0.040)
    for idx, (cyc, path, changed) in enumerate(D['D']):
        r_, c_ = divmod(idx, cols)
        ox = left + c_ * (cell + gap) + cell / 2; oy = top + r_ * (cell + gap)
        lab = 'the deal' if idx == 0 else f'twin {idx}  ·  {changed} threads change hands'
        f = font('i' if idx == 0 else 'm', fs if idx == 0 else int(fs * 0.8))
        w = d.textlength(lab, font=f)
        d.text((ox - w / 2, oy + cell * 0.955), lab, font=f, fill=(232, 96, 92) if idx == 0 else (130, 115, 140))
    for ox, oy in frames:
        b = cell * 0.49
        d.rounded_rectangle([ox - b, oy - cell * 0.02, ox + b, oy + cell * 1.03], radius=int(cell * 0.06), outline=(240, 140, 130), width=3)
    yb = top + 4 * cell + 3 * gap + int(H * 0.035)
    caption(im, W - left, yb, P('title', 'Every Deal Has a Twin'),
            [('eleven pearls, a warm necklace and a cool thread closing through the coral pearl — the same threads, dealt all sixteen ways', 'i', 0.56),
             ('MathOverflow 515726: the dealt pair can never both be the unique cheapest, since every twin costs the same in total', 'r', 0.46),
             ('Thomason (1978): Hamiltonian decompositions of a 4-regular graph come in pairs, so every deal has a twin (checked: all 191,370 deals at n = 10)', 'r', 0.46)],
            int(W * 0.03), align='right')
    im.save(out)


if __name__ == '__main__':
    main()
