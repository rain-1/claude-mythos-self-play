# pipescene.py — the good permutation of 31 (MO 514690) as a raft of glass pipes lying on paper, rod k of length
# proportional to a_k, over a printed triangle of all its consecutive blocks: cell [i..j] sits above the pipes i..j,
# coloured by the fractional part of the block's average.  No cell is ever an integer, except the apex (the whole).
import numpy as np, struct, json, colorsys
from PIL import Image, ImageDraw, ImageFilter

def build(perm, pitch=1.0, rr=0.42, unit=0.62, h=None, sat=0.55, absk=0.4, out='scene_pipes.bin', texfn='tex.f32', Y0=300.0,
          texs=0.01, hue_of=None):
    n = len(perm); h = h or pitch * 0.5
    xs = (np.arange(n) - (n - 1) / 2) * pitch
    cap = []
    for k, a in enumerate(perm):
        L = a * unit; hue = 0.97 - 0.55 * (a - 1) / (n - 1)
        t = np.array(colorsys.hsv_to_rgb(hue % 1, sat, 1.0)); col = -np.log(np.clip(t, 1e-3, 1)) * absk
        y1 = -0.6; y0 = y1 - L
        cap.append([xs[k], y0 + rr, rr, xs[k], y1 - rr, rr, rr, 0, *col, 0])
    # printed triangle: cell [i..j] centred at x=(xs_i+xs_j)/2, y=(j-i)*h ; drawn as a diamond of half-width pitch/2, half-height h
    x0, x1 = xs[0] - 2, xs[-1] + 2; ytop = (n - 1) * h + 2; ybot = -0.3
    TW = int((x1 - x0) / texs); TH = int((ytop - ybot) / texs)
    img = Image.new('RGB', (TW, TH), (255, 255, 255)); dr = ImageDraw.Draw(img)
    S = np.concatenate([[0], np.cumsum(perm)])
    def px(x, y): return ((x - x0) / texs, (y - ybot) / texs)   # row = u increasing with y
    cells = []
    for ln in range(2, n + 1):
        for i in range(0, n - ln + 1):
            j = i + ln - 1; s = S[j + 1] - S[i]; f = (s % ln) / ln
            cx = (xs[i] + xs[j]) / 2; cy = (ln - 1) * h
            if f == 0: rgb = (247, 135, 120)
            else:
                hh = (0.97 - 0.85 * f) if hue_of is None else hue_of(f)
                rgb = tuple(int(255 * c) for c in colorsys.hsv_to_rgb(hh % 1, 0.30, 1.0))
            g = 0.47
            pts = [px(cx - pitch * g, cy), px(cx, cy - h * 2 * g), px(cx + pitch * g, cy), px(cx, cy + h * 2 * g)]
            dr.polygon(pts, fill=rgb)
            cells.append((i, j, f))
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    a = np.asarray(img, dtype=np.float32) / 255.0
    # u = y - Y0 on the floor; tex rows indexed by u
    with open(texfn, 'wb') as fh:
        fh.write(struct.pack('ii', TW, TH)); fh.write(struct.pack('ddd', x0, ybot - Y0, texs)); fh.write(a.astype(np.float32).tobytes())
    with open(out, 'wb') as fh:
        fh.write(struct.pack('ii', 0, len(cap))); fh.write(np.array(cap, dtype=np.float64).tobytes())
    return cells, (x0, x1, ybot, ytop)

if __name__ == '__main__':
    perm = json.load(open('math_perm/good31.json'))['canonical']
    cells, ext = build(perm)
    print(len(cells), sum(1 for c in cells if c[2] == 0), ext)

