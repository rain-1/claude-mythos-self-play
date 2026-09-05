"""render_song.py — 'The Same Song' (2560², specimen sheet).
Pairs of binary strings whose 0/1 Jacobi matrices H_b are isospectral but not reverses of each other
(MO 514920). Each specimen: the two strings as bead necklaces (1 = ink coin, 0 = paper coin), and
above each its spectral portrait — a pastel coin at (bead j, eigenvalue λ_i) of radius ∝ |v_i(j)|,
pigment by the sign of the eigenvector entry. The eigenvalue rows coincide (the shared spine, ink
ticks between the two portraits); the coin patterns differ: the same song, other words.
Families are the Cayley–Hamilton ladders 0001(01)^k1011 ~ 0010(01)^k0111 (k = 0..5) and the five
primitive seeds ≤ 14.
"""
import numpy as np, json, sys, time
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import pastel as P

INK = P.PIG['ink']

FAMILY = [('0001' + '01' * k + '1011', '0010' + '01' * k + '0111') for k in range(6)]
SEEDS = [('000101011', '011001001'), ('001010111', '011011001'),
         ('0000101010011', '0110001001001'), ('0011010101111', '0110110111001'),
         ('01010110110001', '01110010010101')]
PAIRS = FAMILY + SEEDS   # 11 specimens


def H(b):
    n = len(b)
    M = np.diag([int(c) for c in b]).astype(float)
    M += np.diag(np.ones(n - 1), 1) + np.diag(np.ones(n - 1), -1)
    return M


