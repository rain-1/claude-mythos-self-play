"""board.py SIZE out — 'Four Carry More Than Five': the chevron lemma for rows of crates, in chalk.
At the moment a row stands diagonal to the lane, the lane round it is a chevron sqrt(2)*w thick."""
import sys, numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont
from chalk import Board, rgb, CREAM, RED, F_I, F_R

def main():
    S = int(sys.argv[1]); out = sys.argv[2]
    u = S / 4096.0
    B = Board(S, seed=3)
    BX0, BX1, BY0, BY1 = 330 * u, 3766 * u, 300 * u, 3290 * u
    r2 = np.sqrt(2); n = 4; w = (n + 4) * (r2 - 1) / 2; m = w - 1
    k = 292 * u; cx = BX0 + 1130 * u; yA = BY0 + 610 * u
    T = lambda x, d: (cx + k * x, yA + k * d)          # x along the row, d = depth below the outer apex
    # ghost of yesterday's lesson, rubbed out
    B.text(BX0 + 2250 * u, BY0 + 2680 * u, "3/5 · 4/5 · 12/13 ···", 116 * u, pressure=0.55, dust=0)
    B.text(BX0 + 2250 * u, BY0 + 2840 * u, "= 2/5", 150 * u, pressure=0.55, dust=0)
    B.rub(BX0 + 2760 * u, BY0 + 2720 * u, 640 * u, 250 * u, strength=0.55, seed=5)
    # the chevron: outer V and inner V
    E = 3.25
    B.line(T(-E, E), T(0, 0), 15 * u, 0.82); B.line(T(0, 0), T(E, E), 15 * u, 0.82)
    D = r2 * w
    B.line(T(-E, D + E), T(0, D), 15 * u, 0.82); B.line(T(0, D), T(E, D + E), 15 * u, 0.82)
    # wall hatching outside the outer V and below the inner V
    for t in np.arange(0.25, E, 0.30):
        for sgn in (-1, 1):
            p = T(sgn * t, t); B.line(p, (p[0] + sgn * 40 * u, p[1] - 40 * u), 6 * u, 0.42, dust=0.2)
            q = T(sgn * t, D + t); B.line(q, (q[0] - sgn * 40 * u, q[1] + 40 * u), 6 * u, 0.42, dust=0.2)
    # the row of four: ends hang from the outer V, the middle sits on the inner corner
    cols = [(-2, n / 2), (-1, n / 2 - m), (0, n / 2 - m), (1, n / 2)]     # (left x, depth of top)
    for x0, d0 in cols:
        P = [T(x0, d0), T(x0 + 1, d0), T(x0 + 1, d0 + 1), T(x0, d0 + 1)]
        for i in range(4): B.line(P[i], P[(i + 1) % 4], 13 * u, 0.86)
        for j in range(1, 6):                                            # light hatching: the crate is solid
            a_ = T(x0 + j / 6, d0 + 0.06); b_ = T(x0 + j / 6 - 0.0, d0 + 0.94)
            B.line(a_, b_, 5 * u, 0.30, dust=0.15)
    # dimensions
    def dim(p, q, label, off=(0, 0), px=92, **kw):
        B.arrow(p, q, 7 * u, 0.6, head=36 * u); B.arrow(q, p, 7 * u, 0.6, head=36 * u)
        B.text((p[0] + q[0]) / 2 + off[0] * u, (p[1] + q[1]) / 2 + off[1] * u, label, px * u, anchor='ms', pressure=0.7, **kw)
    xr = 2.62
    dim(T(xr, n / 2 - m), T(xr, n / 2 + 1), "w", off=(64, 30), px=110)
    B.line(T(1.05, n / 2 - m), T(xr + 0.12, n / 2 - m), 5 * u, 0.4, dash=(30 * u, 26 * u), dust=0.2)
    B.line(T(2.05, n / 2 + 1), T(xr + 0.12, n / 2 + 1), 5 * u, 0.4, dash=(30 * u, 26 * u), dust=0.2)
    dim(T(-2, n / 2 + 1.42), T(0, n / 2 + 1.42), "n/2", off=(0, 104), px=96)
    B.line(T(-2, n / 2 + 1.05), T(-2, n / 2 + 1.52), 5 * u, 0.4, dust=0.2)
    dim(T(0, 0.10), T(0, D - 0.10 - m - 1 + 1 - 0.0 if False else n / 2 - m - 0.08), "", off=(0, 0))
    B.text(T(0, 0)[0] - 60 * u, T(0, 0.70)[1], "n/2 − rise", 80 * u, anchor='rs', pressure=0.66) if False else B.text(T(0.16, 0)[0], T(0, 0.66)[1], "n/2 − rise", 70 * u, pressure=0.66)
    dim(T(-3.02, 3.12), T(-3.02, D + 2.92), "√2 w", off=(-150, 30), px=96)
    # the three touches; the inner corner in red
    for p in (T(-2, 2), T(2, 2)): B.dot(p, 22 * u, 1.0)
    h = T(0, D); B.dot(h, 30 * u, 1.0, colour=RED, name='red'); B.circle(h, 56 * u, 9 * u, 0.8, colour=RED, name='red')
    B.text(h[0], h[1] + 560 * u, "the inner corner", 92 * u, anchor='ms', pressure=0.74, colour=RED, name='red')
    dim(T(-2.45, n / 2 - m), T(-2.45, n / 2), "rise", off=(-120, 30), px=84)
    B.line(T(-2.55, n / 2 - m), T(-1.05, n / 2 - m), 5 * u, 0.4, dash=(30 * u, 26 * u), dust=0.2)
    # heading
    B.text(BX0 + 150 * u, BY0 + 240 * u, "Stand the row diagonal to the lane:", 150 * u, pressure=0.80, width_boost=1.2 * u)
    B.text(BX0 + 150 * u, BY0 + 410 * u, "the lane is a chevron, √2 w thick.", 124 * u, pressure=0.64)
    B.text(BX0 + 150 * u, BY1 - 250 * u, "Ends hang from the outer walls, the middle", 108 * u, pressure=0.62)
    B.text(BX0 + 150 * u, BY1 - 112 * u, "clears the corner — and it must still lie flat.", 108 * u, pressure=0.62)
    # right column: the argument and the table
    tx = BX0 + 2330 * u; ty = BY0 + 660 * u
    B.text(tx, ty - 60 * u, "rise  ≥  1 + n/2 − √2 w", 100 * u, pressure=0.72)
    B.text(tx, ty + 76 * u, "rise  ≤  w − 1", 100 * u, pressure=0.72)
    B.text(tx, ty + 250 * u, "w = (n + 4)(√2 − 1)/2", 112 * u, pressure=0.88, width_boost=1.0 * u)
    ty2 = ty + 470 * u; row = 146 * u
    B.text(tx + 20 * u, ty2, "crates", 96 * u, pressure=0.6); B.text(tx + 380 * u, ty2, "side", 96 * u, pressure=0.6); B.text(tx + 690 * u, ty2, "carried", 96 * u, pressure=0.6)
    B.line((tx - 10 * u, ty2 + 36 * u), (tx + 1040 * u, ty2 + 40 * u), 7 * u, 0.6)
    for j, nn in enumerate(range(3, 8)):
        ww = (nn + 4) * (r2 - 1) / 2; yy = ty2 + (j + 1) * row + 10 * u
        pr = 0.9 if nn == 4 else 0.70
        B.text(tx + 90 * u, yy, str(nn), 112 * u, font=F_R, pressure=pr)
        B.text(tx + 370 * u, yy, "%.3f" % (1 / ww), 112 * u, font=F_R, pressure=pr)
        B.text(tx + 700 * u, yy, "%.4f" % (nn / ww ** 2), 112 * u, font=F_R, pressure=pr, width_boost=(1.0 * u if nn == 4 else 0))
        if nn == 4:
            B.line((tx + 680 * u, yy + 34 * u), (tx + 1010 * u, yy + 26 * u), 10 * u, 0.9, colour=RED, name='red')
            B.line((tx + 684 * u, yy + 58 * u), (tx + 1004 * u, yy + 51 * u), 10 * u, 0.9, colour=RED, name='red')
    yy = ty2 + 6 * row + 80 * u
    B.text(tx, yy, "4n(3 + 2√2)/(n + 4)²", 104 * u, pressure=0.66)
    B.text(tx, yy + 150 * u, "is greatest at n = 4.", 112 * u, pressure=0.72)
    img = B.render()
    # ---------------- the room: wall, frame, tray, moonlight -------------------------------
    x, y = B.x, B.y; rng = np.random.default_rng(8)
    wall = np.empty_like(img); wall[:] = rgb('#e9e3d4')
    wn = ndi.zoom(rng.standard_normal((S // 32 + 2, S // 32 + 2)).astype(np.float32), 32, order=3)[:S, :S]
    fine = ndi.gaussian_filter(rng.standard_normal((S, S)).astype(np.float32), 0.8 * max(1, u))
    wall *= (1 + 0.018 * wn + 0.03 * fine)[..., None]
    def box(x0, y0, x1, y1): return np.clip(np.minimum(np.minimum(x - x0, x1 - x), np.minimum(y - y0, y1 - y)) + 0.5, 0, 1)
    fw = 86 * u
    frame = box(BX0 - fw, BY0 - fw, BX1 + fw, BY1 + fw); inner = box(BX0, BY0, BX1, BY1)
    # shadow of the frame on the wall (lamp upper left)
    sh = ndi.gaussian_filter(np.roll(np.roll(frame, int(26 * u), 0), int(18 * u), 1), 16 * u)
    wall *= (1 - 0.34 * sh * (1 - frame))[..., None]
    wood = np.empty_like(img); wood[:] = rgb('#5b4334')
    grain = ndi.gaussian_filter(rng.standard_normal((S, S)).astype(np.float32), (1.2 * u, 40 * u)); grainv = ndi.gaussian_filter(rng.standard_normal((S, S)).astype(np.float32), (40 * u, 1.2 * u))
    horiz = (np.minimum(y - (BY0 - fw), (BY1 + fw) - y) < np.minimum(x - (BX0 - fw), (BX1 + fw) - x))
    wood *= (1 + 0.9 * np.where(horiz, grain, grainv))[..., None]
    # bevel on the frame
    dedge = np.minimum(np.minimum(x - (BX0 - fw), (BX1 + fw) - x), np.minimum(y - (BY0 - fw), (BY1 + fw) - y))
    wood *= (1 + 0.22 * np.exp(-dedge / (9 * u)) * np.where((y - (BY0 - fw) < x - (BX0 - fw) + 1e9) & ((dedge == y - (BY0 - fw)) | (dedge == x - (BX0 - fw))), 1, -0.8))[..., None]
    out_img = wall * (1 - frame[..., None]) + wood * frame[..., None]
    # inner shadow of the frame onto the slate
    ish = ndi.gaussian_filter(1 - np.roll(np.roll(inner, int(14 * u), 0), int(10 * u), 1), 9 * u)
    img = img * (1 - 0.45 * np.clip(ish, 0, 1))[..., None]
    out_img = out_img * (1 - inner[..., None]) + img * inner[..., None]
    # chalk tray
    TY0, TY1 = BY1 + fw - 8 * u, BY1 + fw + 74 * u
    tray = box(BX0 - fw - 30 * u, TY0, BX1 + fw + 30 * u, TY1)
    tsh = ndi.gaussian_filter(np.roll(np.roll(tray, int(30 * u), 0), int(14 * u), 1), 14 * u)
    out_img *= (1 - 0.36 * tsh * (1 - tray))[..., None]
    tw = np.empty_like(img); tw[:] = rgb('#6a4f3d'); tw *= (1 + 0.9 * grain)[..., None]
    tw *= (1 + 0.16 * np.clip(1 - (y - TY0) / (16 * u), 0, 1) - 0.25 * np.clip((y - TY1 + 20 * u) / (20 * u), 0, 1))[..., None]
    # chalk dust lying in the tray
    dust = np.clip(ndi.gaussian_filter(rng.random((S, S)).astype(np.float32), 1.2 * u) * 2.2 - 0.9, 0, 1) * np.clip(1 - np.abs(y - (TY0 + 22 * u)) / (26 * u), 0, 1)
    tw = tw + (CREAM - tw) * (0.5 * dust)[..., None]
    out_img = out_img * (1 - tray[..., None]) + tw * tray[..., None]
    def stick(cx, L, col, tilt=0.0):
        yy0 = TY0 - 34 * u; d = B.seg_dist(cx - L / 2, yy0 + tilt * L / 2 + 14 * u, cx + L / 2, yy0 - tilt * L / 2 + 14 * u)
        m = np.clip(17 * u - d + 0.5, 0, 1)
        shade = 1 - 0.30 * np.clip((y - yy0 - 14 * u) / (17 * u), -1, 1)
        s2 = ndi.gaussian_filter(np.roll(np.roll(m, int(9 * u), 0), int(7 * u), 1), 5 * u)
        nonlocal out_img
        out_img *= (1 - 0.4 * s2 * (1 - m))[..., None]
        out_img = out_img * (1 - m[..., None]) + (col * shade[..., None] * (1 + 0.04 * fine[..., None])) * m[..., None]
    stick(BX0 + 520 * u, 250 * u, CREAM, 0.0); stick(BX0 + 860 * u, 150 * u, CREAM, 0.02); stick(BX0 + 2700 * u, 190 * u, RED * 1.02, -0.01)
    # the felt eraser
    ex0, ex1, ey0, ey1 = BX0 + 3000 * u, BX0 + 3330 * u, TY0 - 92 * u, TY0 + 6 * u
    er = box(ex0, ey0, ex1, ey1); s2 = ndi.gaussian_filter(np.roll(np.roll(er, int(12 * u), 0), int(9 * u), 1), 7 * u)
    out_img *= (1 - 0.4 * s2 * (1 - er))[..., None]
    ec = np.where(((y - ey0) < 46 * u)[..., None], rgb('#7a5a40'), rgb('#39405a') * (1 + 0.25 * fine[..., None]) + 0.10 * CREAM)
    out_img = out_img * (1 - er[..., None]) + ec * er[..., None]
    # moonlight through a window: a slanted patch with a glazing bar
    def para(x0, y0, w, h, skew):
        xs = x - x0 - skew * (y - y0)
        return np.clip(np.minimum(np.minimum(xs, w - xs), np.minimum(y - y0, h - (y - y0))) / (28 * u) + 0.5, 0, 1)
    mw = para(1500 * u, 80 * u, 1750 * u, 3050 * u, 0.36)
    bar1 = para(1500 * u + 850 * u, 80 * u, 50 * u, 3050 * u, 0.36); 
    bars = np.clip(bar1 + para(1500 * u, 80 * u + 1480 * u, 1750 * u, 60 * u, 0.36), 0, 1)
    light = ndi.gaussian_filter(mw * (1 - bars), 22 * u)
    gain = np.where(inner[..., None] > 0.5, 0.16, 0.035)
    out_img = out_img * (1 + gain * light[..., None]) + rgb('#9fb6e8') * (0.035 * light[..., None]) * (inner[..., None] * 0.8 + 0.2)
    out_img *= (0.93 + 0.0 * light)[..., None] ** 0
    # captions on the wall, in pencil
    im = Image.new('L', (S, S), 0); d = ImageDraw.Draw(im); cx = (BX0 + BX1) / 2
    from papercut import SERIF, SERIF_I
    for yy, t, fp, px in [(3600, "Four Carry More Than Five", SERIF, 104),
                          (3744, "At the moment a row of crates stands diagonal to the lane, the lane round it is a chevron. The ends must hang below the outer walls, the middle", SERIF_I, 50),
                          (3812, "must clear the inner corner, and the whole must still lie flat in the lane: so a row of n needs a lane (n + 4)(√2 − 1)/2 crates wide.", SERIF_I, 50),
                          (3904, "drawn: the row of four, to scale  ·  rows only; a tilted pair of two carries 1.1620  ·  each value checked against 46,080 moments of the turn  ·  chalk, one red", SERIF, 40)]:
        d.text((cx, yy * u), t, font=ImageFont.truetype(fp, int(round(px * u))), fill=255, anchor='ma')
    a = (np.asarray(im, np.float32) / 255.0 * 0.86)[..., None]
    out_img = out_img * (1 - a) + rgb('#4a4640') * a
    Image.fromarray((np.clip(out_img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out)

if __name__ == "__main__":
    main()
