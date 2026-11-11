# Build a pond scene from a hypercube decomposition and render it.
import numpy as np, json, sys, math
from PIL import Image, ImageDraw, ImageFont
import koi
from koi import hexc, SCHOOLS

def warp(pos, p=0.62):
    r = np.linalg.norm(pos, axis=1); R0 = r.max()
    return pos * ((r / R0) ** (p - 1))[:, None]

def petrie(d):
    """d-cube in its Petrie polygon projection, edge length 1"""
    e = np.array([[math.cos(k * math.pi / d), math.sin(k * math.pi / d)] for k in range(d)])
    pos = np.zeros((1 << d, 2))
    for v in range(1 << d):
        for k in range(d):
            pos[v] += (0.5 if (v >> k) & 1 else -0.5) * e[k]
    return pos

def build(pos, cycles, schools, seed=3, delta=0.045, fish_per_edge=2.0, flen=0.215, fw=0.030, pad_r=0.088,
          R=1.78, center=(0.5, 0.452), ppu=1 / 4.25, sym=1, rin=0.2, ripples=6, flower=None, trail_w=0.036, padrot=None, petals=46, petal_r0=0.86, fish_density=None):
    rng = np.random.default_rng(seed)
    n = len(pos); d = int(round(math.log2(n))) if flower is None else 0
    pads = []
    greens = [('#bfe9a6', '#e3f6c4'), ('#a9e2b4', '#d6f3cf'), ('#c9ec9d', '#ecf8c6'), ('#9fdcbc', '#d0f1dc')]
    for v in range(n):
        fl = (bin(v).count('1') % 2 == 0) if flower is None else flower[v]
        g = greens[rng.integers(len(greens))]
        rot = math.atan2(pos[v, 1], pos[v, 0]) + rng.normal(0, 0.5) if padrot is None else padrot[v]
        pet = [hexc('#ffc4dc'), hexc('#ff9fc6'), hexc('#ff7fb2')]
        pads.append(dict(x=float(pos[v, 0]), y=float(pos[v, 1]), r=pad_r * (1.0 + 0.06 * rng.normal()), rot=rot,
                         col=hexc(g[0]), col2=hexc(g[1]), flower=1 if fl else 0, seed=int(rng.integers(1, 1000)), pet=pet))
    loops = []; fish = []
    for ci, cyc in enumerate(cycles):
        sc = SCHOOLS[schools[ci]]
        dense = koi.loop_path(pos, list(cyc), delta=delta, rin=rin)
        path, L = koi.resample(dense, 0.004)
        loops.append(dict(path=path.astype(np.float32), trail=sc['trail']))
        nf = int(round(len(cyc) * fish_per_edge)) if fish_density is None else max(2, int(round(L * fish_density)))
        ph0 = rng.random()
        for k in range(nf):
            jit = rng.normal(0, 0.012 * sym)
            s = (k + ph0 * 0 + 0.37 + jit) / nf * L
            fl_ = flen * (1 + 0.10 * rng.normal()); fw_ = fw * (fl_ / flen) * (1 + 0.06 * rng.normal())
            sp = koi.make_fish(path, L, s, fl_, fw_, rng.random(), rng)
            # fins: pectorals + small ventrals; frame from the spine
            K = len(sp); fins = []
            for (tf, a, b, ang) in ((0.25, 0.034, 0.015, 0.95), (0.54, 0.018, 0.008, 0.7)):
                i = int(tf * (K - 1)); T = sp[i + 1] - sp[i]; T = T / np.linalg.norm(T)   # tailward
                N = np.array([-T[1], T[0]])
                w = koi.body_w(tf) * fw_
                for sgn in (1, -1):
                    flap = ang + 0.25 * rng.normal()
                    dirv = math.cos(flap) * T + sgn * math.sin(flap) * N
                    c = sp[i] + sgn * N * w * 0.55 + dirv * a * fl_ / flen * 0.8
                    fins.append([c[0], c[1], dirv[0], dirv[1], a * fl_ / flen, b * fl_ / flen])
            style = rng.random()
            base, patch, patch2 = sc['base'], sc['patch'], sc['patch2']
            thr = 0.40 + 0.22 * rng.random()
            if style < 0.22: thr = 0.12          # nearly solid colour
            if sc['name'] == 'pearl': thr = 0.52 + 0.14 * rng.random()
            fish.append(dict(sp=sp, fins=np.array(fins, np.float32), fw=float(fw_), flen=float(fl_), base=base, patch=patch,
                             patch2=patch2, fin=sc['fin'], pearl=sc['name']=='pearl', seed=int(rng.integers(1, 100000)), thr=float(thr), depth=float(rng.random())))
    rip = []
    for k in range(ripples):
        a = rng.random() * 2 * np.pi; r = R * (0.25 + 0.65 * rng.random())
        rip.append((r * math.cos(a), r * math.sin(a), 0.10 + 0.10 * rng.random(), 3 + rng.integers(3), 0.035))
    pets = []
    pc = [hexc('#ff9fc6'), hexc('#ffc4dc'), hexc('#ffd9a0'), hexc('#ffffff'), hexc('#ff8fb8')]
    k = 0
    while len(pets) < petals and k < 10000:
        k += 1
        a = rng.random() * 2 * np.pi; r = R * (petal_r0 + (0.95 - petal_r0) * rng.random() ** 0.6)
        x, y = r * math.cos(a), r * math.sin(a)
        if min(np.hypot(pos[:, 0] - x, pos[:, 1] - y)) < pad_r * 1.5: continue
        sz = 0.016 * (0.7 + 0.6 * rng.random())
        pets.append((x, y, sz, sz * 0.55, rng.random() * 6.28, pc[rng.integers(len(pc))]))
    return dict(center=center, ppu=ppu, R=R, pads=pads, loops=loops, fish=fish, ripples=rip, trail_w=trail_w, petals=pets)

def font(name, size):
    return ImageFont.truetype('/usr/share/fonts/truetype/freefont/' + name + '.ttf', size)

def caption(im, lines, y0, ink=(92, 77, 102)):
    """lines: list of (text, fontname, size_frac, gap_frac, colour or None)"""
    W, H = im.size; dr = ImageDraw.Draw(im); y = y0 * H
    for text, fn, sz, gap, col in lines:
        f = font(fn, int(sz * W)); w = dr.textlength(text, font=f)
        dr.text(((W - w) / 2, y), text, font=f, fill=col or ink)
        y += (sz + gap) * W
    return im