def build_beads(perm, ox=0.0, oy=0.0, pitch=1.0, rr=0.4, unit=0.42, br=0.45, sat=0.5, absk=0.35, bsat=0.55, babsk=0.5, out='scene_pipes2.bin',
                coral=(0.05, 0.55, 0.65)):
    n = len(perm); hn = n; xs = (np.arange(n) - (n - 1) / 2) * pitch; hrow = pitch * np.sqrt(3) / 2
    sph, cap = [], []
    for k, a in enumerate(perm):
        L = a * unit; hue = 0.97 - 0.55 * (a - 1) / (n - 1)
        t = np.array(colorsys.hsv_to_rgb(hue % 1, sat, 1.0)); col = -np.log(np.clip(t, 1e-3, 1)) * absk
        y1 = -0.75; y0 = y1 - L
        cap.append([xs[k], y0 + rr, rr, xs[k], y1 - rr, rr, rr, 0, *col, 0])
    S = np.concatenate([[0], np.cumsum(perm)]); cells = []
    for ln in range(1, n + 1):
        for i in range(0, n - ln + 1):
            j = i + ln - 1; s = S[j + 1] - S[i]; f = (s % ln) / ln
            cx = (xs[i] + xs[j]) / 2; cy = (ln - 1) * hrow
            if ln == 1: continue
            if f == 0: col = np.array(coral) * babsk * 2
            else:
                t = np.array(colorsys.hsv_to_rgb(0.45 + 0.47 * f ** 0.6, bsat, 1.0)); col = -np.log(np.clip(t, 1e-3, 1)) * babsk
            sph.append([cx, cy, br, br, 0, *col, 0]); cells.append((i, j, f))
    for q in sph: q[0] += ox; q[1] += oy
    for q in cap: q[0] += ox; q[3] += ox; q[1] += oy; q[4] += oy
    if out: write(out, sph, cap)
    return sph, cap, cells

def write(out, sph, cap):
    with open(out, 'wb') as fh:
        fh.write(struct.pack('ii', len(sph), len(cap))); fh.write(np.array(sph, dtype=np.float64).tobytes()); fh.write(np.array(cap, dtype=np.float64).tobytes())

def family(out='scene_family.bin', unit=0.3, **kw):
    p31 = json.load(open('math_perm/good31.json'))['canonical']; p7 = [1, 6, 7, 4, 5, 2, 3]; p3 = [1, 2, 3]
    S, C = [], []
    for perm, ox, oy in ((p31, 5.0, 0.0), (p7, -16.0, 0.0), (p3, -23.0, 0.0)):
        s_, c_, _ = build_beads(perm, ox, oy, unit=unit, out=None, **kw); S += s_; C += c_
    write(out, S, C)

def canon(p):
    a = [1]
    for k in range(p - 1, 1, -2): a += [k, k + 1]
    return a

def isgood(a):
    n = len(a); S = np.concatenate([[0], np.cumsum(a)])
    return all((S[j] - S[i]) % (j - i) for i in range(n) for j in range(i + 2, n + 1) if not (i == 0 and j == n))

def family2(out='scene_family2.bin', unit=0.3, place=None, **kw):
    S, C = [], []
    for p, ox, oy in place:
        a = canon(p); assert isgood(a), p
        s_, c_, _ = build_beads(a, ox, oy, unit=unit, out=None, **kw); S += s_; C += c_
    write(out, S, C)
    return len(S), len(C)

def ring(cx, cy, R, br=0.22, col=(0.05, 0.55, 0.65), k=0.9):
    m = max(12, int(2 * np.pi * R / (br * 3.2)))
    return [[cx + R * np.cos(2 * np.pi * i / m), cy + R * np.sin(2 * np.pi * i / m), br, br, 0, *(np.array(col) * k), 0] for i in range(m)]

def family3(out='scene_family3.bin', unit=0.3, place=None, rings=(), **kw):
    S, C = [], []
    for p, ox, oy in place:
        a = canon(p); assert isgood(a), p
        s_, c_, _ = build_beads(a, ox, oy, unit=unit, out=None, **kw); S += s_; C += c_
    for cx, cy, R in rings: S += ring(cx, cy, R)
    write(out, S, C)
    return len(S), len(C)
