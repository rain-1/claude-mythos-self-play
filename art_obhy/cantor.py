"""03 - The Real the List Forgot: Cantor's diagonal argument (annotated plate).

A list of reals r_1, r_2, ... shown as rows of binary digits (the bits here
spell a luminous interference tableau -- the argument works for ANY list, so
we choose a beautiful one). Read the diagonal d_k = (k-th digit of r_k); the
real D with digit_k = 1 - d_k differs from every r_k at place k, so D is on no
row. The blazing gold thread down the diagonal is read off, flipped, and laid
out as the hot strip below: a real the list forgot. The same flip is Goedel's.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import artkit as ak

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6],
                   [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16.0
FONT = "/usr/share/fonts/truetype/dejavu/"


def field(N):
    i = np.linspace(-1, 1, N)
    Y, X = np.meshgrid(i, i)
    R = np.hypot(X, Y); A = np.arctan2(Y, X)
    f = (0.5 + 0.28 * np.sin(13 * R - 2.0)
         + 0.16 * np.sin(7 * A + 9 * R) + 0.12 * np.cos(19 * R + 3 * A))
    f = (f - f.min()) / (f.max() - f.min())
    f *= (1.0 - 0.30 * R ** 2).clip(0, 1)
    return f


def render(N=300, cell=5, S=2048, fname="03_cantor_2048.png",
           expo_k=1.5, sat=1.2, gamma=1/1.95, bloom_amp=1.0):
    T = N * cell
    ox = (S - T) // 2
    oy = 96
    drow_y = oy + T + 64                       # top of the D barcode row
    drow_h = 44

    F = field(N)
    bayer = np.tile(BAYER4, (N // 4 + 1, N // 4 + 1))[:N, :N]
    bits = (F > bayer).astype(np.uint8)

    teal = np.array([0.10, 0.47, 0.64], np.float32)
    indigo = np.array([0.22, 0.30, 0.72], np.float32)
    off = np.array([0.02, 0.045, 0.10], np.float32)
    hot = np.array([1.0, 0.30, 0.55], np.float32)

    on = teal[None, None] * (1 - F[..., None]) + indigo[None, None] * F[..., None]
    img = np.where(bits[..., None] == 1, on, off[None, None]).astype(np.float32)
    img *= (0.55 + 0.85 * F[..., None])
    up = np.repeat(np.repeat(img, cell, 0), cell, 1)

    canvas = np.zeros((S, S, 3), np.float32)
    canvas[oy:oy + T, ox:ox + T] = up

    dk = bits[np.arange(N), np.arange(N)]
    D = 1 - dk

    # faint "rain" tracers: every column from diagonal cell down to D row
    xs_all = ox + (np.arange(N) + 0.5) * cell
    diag_y = oy + (np.arange(N) + 0.5) * cell
    # vectorised faint vertical wash
    for k in range(N):
        x = int(round(xs_all[k]))
        y0 = int(round(diag_y[k])); y1 = drow_y
        canvas[y0:y1, x] += np.array([0.05, 0.045, 0.06], np.float32)

    # blazing gold diagonal thread (additive splats)
    npts = T
    tx = ox + np.linspace(0, T, npts)
    ty = oy + np.linspace(0, T, npts)
    gold = np.array([1.0, 0.80, 0.32], np.float32)
    ak.splat_add(canvas, tx, ty, gold, radius=max(1.8, cell * 0.55), intensity=0.55)

    # a few bright tracer lines (the flip operation), gold -> pink
    picks = np.linspace(8, N - 8, 9).astype(int)
    for k in picks:
        x = int(round(xs_all[k]))
        y0 = int(round(diag_y[k])); y1 = drow_y + drow_h // 2
        yy = np.arange(y0, y1)
        if len(yy) < 2:
            continue
        t = (yy - y0) / (y1 - y0)
        col = (1 - t)[:, None] * gold + t[:, None] * hot
        canvas[yy, x] += col * 0.5
        canvas[yy, x - 1] += col * 0.25
        canvas[yy, x + 1] += col * 0.25

    # the forgotten real D as a hot barcode row
    for k in range(N):
        x0 = ox + k * cell
        v = 0.28 + 0.72 * D[k]
        canvas[drow_y:drow_y + drow_h, x0:x0 + cell] += hot * v

    canvas = ak.bloom(canvas, sigmas=(1.5, 5, 14),
                      amps=(0.11*bloom_amp, 0.07*bloom_amp, 0.045*bloom_amp))
    rgb = ak.filmic(canvas, k=expo_k)
    luma = (0.2126*rgb[..., 0]+0.7152*rgb[..., 1]+0.0722*rgb[..., 2])[..., None]
    rgb = np.clip(luma + (rgb - luma) * sat, 0, 1)
    rgb = ak.gamma(rgb, gamma)

    # ---- text, drawn crisp after tone-mapping ----
    im = Image.fromarray(np.clip(rgb * 255 + 0.5, 0, 255).astype(np.uint8), "RGB")
    dr = ImageDraw.Draw(im)
    f_tag = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 26)
    f_title = ImageFont.truetype(FONT + "DejaVuSans-Bold.ttf", 60)
    f_body = ImageFont.truetype(FONT + "DejaVuSans.ttf", 30)
    f_mono = ImageFont.truetype(FONT + "DejaVuSansMono-Bold.ttf", 26)

    # label for D row
    dr.text((ox, drow_y - 40), "D = the diagonal, flipped", font=f_mono, fill=(255, 150, 185))
    bitstr = "0." + "".join(str(b) for b in D[:46]) + "…"
    dr.text((ox, drow_y + drow_h + 12), bitstr, font=f_mono, fill=(255, 120, 165))

    # caption block at the bottom
    cy = drow_y + drow_h + 86
    dr.rectangle([ox, cy, ox + 8, cy + 168], fill=(255, 200, 90))
    dr.text((ox + 28, cy - 2), "FIGURE · DIAGONALIZATION", font=f_tag, fill=(255, 200, 90))
    dr.text((ox + 28, cy + 30), "The Real the List Forgot", font=f_title, fill=(238, 240, 248))
    body = ("Every row above is a real number, written in binary. Read the gold "
            "diagonal — digit k of\nreal k — and flip every bit. The result D differs "
            "from row k at place k, for every k,\nso D is on no row. No list of the reals "
            "is complete; the same flip is Gödel's sentence.")
    dr.multiline_text((ox + 28, cy + 104), body, font=f_body, fill=(150, 160, 178), spacing=8)

    im.save(fname)
    print("wrote", fname, "N", N, "D-on-no-row:", bool(np.all(D == 1 - dk)))


if __name__ == "__main__":
    render()
