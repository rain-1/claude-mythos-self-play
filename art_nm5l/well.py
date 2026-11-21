"""well.py — 'On Average, One Circle Holds the Well'  (Weyl's cyclic identity, MO 392723)
A journey of five legs in random directions.  Swing ONE leg full circle and the journey's end draws
a circle through where it really ended.  Count the circles that enclose home.  The count averages 1.
usage: well.py SIZE out.png [seed]"""
import sys, numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont
from chalk import Board, rgb, CREAM, RED, F_I, F_R

A = np.array([4.0, 3.0, 2.4, 1.7, 1.1])
W = [0.5233, 0.2224, 0.1563, 0.0692, 0.0288]          # math_camel/weyl.py (Bessel quadrature + 2e7 MC)

def pick(seed):
    """a journey where exactly one circle holds the well, with clear margins"""
    r = np.random.default_rng(seed); best = None
    for _ in range(200000):
        th = r.uniform(0, 2 * np.pi, 5); z = A * np.exp(1j * th); S = z.sum(); R = np.abs(S - z)
        inside = R < A
        if inside.sum() != 1 or not inside[1]: continue        # the second leg's circle: not the obvious one
        if np.min(np.abs(R - A)) < 0.45 or abs(S) < 2.2: continue
        P = np.concatenate([[0], np.cumsum(z)])
        # no leg should run along another, the path should not cross the well again
        if min(abs(P[k]) for k in range(1, 6)) < 1.2: continue
        cen = S - z; ext = max(np.max(np.abs(cen - S) + A), 0)
        score = -np.max(np.abs(np.concatenate([(cen + A), (cen - A), cen + 1j * A, cen - 1j * A]) - S).real) 
        box = [min((cen.real - A).min(), P.real.min()), max((cen.real + A).max(), P.real.max()), min((cen.imag - A).min(), P.imag.min()), max((cen.imag + A).max(), P.imag.max())]
        size = max(box[1] - box[0], (box[3] - box[2]) * 1.15)
        dmin = min(abs(th[i] - th[j]) % np.pi for i in range(5) for j in range(i))
        sc = size - 1.5 * min(dmin, 0.5)
        if best is None or sc < best[0]: best = (sc, th, box)
        if _ > 60000 and best: break
    return best

