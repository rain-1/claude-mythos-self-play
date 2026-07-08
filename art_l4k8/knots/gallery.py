"""THE SPECIMEN DRAWER — twenty-five knots and the primes that color them.

Mazur's dictionary reads: knots are primes, links are ideals, Fox
p-colorings of a knot are analogous to unramified F_p-extensions -- and a
knot admits nontrivial p-colorings exactly when p divides its determinant
|Delta_K(-1)|. So every knot carries a little spectrum of primes, the way
every number carries its factorization.

Here: 25 braid closures (classics + specimens grown from random braid
words, deduplicated by invariants). Each is woven as a glossy wreath and
dyed by an actual Fox coloring modulo the SMALLEST prime of its spectrum
-- the colors change only where an arc dives under a crossing, obeying
under = 2*over - under (mod p) at every crossing (that consistency IS the
coloring; it is solved exactly, not painted by hand). Knots whose
determinant is 1 admit no coloring by any prime: they stay monochrome
gold -- arithmetically inert specimens.
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from braidknot import is_knot, fox_colorings, determinant, verify
from wreath import stamp_knot, label_palette, GOLD
from PIL import Image, ImageDraw, ImageFont

SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def word_str(word):
    """Compact braid word: sigma_i with subscript index, superscript power."""
    out = []
    runs = []
    for (i, s) in word:
        if runs and runs[-1][0] == (i, s):
            runs[-1][1] += 1
        else:
            runs.append([(i, s), 1])
    for (i, s), k in runs:
        e = s * k
        sym = "σ" + str(i + 1).translate(SUB)
        if e != 1:
            sym += str(e).translate(SUP)
        out.append(sym)
    return "".join(out)


def prime_factors(m):
    out = []
    d = 2
    while d * d <= m:
        if m % d == 0:
            out.append(d)
            while m % d == 0:
                m //= d
        d += 1
    if m > 1:
        out.append(m)
    return out


def spectrum(n, word, det):
    """(p, kernel_dim) for every prime dividing det. Asserts the classical
    theorem: p-colorable <=> p | det(K)."""
    out = []
    for p in prime_factors(det):
        d, _ = fox_colorings(n, word, p)
        assert d > 1, f"p={p} divides det={det} but no coloring!?"
        out.append((p, d))
    for p in (3, 5, 7):
        if det % p:
            d, _ = fox_colorings(n, word, p)
            assert d == 1, f"p={p} colors the knot but det={det} is coprime!?"
    return out


def best_coloring(n, word, p):
    """Kernel vector mod p with the most distinct labels."""
    d, basis = fox_colorings(n, word, p)
    if d <= 1:
        return None
    basis = [b % p for b in basis]
    best, bestscore = None, -1
    # enumerate small combos of basis vectors
    if p ** d <= 4000:
        from itertools import product
        for coeffs in product(range(p), repeat=d):
            v = np.zeros(n, dtype=np.int64)
            for c, b in zip(coeffs, basis):
                v = (v + c * b) % p
            sc = len(set(v.tolist()))
            if sc > bestscore:
                best, bestscore = v, sc
    else:
        rng = np.random.default_rng(0)
        for _ in range(3000):
            coeffs = rng.integers(0, p, d)
            v = np.zeros(n, dtype=np.int64)
            for c, b in zip(coeffs, basis):
                v = (v + int(c) * b) % p
            sc = len(set(v.tolist()))
            if sc > bestscore:
                best, bestscore = v, sc
    return best


def factor_str(m):
    if m == 1:
        return "1"
    out = []
    x = m
    d = 2
    while d * d <= x:
        e = 0
        while x % d == 0:
            x //= d
            e += 1
        if e:
            out.append(f"{d}" + (f"^{e}" if e > 1 else ""))
        d += 1
    if x > 1:
        out.append(str(x))
    return "·".join(out)


def gather_specimens(seed=20260708, want=25):
    """Classics first, then deduplicated random braid knots."""
    classics = [
        ("3₁ trefoil", 2, [(0, 1)] * 3),
        ("4₁ figure-eight", 3, [(0, 1), (1, -1), (0, 1), (1, -1)]),
        ("5₁ cinquefoil", 2, [(0, 1)] * 5),
        ("7₁", 2, [(0, 1)] * 7),
        ("9₁", 2, [(0, 1)] * 9),
        ("8₁₉ = T(3,4)", 3, [(0, 1), (1, 1)] * 4),
        ("10₁₂₄ = T(3,5)", 3, [(0, 1), (1, 1)] * 5),
    ]
    specimens = []
    seen = set()
    for name, n, w in classics:
        if not is_knot(n, w):
            continue
        det = determinant(n, w)
        spec = tuple(spectrum(n, w, det))
        fp = (det, spec, n, len(w))
        seen.add((det, spec))
        specimens.append(dict(name=name, n=n, word=w, det=det, spec=spec))
    rng = np.random.default_rng(seed)
    tries = 0
    while len(specimens) < want and tries < 30000:
        tries += 1
        n = int(rng.integers(2, 6))
        L = int(rng.integers(max(4, n + 1), 13))
        word = []
        for _ in range(L):
            i = int(rng.integers(0, n - 1))
            s = int(rng.choice([-1, 1]))
            if word and word[-1] == (i, -s):
                s = -s          # avoid immediate cancellation
            word.append((i, s))
        if not is_knot(n, word):
            continue
        det = determinant(n, word)
        if det == 0:
            continue
        spec = tuple(spectrum(n, word, det))
        if (det, spec) in seen:
            continue
        # prefer knots that are actually knotted-looking: det>1 mostly,
        # but keep a couple of det-1 specimens for the 'inert' story
        n_det1 = sum(1 for s in specimens if s["det"] == 1)
        if det == 1 and n_det1 >= 1:
            continue
        seen.add((det, spec))
        specimens.append(dict(name=f"specimen {len(specimens)+1}",
                              n=n, word=word, det=det, spec=spec))
    # order: by det (unknotted-ish gold last), classics keep early positions
    return specimens[:want]


def render(out="specimen_drawer_4096.png", CELL=780, SSK=2, COLS=5,
           caption_h=104, header_h=190, margin=34):
    verify()
    specs = gather_specimens()
    print(f"{len(specs)} specimens")
    for s in specs:
        print(f"  {s['name']:<18} n={s['n']} len={len(s['word'])} det={s['det']} spec={s['spec']}")

    ROWS = (len(specs) + COLS - 1) // COLS
    W = COLS * CELL + (COLS + 1) * margin
    H = header_h + ROWS * (CELL + caption_h) + (ROWS + 1) * margin
    # paint knots at SSK, downscale later
    canvas = np.zeros((H * SSK, W * SSK, 3))
    canvas[:] = np.array([0.016, 0.015, 0.028])

    for k, s in enumerate(specs):
        r, c = divmod(k, COLS)
        cx = (margin + c * (CELL + margin) + CELL / 2) * SSK
        cy = (header_h + margin + r * (CELL + caption_h + margin) + CELL / 2) * SSK
        n = s["n"]
        Rout = CELL * 0.44 * SSK
        gap = Rout * 0.62 / max(n - 1 + 0.001, 1.4)
        Rin = Rout - (n - 1) * gap
        tube = min(gap * 0.44, Rin * 0.16, 26 * SSK)
        tube = max(tube, 10.0)
        if s["spec"]:
            p = s["spec"][0][0]
            vec = best_coloring(n, s["word"], p)
            pal = label_palette(p)
            stamp_knot(canvas, cx, cy, n, s["word"], p, vec.tolist(),
                       R=Rin, gap=gap, tube_w=tube, colors=pal,
                       phase=2 * np.pi * (k * 0.37 % 1))
        else:
            stamp_knot(canvas, cx, cy, n, s["word"], 0, None,
                       R=Rin, gap=gap, tube_w=tube, colors=None,
                       phase=2 * np.pi * (k * 0.37 % 1))
        print(f"  painted {s['name']}")

    img = (np.clip(canvas, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(img).resize((W, H), Image.LANCZOS)

    # ---- text
    draw = ImageDraw.Draw(im)
    fp = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    fpb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    f_title = ImageFont.truetype(fpb, 64)
    f_sub = ImageFont.truetype(fp, 30)
    f_cap = ImageFont.truetype(fpb, 26)
    f_cap2 = ImageFont.truetype(fp, 24)
    gold = (222, 190, 120)
    dim = (150, 150, 175)
    bright = (235, 228, 210)

    def fit(text, path, size, maxw):
        while size > 14:
            f = ImageFont.truetype(path, size)
            if draw.textlength(text, font=f) <= maxw:
                return f
            size -= 2
        return ImageFont.truetype(path, 14)

    draw.text((W // 2, 62), "THE SPECIMEN DRAWER", font=f_title,
              fill=bright, anchor="mm")
    sub = ("twenty-five braid closures, dyed by the smallest prime dividing "
           "their determinant  ·  arcs obey  under ≡ 2·over − under (mod p)")
    draw.text((W // 2, 132), sub, font=fit(sub, fp, 30, W - 120),
              fill=dim, anchor="mm")

    for k, s in enumerate(specs):
        r, c = divmod(k, COLS)
        x = margin + c * (CELL + margin) + CELL // 2
        y0 = header_h + margin + r * (CELL + caption_h + margin) + CELL
        primes = ", ".join(str(p) for p, _ in s["spec"]) if s["spec"] else "none — det 1"
        line1 = f"{s['name']}   ·   det = {s['det']}" + \
            (f" = {factor_str(s['det'])}" if s['det'] not in (1,) and factor_str(s['det']) != str(s['det']) else "")
        line2 = f"β = {word_str(s['word'])}   ·   p: {primes}"
        draw.text((x, y0 + 32), line1, font=fit(line1, fpb, 26, CELL - 8),
                  fill=gold, anchor="mm")
        draw.text((x, y0 + 70), line2, font=fit(line2, fp, 24, CELL - 8),
                  fill=dim, anchor="mm")

    im.save(out)
    print("saved", out, im.size)


if __name__ == "__main__":
    render()
