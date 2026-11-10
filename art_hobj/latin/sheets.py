"""Four checkered sheets of tissue (the bits of i XOR j) weigh 8, 4, 2, 1 and sum to a 16x16 Latin square of rank 5;
below, the exhaustive minimum rank r(n) for n = 2..7 with one extremal square each (rank.c)."""
import numpy as np, sys, json
sys.path.insert(0, '../domino')
from render import dominoes, blur, shift, font, wheel
from PIL import Image, ImageDraw

def pillow_grid(colors, px):
    """colors (n,n,3) -> RGB float tile (side px*(n+1)) of glossy square pillows with soft shadow on paper, + offset."""
    n = colors.shape[0]; u = px; S = int(u * (n + 1)); x0 = y0 = u / 2
    idx = np.arange(n * n, dtype=np.int32).reshape(n, n)
    cen = np.array([[c + 0.5, r + 0.5] for r in range(n) for c in range(n)]); half = np.full((n * n, 2), 0.5)
    h, alb, msk = dominoes(S, x0, y0, u, idx, cen, half, colors.reshape(-1, 3).astype(np.float32), 0.20)
    Lv = np.array([-0.42, -0.55, 0.72]); Lv /= np.linalg.norm(Lv); Hv = Lv + np.array([0, 0, 1.0]); Hv /= np.linalg.norm(Hv)
    gy, gx = np.gradient(h); nz = 1 / np.sqrt(gx * gx + gy * gy + 1); nx = -gx * nz; ny = -gy * nz
    dif = np.clip(nx * Lv[0] + ny * Lv[1] + nz * Lv[2], 0, 1); sp = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1)
    dom = alb * (0.70 + 0.40 * dif)[..., None]
    dom = dom * (1 - 0.10 * (1 - nz)[..., None]) + 0.10 * (1 - nz)[..., None] * np.array([0.72, 0.74, 0.95])
    gl = np.clip((sp - 0.975) / 0.02, 0, 1) ** 1.5 * 0.75; dom = dom + gl[..., None] * (1 - dom)
    so = max(int(0.07 * u), 1)
    sh = blur(shift(msk, so, int(so * 1.3)), 0.09 * u) * 0.55 + blur(msk, 0.05 * u) * 0.25
    return dom, msk, sh, S

def place(canvas, colors, x, y, side, labels=None, fsz=0.3):
    n = colors.shape[0]; px = side / n
    dom, msk, sh, T = pillow_grid(colors, px)
    xi = int(x - px / 2); yi = int(y - px / 2)
    reg = canvas[yi:yi + T, xi:xi + T]
    reg[:] = reg * (1 - sh[..., None] * (1 - np.array([0.62, 0.60, 0.80])))
    reg[:] = reg * (1 - msk[..., None]) + dom * msk[..., None]
    return px