def main():
    S = int(sys.argv[1]); out = sys.argv[2]; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    u = S / 4096.0
    B = Board(S, seed=3)
    # board rectangle (inside the frame)
    BX0, BX1, BY0, BY1 = 330 * u, 3766 * u, 300 * u, 3290 * u
    sc, th, box = pick(seed)
    z = A * np.exp(1j * th); P = np.concatenate([[0], np.cumsum(z)]); End = P[-1]; cen = End - z
    # figure area: left 62 % of the board
    FX0, FX1, FY0, FY1 = BX0 + 130 * u, BX0 + 2150 * u, BY0 + 500 * u, BY1 - 420 * u
    k = min((FX1 - FX0) / (box[1] - box[0]), (FY1 - FY0) / (box[3] - box[2]))
    ox = (FX0 + FX1) / 2 - k * (box[0] + box[1]) / 2; oy = (FY0 + FY1) / 2 + k * (box[2] + box[3]) / 2
    T = lambda w: (ox + k * w.real, oy - k * w.imag)
    inside = np.abs(End - z) < A
    # ghost of yesterday's lesson, rubbed out
    B.text(BX0 + 2400 * u, BY0 + 2560 * u, "17 + 1 = 18", 150 * u, pressure=0.55, dust=0)
    B.text(BX0 + 2400 * u, BY0 + 2760 * u, "9 + 6 + 2 = 17", 150 * u, pressure=0.55, dust=0)
    B.rub(BX0 + 2850 * u, BY0 + 2620 * u, 640 * u, 300 * u, strength=0.55, seed=5)
    # the five circles
    for j in range(5):
        c = T(cen[j]); r = k * A[j]
        if inside[j]: B.circle(c, r, 15 * u, 0.80)
        else: B.circle(c, r, 9.5 * u, 0.50)
        # centre mark and the radius = a copy of leg j
        e = 20 * u
        B.line((c[0] - e, c[1] - e), (c[0] + e, c[1] + e), 6 * u, 0.55); B.line((c[0] - e, c[1] + e), (c[0] + e, c[1] - e), 6 * u, 0.55)
        B.line(c, T(End), 5.5 * u, 0.36, dash=(34 * u, 30 * u), dust=0.3)
    # the journey
    for j in range(5):
        a, b = T(P[j]), T(P[j + 1])
        B.arrow(a, b, 13 * u, 0.85, head=64 * u)
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); nrm = np.array([-(b[1] - a[1]), b[0] - a[0]]); nrm = nrm / np.hypot(*nrm)
        B.text(mid[0] + 84 * u * nrm[0], mid[1] + 84 * u * nrm[1] + 30 * u, str(j + 1), 96 * u, anchor='ms', font=F_R, pressure=0.7)
    # home (the well) in red, the end as an open ring
    h = T(0j)
    B.dot(h, 30 * u, 1.0, colour=RED, name='red'); B.circle(h, 54 * u, 9 * u, 0.8, colour=RED, name='red')
    e = T(End); B.circle(e, 34 * u, 11 * u, 0.9)
    B.text(h[0] + 80 * u, h[1] + 96 * u, "the well", 96 * u, pressure=0.7, colour=RED, name='red')
    B.text(e[0] + 70 * u, e[1] + 150 * u, "the end", 96 * u, pressure=0.66)
    # heading
    B.text(BX0 + 150 * u, BY0 + 250 * u, "Swing one leg of the journey all the way round.", 150 * u, pressure=0.80, width_boost=1.2 * u)
    B.text(BX0 + 150 * u, BY0 + 420 * u, "Its end draws a circle. Does the circle hold the well?", 118 * u, pressure=0.62)
    B.text(BX0 + 150 * u, BY1 - 250 * u, "With three legs, the three chances are", 110 * u, pressure=0.62)
    B.text(BX0 + 150 * u, BY1 - 110 * u, "the angles of their triangle, over π.", 110 * u, pressure=0.62)
    # the table, right column
    tx = BX0 + 2360 * u; ty = BY0 + 760 * u; row = 168 * u
    B.text(tx, ty, "leg", 104 * u, pressure=0.6); B.text(tx + 300 * u, ty, "length", 104 * u, pressure=0.6); B.text(tx + 690 * u, ty, "chance", 104 * u, pressure=0.6)
    B.line((tx - 20 * u, ty + 36 * u), (tx + 990 * u, ty + 40 * u), 7 * u, 0.6)
    for j in range(5):
        yy = ty + (j + 1) * row + 10 * u
        B.text(tx + 30 * u, yy, str(j + 1), 118 * u, font=F_R, pressure=0.72)
        B.text(tx + 330 * u, yy, "%.1f" % A[j], 118 * u, font=F_R, pressure=0.72)
        B.text(tx + 700 * u, yy, "%.4f" % W[j], 118 * u, font=F_R, pressure=0.72)
    yy = ty + 6 * row + 40 * u
    B.line((tx + 660 * u, yy - 128 * u), (tx + 1000 * u, yy - 124 * u), 7 * u, 0.6)
    B.text(tx + 700 * u, yy, "1.0000", 118 * u, font=F_R, pressure=0.9, width_boost=1.0 * u)
    B.line((tx + 680 * u, yy + 40 * u), (tx + 1010 * u, yy + 30 * u), 11 * u, 0.9, colour=RED, name='red')
    B.line((tx + 684 * u, yy + 66 * u), (tx + 1004 * u, yy + 58 * u), 11 * u, 0.9, colour=RED, name='red')
    B.text(tx, yy + 250 * u, "always,", 124 * u, pressure=0.7)
    B.text(tx, yy + 400 * u, "whatever the lengths.", 124 * u, pressure=0.7)
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
    for yy, t, fp, px in [(3600, "On Average, One Circle Holds the Well", SERIF, 104),
                          (3744, "Five legs, each in a direction chosen at random. Swing any one leg full circle and the end of the journey draws a circle through", SERIF_I, 50),
                          (3812, "where it really ended. The number of those circles that enclose the starting point is, on average, exactly one. (Weyl, 1938.)", SERIF_I, 50),
                          (3904, "here: legs 4, 3, 2.4, 1.7, 1.1; only the circle of leg 2 holds the well  ·  chances from 2·10⁷ random journeys and from the Bessel integral  ·  chalk, one red", SERIF, 40)]:
        d.text((cx, yy * u), t, font=ImageFont.truetype(fp, int(round(px * u))), fill=255, anchor='ma')
    a = (np.asarray(im, np.float32) / 255.0 * 0.86)[..., None]
    out_img = out_img * (1 - a) + rgb('#4a4640') * a
    Image.fromarray((np.clip(out_img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out)
    print('seed', seed, 'inside', inside, 'angles', np.round(th, 4))

if __name__ == "__main__":
    main()