def render(S=2560, SS=2, out='song_2560.png', seed=21):
    t0 = time.time()
    Wd, Hd = S * SS, S * SS
    sh = P.Sheet(Wd, Hd, seed=seed)
    cols, rows = 3, 4
    mx, my = 0.06 * Wd, 0.06 * Hd
    cw = (Wd - 2 * mx) / cols; ch = (0.86 * Hd - my) / rows
    cert = []
    fills = [Image.new('F', (Wd, Hd), 0.0) for _ in range(3)]
    dfs = [ImageDraw.Draw(im) for im in fills]
    ink = Image.new('F', (Wd, Hd), 0.0); dink = ImageDraw.Draw(ink)
    coral = Image.new('F', (Wd, Hd), 0.0); dcor = ImageDraw.Draw(coral)
    labels = []
    for idx, (b1, b2) in enumerate(PAIRS):
        n = len(b1)
        r_, c_ = divmod(idx, cols)
        x0 = mx + c_ * cw; y0 = my + r_ * ch
        lam1, V1 = np.linalg.eigh(H(b1)); lam2, V2 = np.linalg.eigh(H(b2))
        same = float(np.abs(lam1 - lam2).max())
        rev = b2 == b1[::-1]
        cert.append(dict(b1=b1, b2=b2, n=n, spectrum_gap=same, is_reversal=rev))
        # layout inside the cell: two portraits side by side, spine between
        pw = 0.40 * cw; gapx = 0.08 * cw
        px1 = x0 + 0.06 * cw; px2 = px1 + pw + gapx
        ptop = y0 + 0.10 * ch; pbot = y0 + 0.66 * ch
        lmin, lmax = lam1.min() - 0.3, lam1.max() + 0.3
        ly = lambda l: pbot - (l - lmin) / (lmax - lmin) * (pbot - ptop)
        bead = pw / n
        rmax = 0.46 * min(bead, (pbot - ptop) / n)
        for (px, lam, Vv, b) in ((px1, lam1, V1, b1), (px2, lam2, V2, b2)):
            for i in range(n):
                for j in range(n):
                    a = Vv[j, i]
                    rr = rmax * np.sqrt(abs(a)) * 1.9
                    if rr < 0.6:
                        continue
                    x = px + (j + 0.5) * bead; y = ly(lam[i])
                    tint = P.PIG['aqua'] if a > 0 else P.PIG['apricot']
                    dens = 0.55 + 0.6 * abs(a)
                    ab = dens * P.absorb(tint)
                    for cch in range(3):
                        dfs[cch].ellipse([x - rr, y - rr, x + rr, y + rr], fill=float(ab[cch]))
            # necklace below the portrait
            yb = pbot + 0.10 * ch
            rb = 0.42 * bead
            for j, chb in enumerate(b):
                x = px + (j + 0.5) * bead
                if chb == '1':
                    dink.ellipse([x - rb, y - rb if False else yb - rb, x + rb, yb + rb], fill=0.95)
                else:
                    dink.ellipse([x - rb, yb - rb, x + rb, yb + rb], outline=0.9, width=max(1, int(round(0.9 * SS))))
            # eigenvalue ticks at the portrait's left edge (ink)
            for l in lam:
                dink.line([(px - 0.012 * cw, ly(l)), (px, ly(l))], fill=0.7, width=max(1, int(round(0.8 * SS))))
        # shared spine: coral ticks between the two portraits, one per eigenvalue
        xs0 = px1 + pw + 0.25 * gapx; xs1 = px2 - 0.25 * gapx
        for l in lam1:
            dcor.line([(xs0, ly(l)), (xs1, ly(l))], fill=1.0, width=max(1, int(round(1.6 * SS))))
        labels.append((f"n = {n}" + ("" if idx >= len(FAMILY) else f"   (family k = {idx})") + ("" if idx < len(FAMILY) else "   primitive"),
                       x0 + 0.5 * cw, y0 + 0.03 * ch, int(0.0095 * Wd), 'italic', 'mm'))
        labels.append((b1, px1 + 0.5 * pw, pbot + 0.19 * ch, int(0.0085 * Wd), 'mono', 'mm'))
        labels.append((b2, px2 + 0.5 * pw, pbot + 0.19 * ch, int(0.0085 * Wd), 'mono', 'mm'))
    A = np.stack([np.asarray(im, np.float32) for im in fills], axis=-1)
    g = P.noise(Hd, Wd, 1.6, seed + 11)
    A *= (1 + 0.14 * g)[..., None]
    A = gaussian_filter(A, [0.5 * SS, 0.5 * SS, 0])
    sh.A += A; del A
    sh.wash(gaussian_filter(np.asarray(ink, np.float32), 0.45 * SS) * 0.9, INK)
    sh.wash(gaussian_filter(np.asarray(coral, np.float32), 0.6 * SS) * 1.5, 'coral')
    sh.wash(P.text_density(Wd, Hd, labels) * 0.9, INK)
    # the 12th cell: the theorem, as text
    r_, c_ = divmod(len(PAIRS), cols)
    x0 = mx + c_ * cw; y0 = my + r_ * ch
    thm = [("The Cayley–Hamilton ladder", x0 + 0.5 * cw, y0 + 0.16 * ch, int(0.0125 * Wd), 'serif_bold', 'mm'),
           ("χ(u Xᵏ v) = e₁ᵀ P_u P_Xᵏ P_v e₁ and P_X is 2×2 with det 1,", x0 + 0.5 * cw, y0 + 0.30 * ch, int(0.0095 * Wd), 'italic', 'mm'),
           ("so P_X^{k+2} = tr(P_X)·P_X^{k+1} − P_Xᵏ: two agreeing rungs", x0 + 0.5 * cw, y0 + 0.38 * ch, int(0.0095 * Wd), 'italic', 'mm'),
           ("make every rung agree. The six left-hand specimens are", x0 + 0.5 * cw, y0 + 0.46 * ch, int(0.0095 * Wd), 'italic', 'mm'),
           ("one ladder, X = 01; the five primitive pairs have no ladder", x0 + 0.5 * cw, y0 + 0.54 * ch, int(0.0095 * Wd), 'italic', 'mm'),
           ("we could find below n = 14.", x0 + 0.5 * cw, y0 + 0.62 * ch, int(0.0095 * Wd), 'italic', 'mm')]
    sh.wash(P.text_density(Wd, Hd, thm) * 1.0, INK)
    sh.caption_strip(0.92, 0.99, 0.55)
    items = [("The Same Song", 0.5 * Wd, 0.94 * Hd, int(0.032 * Wd), 'serif_bold', 'mm'),
             ("Eleven pairs of 0/1 strings whose Jacobi matrices share every eigenvalue (the coral spine) yet are not reverses of each other: aqua/apricot coins are the eigenvectors, sized by weight — the same music, other words.",
              0.5 * Wd, 0.972 * Hd, int(0.0105 * Wd), 'italic', 'mm')]
    sh.wash(P.text_density(Wd, Hd, items) * 1.1, INK)
    img = sh.develop()
    P.finish(img, (S, S), out)
    json.dump(cert, open(out.replace('.png', '_cert.json'), 'w'), indent=1)
    print(f'render {out} {time.time()-t0:.0f}s; max spectrum gap over pairs = {max(c["spectrum_gap"] for c in cert):.1e}', flush=True)


if __name__ == '__main__':
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    out = sys.argv[2] if len(sys.argv) > 2 else f'proto_song_{S}.png'
    render(S=S, out=out)
