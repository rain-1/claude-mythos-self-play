"""stamps.py S out.png — 'Small Change': six smaller boards, one for each base 2..7, as a sheet
of engraved stamps whose face value is the number of pairs (4, 9, 16, 25, 36, 49)."""
import sys, json, numpy as np
from PIL import Image
from intaglio import *
from hero import frame, draw_board, smooth, pill

M = 'math_digits/'
STAMPS = [(2, 'sol_1_5_2_rect.json', 'A  ROW  OF  FIVE'),
          (3, 'sol_4_3_3_mask_xxx-xox-xxx-oxo.json', 'A  RING  ON  A  STEM'),
          (4, 'sol_4_4_4_mask_oxxo-xxxx-xxxx-oxxo.json', 'A  CROSS'),
          (5, 'sol_5_4_5_mask_ooxo-xxxx-xxxx-xxxx-xxxx.json', 'A  HOUSE'),
          (6, 'sol_5_5_6_hole1.json', 'A  SMALLER  BOARD'),
          (7, 'sol_5_6_7_rect.json', 'FIVE  BY  SIX')]

def main():
    S = int(sys.argv[1]); out = sys.argv[2]
    P = Plate(S, seed=3); u = P.u
    P.layer('dark'); P.layer('red')
    for t in ('tintA', 'tintB', 'tintC'): P.layer(t)
    sw, sh = 1216.0, 1750.0; ox, oy = (4096 - 3*sw)/2, 190.0
    holes = []
    for k, (b, fn, name) in enumerate(STAMPS):
        g = json.load(open(M + fn)); rows, cols = len(g), len(g[0])
        r, c = divmod(k, 3)
        x0, y0 = (ox + c*sw)*u, (oy + r*sh)*u; x1, y1 = x0 + sw*u, y0 + sh*u
        fx0, fy0, fx1, fy1 = x0 + 92*u, y0 + 92*u, x1 - 92*u, y1 - 92*u; bw = 74*u
        # tint ground: each stamp its own mixture
        sl, xx, yy = P.box(fx0 + 8*u, fy0 + 8*u, fx1 - 8*u, fy1 - 8*u)
        X = xx/u; Y = yy/u
        U1 = (Y + 30*np.sin(2*np.pi*X/260) )/13.0; U2 = (X + 30*np.sin(2*np.pi*Y/260))/13.0
        ta, tb = [('tintA', 'tintC'), ('tintC', 'tintB'), ('tintB', 'tintA'), ('tintB', 'tintC'), ('tintA', 'tintB'), ('tintC', 'tintA')][k]
        P.put(ta, sl, P.level_lines(U1, 4.6*u)); P.put(tb, sl, P.level_lines(U2, 4.0*u))
        frame(P, fx0, fy0, fx1, fy1, bw, period=228.0, lw=1.7)
        for (cx, cy) in ((fx0 + bw/2, fy0 + bw/2), (fx1 - bw/2, fy0 + bw/2), (fx0 + bw/2, fy1 - bw/2), (fx1 - bw/2, fy1 - bw/2)):
            medallion(P, cx, cy, 50*u, k % 5 + (5 if (cx > (x0 + x1)/2) else 0), 10, numeral=False, w=1.5*u)
        # value tablet at the top
        cxm = (x0 + x1)/2; ty = fy0 + bw + 150*u
        Rv = 112*u
        slv, xv, yv = P.box(cxm - Rv - 6*u, ty - Rv - 6*u, cxm + Rv + 6*u, ty + Rv + 6*u)
        cov, rr, th = P.rosette_cov(xv, yv, cxm, ty, Rv, [(0.84, 0.13, 12, 8, 0.0)], 1.8*u, hub=0.68)
        disc = np.clip(Rv - rr + 0.5, 0, 1)
        for t in ('tintA', 'tintB', 'tintC'): P.cut(t, slv, disc*0.8)
        hub = np.clip(Rv*0.68 - rr + 0.5, 0, 1)
        P.put('dark', slv, np.maximum(cov, hub))
        P.text('dark', str(b*b), cxm, ty - 2*u, (118 if b*b < 10 else 100)*u, 'b', cut=True)
        for sx, an in ((-1, 'rm'), (1, 'lm')):
            P.text('dark', 'PAIRS' if sx < 0 else 'BASE  %d' % b, cxm + sx*150*u, ty, 34*u, 'b', anchor=an, track=5*u)
        # the board
        top = ty + Rv + 40*u; bot = fy1 - bw - 110*u
        cell = min((fx1 - fx0 - 2*bw - 70*u)/cols, (bot - top)/rows, 215*u)
        bx = cxm - cols*cell/2; by = (top + bot)/2 - rows*cell/2
        draw_board(P, g, bx, by, cell, b if b % 2 == 0 else b + 1, lw=1.7*u*max(cell/(190*u), 0.8))
        P.text('dark', name, cxm, fy1 - bw - 56*u, 33*u, 'b', track=6*u)
        # perforation holes on the stamp boundary
        for t in np.arange(0.5, sw/38.0):
            holes += [(x0 + t*38*u, y0), (x0 + t*38*u, y1)]
        for t in np.arange(0.5, sh/38.0):
            holes += [(x0, y0 + t*38.04*u), (x1, y0 + t*38.04*u)]
    P.text('dark', 'Small Change', S/2, 3790*u, 60*u, 'r')
    P.text('dark', 'Six smaller boards. On each, every ordered pair of its digits is spelt by exactly one pair of neighbours, left to right or top to bottom;', S/2, 3862*u, 34*u, 'i')
    P.text('dark', 'the face value is the number of pairs. White-line medallions are the upper half of the digits.', S/2, 3908*u, 34*u, 'i')
    img = P.render(INKS, ORDER).astype(np.float32)
    # punch the perforations: paper removed, a dark table below, a soft lip
    hm = np.zeros((S, S), np.float32); rad = 10.5*u
    for (hx, hy) in set((round(a, 1), round(b_, 1)) for a, b_ in holes):
        xa, ya = int(hx - rad - 3), int(hy - rad - 3); xb, yb = int(hx + rad + 4), int(hy + rad + 4)
        if xa < 0 or ya < 0 or xb > S or yb > S: continue
        yy, xx = np.mgrid[ya:yb, xa:xb]
        hm[ya:yb, xa:xb] = np.maximum(hm[ya:yb, xa:xb], np.clip(rad - np.sqrt((xx + .5 - hx)**2 + (yy + .5 - hy)**2) + 0.5, 0, 1))
    sh_ = ndi.gaussian_filter(np.roll(np.roll(hm, int(3*u), 0), int(3*u), 1), 2*u)
    table = np.array([58, 52, 60], np.float32)
    img = img*(1 - 0.25*np.clip(sh_ - hm, 0, 1))[..., None]
    img = img*(1 - hm[..., None]) + table*(hm[..., None])*(0.75 + 0.5*sh_[..., None])
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out)

if __name__ == '__main__': main()
