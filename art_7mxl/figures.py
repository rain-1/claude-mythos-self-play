"""Didactic figure set for proofs.md — four explanatory panels.

fig1_identity.png   Lemma 1: the three-term Fibonacci identity, punch-card view
fig2_kernel.png     Lemma 2: col_a = col_{a+q_t} + col_{a+q_{t+1}} in M_16
fig3_window.png     Theorem 1: the golden window across blocks + census sparks
fig4_lonevoice.png  Theorem 2: forcing, trichotomy, parity kill at u_9 = 64

Style: dark, crisp, labeled; supersample 2x then LANCZOS.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pickle

SS = 2
BG = (11, 13, 18)
GOLD = (240, 195, 100)
ICE = (110, 185, 240)
RED = (225, 95, 110)
VIOLET = (180, 140, 230)
SLATE = (135, 142, 158)
WHITE = (232, 233, 236)
DIM = (70, 74, 86)
GREEN = (140, 210, 150)

FDIR = "/usr/share/fonts/truetype/dejavu/"


def fonts(scale=1.0):
    f = {}
    f['title'] = ImageFont.truetype(FDIR + "DejaVuSerif-Bold.ttf", int(44 * SS * scale))
    f['sub'] = ImageFont.truetype(FDIR + "DejaVuSans.ttf", int(27 * SS * scale))
    f['lab'] = ImageFont.truetype(FDIR + "DejaVuSans.ttf", int(24 * SS * scale))
    f['small'] = ImageFont.truetype(FDIR + "DejaVuSans.ttf", int(20 * SS * scale))
    f['math'] = ImageFont.truetype(FDIR + "DejaVuSans.ttf", int(30 * SS * scale))
    f['mathb'] = ImageFont.truetype(FDIR + "DejaVuSans-Bold.ttf", int(30 * SS * scale))
    return f


def canvas(w, h):
    img = Image.new("RGB", (w * SS, h * SS), BG)
    return img, ImageDraw.Draw(img), fonts()


def save(img, name, w, h):
    img = img.resize((w, h), Image.LANCZOS)
    img.save(name)
    print("saved", name)


FIB = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597,
       2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025]
FSET = set(FIB)


def q(t):
    return FIB[t - 1] if t >= 1 else 1


# ---------------------------------------------------------------- figure 1
def fig1():
    W, H = 1920, 1080
    img, dr, f = canvas(W, H)
    t = 6                      # q_t = 13, q_{t+1} = 21, window (5, 42)
    qt, qt1 = q(t), q(t + 1)
    lo, hi = q(t - 2), 2 * qt1     # open window (5, 42)
    s0, s1 = 2, 46                 # drawn range
    X0, X1 = 130 * SS, (W - 90) * SS

    def X(s):
        return X0 + (s - s0) / (s1 - s0) * (X1 - X0)

    dr.text((60 * SS, 40 * SS), "Lemma 1 — the three-term Fibonacci identity", font=f['title'], fill=WHITE)
    dr.text((60 * SS, 105 * SS),
            f"1[s∈Q]  =  1[s+{qt}∈Q] + 1[s+{qt1}∈Q]      on the window  {lo} < s < {hi}      (here t={t}: q₆=13, q₇=21)",
            font=f['math'], fill=SLATE)

    rows = [
        (f"s ∈ Q ?", [s for s in range(s0, s1 + 1) if s in FSET], GOLD, 300),
        (f"s + {qt} ∈ Q ?", [s for s in range(s0, s1 + 1) if s + qt in FSET], ICE, 470),
        (f"s + {qt1} ∈ Q ?", [s for s in range(s0, s1 + 1) if s + qt1 in FSET], VIOLET, 640),
    ]
    # window shading
    dr.rectangle([X(lo + 0.5) - 6 * SS, 250 * SS, X(hi - 0.5) + 6 * SS, 730 * SS],
                 fill=(20, 24, 34))
    # vertical guides at the four in-window hits
    for s in [q(t - 1), qt, qt1, q(t + 2)]:
        dr.line([X(s), 260 * SS, X(s), 720 * SS], fill=(48, 52, 66), width=2 * SS)

    for label, hits, col, y in rows:
        y *= SS
        dr.line([X(s0), y, X(s1), y], fill=DIM, width=2 * SS)
        dr.text((62 * SS, y - 58 * SS), label, font=f['lab'], fill=col)
        for s in range(s0, s1 + 1):
            x = X(s)
            inwin = lo < s < hi
            if s in hits:
                r = 11 * SS if inwin else 8 * SS
                c = col if inwin else (90, 80, 84)
                dr.ellipse([x - r, y - r, x + r, y + r], fill=c)
            else:
                r = 2.6 * SS
                dr.ellipse([x - r, y - r, x + r, y + r], fill=(58, 62, 74))
        # numbers under first row only
    for s in range(s0, s1 + 1, 1):
        if s % 2 == 0 or s in FSET or s in (lo, hi):
            dr.text((X(s) - 10 * SS, 745 * SS), str(s), font=f['small'], fill=(105, 110, 122))

    # annotate hits
    for s, name in [(q(t - 1), "q₅=8"), (qt, "q₆=13"), (qt1, "q₇=21"), (q(t + 2), "q₈=34")]:
        dr.text((X(s) - 26 * SS, 262 * SS), name, font=f['small'], fill=SLATE)

    # failure marks at the boundary
    for s, msg in [(lo, "s=5: LHS=1, RHS=0 ✗"), (hi, "s=42: LHS=0, RHS=1 ✗")]:
        dr.text((X(s) - 60 * SS, 800 * SS), msg, font=f['small'], fill=RED)
        dr.line([X(s), 260 * SS, X(s), 795 * SS], fill=(120, 60, 66), width=2 * SS)

    dr.text((60 * SS, 860 * SS),
            "Inside the window the only Fibonacci numbers are {8, 13, 21, 34}. The middle row lights exactly at s ∈ {8, 21},",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, 900 * SS),
            "the bottom row exactly at s ∈ {13, 34} — two disjoint sets whose union is the top row. Row 1 = Row 2 + Row 3.",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, 955 * SS),
            "Outside the window it breaks immediately (red) — this is why the dead zone has sharp golden edges.",
            font=f['sub'], fill=(150, 120, 124))
    save(img, "fig1_identity.png", W, H)


# ---------------------------------------------------------------- figure 2
def fig2():
    W, H = 1920, 1250
    img, dr, f = canvas(W, H)
    n = 16
    a, t = 3, 5                     # a=3, q_5=8, q_6=13 -> cols 3, 11, 16
    c1, c2, c3 = a, a + q(t), a + q(t + 1)

    dr.text((60 * SS, 38 * SS), "Lemma 2 — a kernel vector: one column is the sum of two others", font=f['title'], fill=WHITE)
    dr.text((60 * SS, 100 * SS),
            f"M₁₆ (cell lit ⇔ i+j Fibonacci)   ·   column {c1}  =  column {c2} + column {c3}    (offsets q₅ = 8 and q₆ = 13)",
            font=f['math'], fill=SLATE)
    dr.text((60 * SS, 144 * SS),
            f"⇒   x = −e{chr(0x2083)} + e₁₁ + e₁₆ ∈ ker M₁₆   ⇒   det M₁₆ = 0",
            font=f['math'], fill=SLATE)

    gx, gy = 150 * SS, 250 * SS
    cell = 46 * SS
    # column highlights
    for c, col in [(c1, (60, 34, 40)), (c2, (52, 46, 26)), (c3, (52, 46, 26))]:
        dr.rectangle([gx + (c - 1) * cell, gy, gx + c * cell, gy + n * cell], fill=col)
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            x, y = gx + (j - 1) * cell, gy + (i - 1) * cell
            if (i + j) in FSET:
                pad = 7 * SS
                col = GOLD if j in (c2, c3) else (RED if j == c1 else (150, 155, 170))
                dr.rectangle([x + pad, y + pad, x + cell - pad, y + cell - pad], fill=col)
    for k in range(n + 1):
        dr.line([gx + k * cell, gy, gx + k * cell, gy + n * cell], fill=(40, 44, 56), width=1 * SS)
        dr.line([gx, gy + k * cell, gx + n * cell, gy + k * cell], fill=(40, 44, 56), width=1 * SS)
    # labels
    for j in range(1, n + 1):
        col = RED if j == c1 else (GOLD if j in (c2, c3) else (100, 105, 118))
        dr.text((gx + (j - 1) * cell + 14 * SS, gy - 34 * SS), f"{j}", font=f['small'], fill=col)
    for i in range(1, n + 1):
        dr.text((gx - 44 * SS, gy + (i - 1) * cell + 10 * SS), f"{i}", font=f['small'], fill=(100, 105, 118))
    # anti-diagonal band labels
    for qq in [2, 3, 5, 8, 13, 21]:
        # place label near the diagonal's exit on the right or bottom
        if qq - 1 <= n:
            x = gx + (qq - 1) * cell - 30 * SS
            y = gy - 66 * SS
            dr.text((x, y), f"i+j={qq}", font=f['small'], fill=(90, 96, 110))
    dr.text((gx + 6 * cell, gy + n * cell + 18 * SS),
            "each lit anti-diagonal is one Fibonacci number", font=f['small'], fill=(90, 96, 110))

    # extracted columns on the right
    ex = gx + n * cell + 130 * SS
    ey = gy
    dr.text((ex, ey - 60 * SS), "the three columns, extracted:", font=f['lab'], fill=SLATE)
    heads = [(f"col {c1}", RED, c1), ("col 11", GOLD, c2), ("col 16", GOLD, c3)]
    colw = 90 * SS
    for k, (hd, col, cc) in enumerate(heads):
        x = ex + k * colw + (30 * SS if k > 0 else 0)
        dr.text((x + 4 * SS, ey - 26 * SS), hd, font=f['small'], fill=col)
        for i in range(1, n + 1):
            y = ey + (i - 1) * cell
            v = 1 if (i + cc) in FSET else 0
            if v:
                dr.rectangle([x + 8 * SS, y + 8 * SS, x + 54 * SS, y + cell - 8 * SS], fill=col)
            else:
                dr.rectangle([x + 8 * SS, y + 8 * SS, x + 54 * SS, y + cell - 8 * SS],
                             outline=(52, 56, 68), width=1 * SS)
        if k == 0:
            dr.text((x + 66 * SS, ey + n * cell // 2 - 20 * SS), "=", font=f['mathb'], fill=WHITE)
        if k == 1:
            dr.text((x + 66 * SS, ey + n * cell // 2 - 20 * SS), "+", font=f['mathb'], fill=WHITE)

    dr.text((60 * SS, gy + n * cell + 80 * SS),
            "Rows 2, 5, 10 light the red column (2+3, 5+3, 10+3 ∈ {5, 8, 13}); rows 2, 10 light column 11 (sums 13, 21) and row 5",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, gy + n * cell + 120 * SS),
            "lights column 16 (sum 21) — disjointly, by Lemma 1. Sliding the triple a → a+q_t → a+q_{t+1} across the block gives",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, gy + n * cell + 160 * SS),
            "singular Mₙ for every n in the head [q_K, q_K+q_{K−5}−1] (take t = K−2, a = q_{K−4}) and the tail",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, gy + n * cell + 200 * SS),
            "[q_K+q_{K−3}, q_{K+1}−1] (t = K−1, a = q_{K−3}) — that is Theorem 1.",
            font=f['sub'], fill=SLATE)
    save(img, "fig2_kernel.png", W, H)


# ---------------------------------------------------------------- figure 3
def fig3():
    W, H = 1920, 1400
    img, dr, f = canvas(W, H)
    d = pickle.load(open("dets28656.pkl", "rb"))
    PHI = (1 + 5 ** 0.5) / 2

    dr.text((60 * SS, 38 * SS), "Theorem 1 — the golden dead zone, across every Fibonacci block", font=f['title'], fill=WHITE)
    dr.text((60 * SS, 100 * SS),
            "each row = one block q_K ≤ n < q_{K+1}, drawn at relative position m/(q_{K+1}−q_K)",
            font=f['math'], fill=SLATE)
    dr.text((60 * SS, 142 * SS),
            "red = PROVEN det = 0   ·   sparks = census det ≠ 0 (gold +1, ice −1)",
            font=f['math'], fill=SLATE)

    X0, X1 = 210 * SS, (W - 80) * SS
    Y0 = 290 * SS
    rowh = 64 * SS
    Ks = list(range(8, 22))
    for r, K in enumerate(Ks):
        y = Y0 + r * rowh
        flo, fhi = q(K), q(K + 1)
        L = fhi - flo

        def X(m):
            return X0 + m / L * (X1 - X0)
        # proven dead zones
        dr.rectangle([X(0), y - 17 * SS, X(q(K - 5)) - 1, y + 17 * SS], fill=(58, 28, 34))
        dr.rectangle([X(q(K - 3)), y - 17 * SS, X1, y + 17 * SS], fill=(58, 28, 34))
        # window strip
        dr.rectangle([X(q(K - 5)), y - 17 * SS, X(q(K - 3)) - 1, y + 17 * SS], fill=(24, 30, 42))
        # sparks
        for n in range(flo, fhi):
            if n > 28656:
                break
            v = d.get(n, 0)
            if v == 0:
                continue
            x = X(n - flo)
            col = GOLD if v > 0 else ICE
            dr.line([x, y - 14 * SS, x, y + 14 * SS], fill=col, width=max(1, int(2.2 * SS)))
        # u_K marker
        # u sequence values within this block: u_K with q_K <= u_K < q_{K+1} -> m = u_{K-4}
        uvals = {}
        u = {0: 0, 1: 1, 2: 2, 3: 3, 4: 5}
        for k2 in range(5, len(FIB)):
            u[k2] = q(k2) + u[k2 - 4]
        if K in u and flo <= u[K] < fhi:
            x = X(u[K] - flo)
            dr.polygon([(x, y - 30 * SS), (x - 7 * SS, y - 44 * SS), (x + 7 * SS, y - 44 * SS)],
                       fill=WHITE)
        dr.text((70 * SS, y - 14 * SS), f"K={K}", font=f['small'], fill=(110, 116, 130))
        dr.text((X1 + 8 * SS, y - 14 * SS), f"{q(K)}", font=f['small'], fill=(80, 85, 98))
    # meridians
    ybot = Y0 + len(Ks) * rowh
    for rel, lab in [(1 / PHI ** 4, "1/φ⁴ ≈ 0.146"), (1 / PHI ** 2, "1/φ² ≈ 0.382")]:
        x = X0 + rel * (X1 - X0)
        dr.line([x, Y0 - 40 * SS, x, ybot], fill=(150, 140, 100), width=2 * SS)
        dr.text((x - 60 * SS, Y0 - 76 * SS), lab, font=f['small'], fill=(190, 175, 130))
    # bottom annotations
    yb = ybot + 30 * SS
    dr.text((60 * SS, yb),
            "The window's exact edges: first possible det ≠ 0 at m = q_{K−5} (Zeckendorf 100001 0…0), last at m = q_{K−3}−1",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, yb + 40 * SS),
            "(= q_{K−4}+q_{K−6}+⋯, Zeckendorf 1000 10 10 …). Everything red is killed by the sliding kernel triple of Lemma 2;",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, yb + 80 * SS),
            "as K → ∞ the live window converges to [1/φ⁴, 1/φ²]: 76.4% of every block is provably silent. White triangles: the",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, yb + 120 * SS),
            "lone-voice positions u_K of Theorem 2 — always inside the window (Corollary 2).",
            font=f['sub'], fill=SLATE)
    save(img, "fig3_window.png", W, H)


# ---------------------------------------------------------------- figure 4
def fig4():
    W, H = 1920, 1850
    img, dr, f = canvas(W, H)
    # K = 9: n = u_9 = 64; q_9=55, q_10=89; B=[1,24], band=[25,34], S=(34,55), top=[55,64]
    K = 9
    u = {0: 0, -1: 0, 1: 1, 2: 2, 3: 3, 4: 5}
    for k2 in range(5, 12):
        u[k2] = q(k2) + u[k2 - 4]
    n = u[K]

    dr.text((60 * SS, 36 * SS), "Theorem 2 — why u₉ = 64 has exactly one Fibonacci permutation", font=f['title'], fill=WHITE)
    dr.text((60 * SS, 100 * SS),
            "u_K = q_K + u_{K−4}  (Zeckendorf 1(0001)*):  1, 2, 3, 5, 9, 15, 24, 39, 64, 104, …   here n = 64, q₉ = 55, q₁₀ = 89",
            font=f['math'], fill=SLATE)

    X0, X1 = 90 * SS, (W - 90) * SS

    def X(i):
        return X0 + (i - 1) / (n - 1) * (X1 - X0)

    def arc(dr_, i, j, y0, col, wdt, up=True, dash=False):
        xa, xb = X(min(i, j)), X(max(i, j))
        r = (xb - xa) / 2
        h = min(r * 0.62, 105 * SS)
        bbox = [xa, y0 - h, xb, y0 + h]
        if dash:
            for k2 in range(0, 180, 9):
                dr_.arc(bbox, start=180 + k2, end=180 + min(k2 + 4, 180), fill=col, width=wdt)
        else:
            dr_.arc(bbox, start=180, end=360, fill=col, width=wdt)

    def zone_bar(y0, zones):
        for (a, b, col, lab) in zones:
            dr.rectangle([X(a) - 6 * SS, y0 - 13 * SS, X(b) + 6 * SS, y0 + 13 * SS], fill=col)
            if lab:
                dr.text(((X(a) + X(b)) / 2 - len(lab) * 5.6 * SS, y0 + 20 * SS), lab,
                        font=f['small'], fill=SLATE)

    # ---- Panel A: forcing
    yA = 400 * SS
    dr.text((60 * SS, yA - 200 * SS), "A.  Lemma 4 (forcing) + Lemma 5 (the only three kinds of pairs)", font=f['sub'], fill=WHITE)
    zone_bar(yA, [
        (1, u[K - 2], (30, 38, 56), "B = [1, 24]"),
        (u[K - 2] + 1, q(K - 1), (56, 46, 24), "[25, 34] forced band"),
        (q(K - 1) + 1, q(K) - 1, (44, 32, 58), "strip S = (34, 55)"),
        (q(K), n, (56, 46, 24), "[55, 64] top"),
    ])
    # forced arcs: i in [55,64] -> 89 - i in [25,34]
    for i in range(q(K), n + 1):
        arc(dr, i, q(K + 1) - i, yA - 14 * SS, GOLD, 2 * SS)
    # strip internal rho arcs (dashed violet), sample a few
    for i in range(q(K - 1) + 1, (q(K + 1)) // 2 + 1):
        j = q(K + 1) - i
        if j <= q(K) - 1 and j > i:
            arc(dr, i, j, yA - 14 * SS, (120, 95, 160), 2 * SS, dash=True)
    # crossing arcs sample (grey dashed): i in S -> 55 - i in B
    for i in [37, 44, 51]:
        arc(dr, i, q(K) - i, yA - 14 * SS, (95, 100, 112), 2 * SS, dash=True)
    for i in range(1, n + 1, 1):
        xx = X(i)
        dr.ellipse([xx - 2.4 * SS, yA - 2.4 * SS, xx + 2.4 * SS, yA + 2.4 * SS], fill=(150, 155, 168))
    for i in [1, 9, 24, 34, 55, 64]:
        dr.text((X(i) - 10 * SS, yA + 46 * SS), str(i), font=f['small'], fill=(120, 126, 140))
    dr.text((60 * SS, yA + 90 * SS),
            "No pair can sum to q₁₁ = 144 (2·64 < 144). So rows 55…64 have exactly one move: reflect across q₁₀ = 89 (gold),",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, yA + 130 * SS),
            "landing exactly on [25, 34] because 89 − 64 = 25 = u₇ + 1. What survives: B and S. Inside S only sums of 89 exist",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, yA + 170 * SS),
            "(violet, the involution ρ); S ↔ B pairs must sum to 55 (grey); B-internal sums stay below 55 (B is standalone M₂₄).",
            font=f['sub'], fill=SLATE)

    # ---- Panel B: parity kill
    yB = 1000 * SS
    dr.text((60 * SS, yB - 250 * SS), "B.  The crossing is killed by parity", font=f['sub'], fill=WHITE)
    # draw B = [1,24] enlarged with pi*_7 arcs; plus red pair summing to 21

    def XB(i):
        return X0 + (i - 1) / (24 - 1) * (X1 - X0)
    for i in range(1, 25):
        xx = XB(i)
        dr.ellipse([xx - 3 * SS, yB - 3 * SS, xx + 3 * SS, yB + 3 * SS], fill=(160, 165, 178))
        if i in (1, 3, 9, 24):
            dr.text((xx - 8 * SS, yB + 24 * SS), str(i), font=f['small'], fill=(120, 126, 140))
    segs = [(10, 24, 34, GOLD), (4, 9, 13, ICE), (2, 3, 5, VIOLET), (1, 1, 2, GREEN)]
    for lo_, hi_, ssum, col in segs:
        for i in range(lo_, hi_ + 1):
            j = ssum - i
            if j >= i:
                if i == j:
                    dr.line([XB(i), yB - 40 * SS, XB(i), yB - 6 * SS], fill=col, width=2 * SS)
                else:
                    xa, xb = XB(i), XB(j)
                    r = abs(xb - xa) / 2
                    h = min(r * 0.55, 120 * SS)
                    dr.arc([min(xa, xb), yB - h, max(xa, xb), yB + h], 180, 360, fill=col, width=2 * SS)
    # red hypothetical pair r + c = 21, e.g. r=6, c=15
    r_, c_ = 6, 15
    xa, xb = XB(r_), XB(c_)
    hh = min((xb - xa) / 2 * 0.55, 160 * SS)
    for k2 in range(0, 180, 12):
        dr.arc([xa, yB - hh, xb, yB + hh], 180 + k2, 180 + min(k2 + 6, 180), fill=RED, width=4 * SS)
    dr.text(((xa + xb) / 2 - 60 * SS, yB - hh - 46 * SS), "6 + 15 = 21 = q₇ ✗", font=f['lab'], fill=RED)
    dr.text((60 * SS, yB + 70 * SS),
            "If a strip row escaped into B (a grey crossing), B would lose a row r and a column 34−… — precisely a pair with",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, yB + 110 * SS),
            "r + c = q₇ = 21. Re-adding that pair completes a full Fibonacci permutation of [1, 24]. But by induction [1, 24] has",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, yB + 150 * SS),
            "exactly ONE such permutation, and its pair-sums are 34 = q₈, 13 = q₆, 5 = q₄, 2 = q₂ — all EVEN-indexed Fibonacci",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, yB + 190 * SS),
            "numbers. A sum of 21 = q₇ (odd index) can never occur. Contradiction ⇒ no crossings ⇒ S reflects by ρ, B recurses.",
            font=f['sub'], fill=SLATE)

    # ---- Panel C: the full unique permutation
    yC = 1500 * SS
    dr.text((60 * SS, yC - 230 * SS), "C.  The unique permutation π*₉ — nested reflections, one per shell", font=f['sub'], fill=WHITE)
    shells = [(u[7] + 1, u[9], q(10), GOLD),   # (24,64] across 89
              (u[5] + 1, u[7], q(8), ICE),     # (9,24] across 34
              (u[3] + 1, u[5], q(6), VIOLET),  # (3,9] across 13
              (u[1] + 1, u[3], q(4), (240, 150, 150)),  # (1,3] across 5
              (1, 1, q(2), GREEN)]
    for i in range(1, n + 1):
        xx = X(i)
        dr.ellipse([xx - 2.4 * SS, yC - 2.4 * SS, xx + 2.4 * SS, yC + 2.4 * SS], fill=(160, 165, 178))
    for lo_, hi_, ssum, col in shells:
        for i in range(lo_, hi_ + 1):
            j = ssum - i
            if j >= i and lo_ <= j <= hi_:
                if i == j:
                    dr.line([X(i), yC - 30 * SS, X(i), yC - 4 * SS], fill=col, width=2 * SS)
                else:
                    xa, xb = X(i), X(j)
                    r = (xb - xa) / 2
                    h = min(r * 0.62, 150 * SS)
                    dr.arc([xa, yC - h, xb, yC + h], 180, 360, fill=col, width=2 * SS)
    for i, lab in [(1, "1"), (3, "3"), (9, "9"), (24, "24"), (64, "64")]:
        dr.text((X(i) - 8 * SS, yC + 24 * SS), lab, font=f['small'], fill=(120, 126, 140))
    lg = [("(24,64] ↔ sum 89", GOLD), ("(9,24] ↔ sum 34", ICE), ("(3,9] ↔ sum 13", VIOLET),
          ("(1,3] ↔ sum 5", (240, 150, 150)), ("1↔1 sum 2", GREEN)]
    for k2, (lab, col) in enumerate(lg):
        x = 90 * SS + k2 * 340 * SS
        dr.line([x, yC + 90 * SS, x + 40 * SS, yC + 90 * SS], fill=col, width=4 * SS)
        dr.text((x + 52 * SS, yC + 76 * SS), lab, font=f['small'], fill=SLATE)
    dr.text((60 * SS, yC + 140 * SS),
            "Segment boundaries are the u-numbers themselves (u_j + u_{j−2} = q_{j+1} − 1), the sums use every OTHER Fibonacci",
            font=f['sub'], fill=SLATE)
    dr.text((60 * SS, yC + 180 * SS),
            "number — which is exactly what powers the parity argument one level up. per(M₆₄) = 1;  det M₆₄ = sign(π*₉) = −1.",
            font=f['sub'], fill=SLATE)
    save(img, "fig4_lonevoice.png", W, H)


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
    fig4()