def main(S, out):
    canvas = np.empty((S, S, 3), np.float32); canvas[:] = (0.992, 0.985, 0.975)
    canvas += blur(np.random.default_rng(3).normal(0, 1, (S, S)), 0.7 * S / 1024)[..., None] * 0.006
    HUE = np.array([[1.0, 0.62, 0.72], [1.0, 0.86, 0.52], [0.52, 0.90, 0.76], [0.62, 0.72, 1.0]])
    n = 16; L = np.array([[i ^ j for j in range(n)] for i in range(n)])
    def qcol(v):
        t = 0.30 + 0.70 * ((v & 3) / 3.0); return 1 - t * (1 - HUE[v >> 2])
    cols = np.array([[qcol(L[i, j]) for j in range(n)] for i in range(n)])
    QX, QY, QS = 0.075 * S, 0.050 * S, 0.585 * S
    px = place(canvas, cols, QX, QY, QS)
    # minimal-rank strip
    ex = json.load(open('examples.json')); ranks = {2: 2, 3: 3, 4: 3, 5: 5, 6: 4, 7: 6}
    cu = 0.0222 * S; gap = (0.85 * S - 27 * cu) / 5; sbot = 0.862 * S; spos = {}; sx = QX
    for k, nn in enumerate(range(2, 8)):
        M = np.array(ex[str(nn)]); c = 1 - 0.80 * (1 - wheel(0.02 + 0.80 * (M - 1) / (nn - 1) * (1 - 1 / nn)))
        ss = cu * nn; sy = sbot - ss; place(canvas, c, sx, sy, ss); spos[nn] = (sx, sy, ss, M); sx += ss + gap
    im = Image.fromarray((np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(im, 'RGBA')
    ink = (92, 77, 102, 255); soft = (132, 118, 146, 255)
    # numerals on the quilt
    f = font('liberation/LiberationSerif-Regular.ttf', px * 0.30)
    for i in range(n):
        for j in range(n):
            d.text((QX + (j + 0.5) * px, QY + (i + 0.5) * px), str(L[i, j] + 1), font=f, fill=(92, 77, 102, 150), anchor='mm')
    for nn, (sx, sy, ss, M) in spos.items():
        p2 = ss / nn; f2 = font('liberation/LiberationSerif-Regular.ttf', p2 * 0.34)
        for i in range(nn):
            for j in range(nn):
                d.text((sx + (j + 0.5) * p2, sy + (i + 0.5) * p2), str(M[i, j]), font=f2, fill=(92, 77, 102, 150), anchor='mm')
        d.text((sx + ss / 2, sy - 0.016 * S), f'n = {nn}', font=font('liberation/LiberationSerif-Italic.ttf', 0.0165 * S), fill=ink, anchor='mm')
        col = (240, 96, 92, 255) if ranks[nn] in (5, 6) and nn in (5, 7) else ink
        d.text((sx + ss / 2, sy + ss + 0.020 * S), f'rank {ranks[nn]}', font=font('liberation/LiberationSerif-Bold.ttf', 0.019 * S), fill=col, anchor='mm')
    # the four sheets (tissue) on the right
    tx = 0.765 * S; ts = 0.128 * S; tg = (QS - 4 * ts) / 3
    sheet = Image.new('RGBA', im.size, (0, 0, 0, 0)); shd = Image.new('L', im.size, 0); ds = ImageDraw.Draw(sheet); dsh = ImageDraw.Draw(shd)
    tints = [(150, 170, 250), (255, 150, 180), (255, 200, 110), (110, 210, 175)]
    for k, bit in enumerate((3, 2, 1, 0)):
        ty = QY + k * (ts + tg); c = ts / 16
        dsh.rectangle((tx + 0.006 * S, ty + 0.008 * S, tx + ts + 0.006 * S, ty + ts + 0.008 * S), fill=70)
    from PIL import ImageFilter
    shd = shd.filter(ImageFilter.GaussianBlur(0.006 * S))
    lav = Image.new('RGBA', im.size, (150, 140, 200, 255)); lav.putalpha(shd); im.alpha_composite(lav); d = ImageDraw.Draw(im, 'RGBA')
    for k, bit in enumerate((3, 2, 1, 0)):
        ty = QY + k * (ts + tg); c = ts / 16
        T = int(ts); cpx = T / 16.0
        ii = np.minimum((np.arange(T) / cpx).astype(int), 15)
        m = (((ii[:, None] ^ ii[None, :]) >> bit) & 1).astype(np.float32)
        m = blur(m, max(S / 3000, 0.5))
        rr = np.random.default_rng(10 + k)
        fib = blur(rr.normal(0, 1, (T, T)), S / 700) * 0.9 + blur(rr.normal(0, 1, (T, T)), S / 180) * 2.2
        dens = [1.0, 0.80, 0.64, 0.52][k]
        tint = np.array([[0.60, 0.56, 0.93], [0.64, 0.60, 0.94], [0.68, 0.65, 0.95], [0.72, 0.70, 0.96]][k])
        a_ = np.clip(m * dens * (1 + 0.10 * fib), 0, 1)[..., None]
        base_ = np.array([1.0, 0.997, 0.992]) * (1 + 0.012 * fib[..., None])
        tile = base_ * (1 - a_) + (1 - (1 - tint) * (0.55 + 0.45 * dens)) * a_
        yy_, xx_ = np.mgrid[0:T, 0:T] / T
        tile = tile * (0.985 + 0.03 * (1 - xx_ - yy_ + 1)[..., None] / 2)
        im.paste(Image.fromarray((np.clip(tile, 0, 1) * 255).astype(np.uint8)), (int(tx), int(ty)))
        d = ImageDraw.Draw(im, 'RGBA')
        d.rectangle((int(tx), int(ty), int(tx) + T, int(ty) + T), outline=(150, 136, 190, 110), width=max(int(S / 1400), 1))
        d.text((tx - 0.018 * S, ty + ts / 2), f'{1 << bit} ×', font=font('liberation/LiberationSerif-Bold.ttf', 0.030 * S), fill=ink, anchor='rm')
        if k < 3: d.text((tx + ts / 2, ty + ts + tg / 2), '+', font=font('liberation/LiberationSerif-Regular.ttf', 0.026 * S), fill=soft, anchor='mm')
    d.text((QX + QS + 0.028 * S, QY + QS / 2), '=', font=font('liberation/LiberationSerif-Regular.ttf', 0.05 * S), fill=soft, anchor='mm')
    d.text((tx + ts + 0.012 * S, QY + QS + 0.004 * S), '+ 1', font=font('liberation/LiberationSerif-Bold.ttf', 0.024 * S), fill=ink, anchor='ra')
    d.text((QX, QY + QS + 0.040 * S), 'the fewest independent rows a Latin square on 1…n can have — every square checked, one of the leanest shown', font=font('liberation/LiberationSerif-Italic.ttf', 0.0160 * S), fill=ink)
    y = 0.902 * S
    d.text((QX, y), 'Four Sheets Hold Two Hundred and Fifty-Six Facts', font=font('liberation/LiberationSerif-Bold.ttf', 0.030 * S), fill=ink)
    d.text((QX, y + 0.042 * S), 'A 16×16 Latin square is four checkered sheets and a constant: rank 5.  Can the laws stay few as the table grows?', font=font('liberation/LiberationSerif-Italic.ttf', 0.0172 * S), fill=ink)
    d.text((QX, y + 0.066 * S), 'cell = 1 + (row XOR column) · hue = the two heavy sheets, depth = the two light ones · minimum rank 2 3 3 5 4 6 for n = 2…7: not monotone', font=font('dejavu/DejaVuSansMono.ttf', 0.0098 * S), fill=soft)
    im.convert('RGB').save(out); print('saved', out)

if __name__ == '__main__':
    main(int(sys.argv[1]), sys.argv[2])
