"""hero.py S grid.json out.png [title] — the holed chessboard as an engraved specimen note."""
import sys, json, numpy as np
from PIL import Image
from intaglio import *

def smooth(t): t = np.clip(t, 0, 1); return t*t*(3 - 2*t)

def tints(P, x0, y0, x1, y1, split=True):
    u = P.u
    sl, xx, yy = P.box(x0, y0, x1, y1)
    t = smooth((xx - x0)/(x1 - x0)*1.5 - 0.25) if split else 0.5*np.ones_like(xx)
    X = xx/u; Y = yy/u
    U1 = (Y + 46*np.sin(2*np.pi*X/436) + 11*np.sin(2*np.pi*X/109))/9.5
    U2 = (Y - 46*np.sin(2*np.pi*X/436) + 11*np.sin(2*np.pi*X/109 + 1.0))/9.5
    U3 = (X + 30*np.sin(2*np.pi*Y/260))/19.0
    for U, nm, wt in ((U1, 'tintA', 1 - t), (U2, 'tintB', t)):
        gy, gx = np.gradient(U); 
        P.put(nm, sl, P.level_lines(U, 3.1*u*np.sqrt(wt) , gx, gy)*(wt > 0.02))
    gy, gx = np.gradient(U3)
    P.put('tintC', sl, P.level_lines(U3, 2.3*u, gx, gy))

def frame(P, x0, y0, x1, y1, bw, period=372.0, lw=2.2):
    """lathe-work border band between the rect and the rect inset by bw"""
    u = P.u; half = bw*0.5 - 6.4*lw*u
    def side(a0, b0, a1, b1, horiz, sgn):
        sl, xx, yy = P.box(a0, b0, a1, b1)
        if horiz: sc = xx - (x0 + x1)/2; tc = yy - (b0 + b1)/2
        else: sc = yy - (y0 + y1)/2; tc = xx - (a0 + a1)/2
        c = P.band_cov(sc, tc, half, 6, period*u, lw*u, amp=0.9)
        c = np.maximum(c, P.band_cov(sc, tc, half*0.46, 4, period*0.5*u, lw*0.8*u, amp=0.9, ph=0.7, rails=False))
        c = np.maximum(c, aa(np.abs(np.abs(tc) - (half + 4*lw*u)), 2*lw*u))
        P.put('dark', sl, c)
        for t in ('tintA', 'tintB', 'tintC'): P.cut(t, sl, (np.abs(tc) < half + 12*u)*0.6)
    side(x0 + bw, y0, x1 - bw, y0 + bw, True, 1); side(x0 + bw, y1 - bw, x1 - bw, y1, True, -1)
    side(x0, y0 + bw, x0 + bw, y1 - bw, False, 1); side(x1 - bw, y0 + bw, x1, y1 - bw, False, -1)

def pill(P, cx, cy, hw, hh, ink='dark', w=None):
    u = P.u; w = w or 1.9*u
    sl, xx, yy = P.box(cx - hw - 6*u, cy - hh - 6*u, cx + hw + 6*u, cy + hh + 6*u)
    r = min(hw, hh)
    qx = np.abs(xx - cx) - (hw - r); qy = np.abs(yy - cy) - (hh - r)
    d = np.sqrt(np.maximum(qx, 0)**2 + np.maximum(qy, 0)**2) + np.minimum(np.maximum(qx, qy), 0) - r
    inside = np.clip(-d + 0.5, 0, 1)
    for t in ('tintA', 'tintB', 'tintC', 'dark'):
        if t in P.L: P.cut(t, sl, inside)
    P.put(ink, sl, aa(np.abs(d + 1.5*w), w))

def link(P, xa, ya, xb, yb):
    """the fine double rule that joins two neighbouring medallions"""
    u = P.u
    sl, xx, yy = P.box(min(xa, xb) - 12*u, min(ya, yb) - 12*u, max(xa, xb) + 12*u, max(ya, yb) + 12*u)
    if abs(ya - yb) < 1: d = np.abs(yy - ya); inside = (xx > xa) & (xx < xb)
    else: d = np.abs(xx - xa); inside = (yy > ya) & (yy < yb)
    c = np.maximum(aa(np.abs(d - 7*u), 1.5*u), aa(d, 1.2*u))*inside
    P.put('dark', sl, c)

def draw_board(P, g, bx, by, cell, base, R=None, pairs=True, axis=None, numerals=True, lw=None, doubles=False):
    u = P.u; n = len(g); m = len(g[0]); R = R or cell*0.385
    ctr = lambda i, j: (bx + (j + 0.5)*cell, by + (i + 0.5)*cell)
    E = []
    for i in range(n):
        for j in range(m):
            if g[i][j] is None: continue
            if j + 1 < m and g[i][j+1] is not None: E.append((i, j, i, j+1))
            if i + 1 < n and g[i+1][j] is not None: E.append((i, j, i+1, j))
    for (i, j, k, l) in E:
        (xa, ya), (xb, yb) = ctr(i, j), ctr(k, l); link(P, xa, ya, xb, yb)
    for i in range(n):
        for j in range(m):
            if g[i][j] is None: continue
            x, y = ctr(i, j); medallion(P, x, y, R, g[i][j], base, numeral=numerals, w=lw)
    if not pairs: return E
    s = cell/390.0
    for (i, j, k, l) in E:
        (xa, ya), (xb, yb) = ctr(i, j), ctr(k, l); cx, cy = (xa + xb)/2, (ya + yb)/2
        a, b = GLYPH[g[i][j]], GLYPH[g[k][l]]
        red = (axis is not None and i == k and (j + 0.5 < axis < l + 0.5)) or (doubles and a == b)
        ink = 'red' if red else 'dark'
        if i == k:
            pill(P, cx, cy, 54*s, 31*s, ink, w=1.9*u*max(s, .6)); P.text(ink, a + b, cx, cy - 1*s, 52*s, 'b')
        else:
            pill(P, cx, cy, 31*s, 54*s, ink, w=1.9*u*max(s, .6))
            P.text(ink, a, cx, cy - 23*s, 46*s, 'b'); P.text(ink, b, cx, cy + 24*s, 46*s, 'b')
    return E

def centre(P, cx, cy, R, label='100'):
    """the hole: one big medallion, black-line on the left of the fold, white-line on the right"""
    u = P.u
    sl, xx, yy = P.box(cx - R - 8*u, cy - R - 8*u, cx + R + 8*u, cy + R + 8*u)
    bands = [(0.845, 0.125, 10, 10, 0.0), (0.845, 0.125, 20, 5, 0.3)]
    cov, r, th = P.rosette_cov(xx, yy, cx, cy, R, bands, 2.4*u, hub=0.70)
    cov = np.maximum(cov, aa(np.abs(r - R*0.675), 1.2*u))
    # rays in the hub
    hubm = np.clip(R*0.675 - r + 0.5, 0, 1)
    disc = np.clip(R - r + 0.5, 0, 1)
    right = np.clip((xx - cx) + 0.5, 0, 1)
    tm = P.text_mask(label, R*0.80, 'b'); h, w = tm.shape
    T = np.zeros_like(xx); y0 = int(round(cy - h/2 - 4*u)) - sl[0].start; x0 = int(round(cx - w/2)) - sl[1].start
    T[y0:y0+h, x0:x0+w] = tm
    # hub tone: fine concentric swelling lines, darker to the rim
    ring = aa(np.abs(((r/u)/9.0) - np.round((r/u)/9.0))*9.0*u, 1.0*u + 2.6*u*(r/(R*0.675))**2)*hubm
    halo = ndi.maximum_filter(T, int(13*u) | 1)
    ring = ring*(1 - halo)
    left_ink = np.maximum(cov, ring); left_ink = np.maximum(left_ink*(1 - T), T)
    right_ink = disc*(1 - 0.97*np.maximum(cov, ring))*(1 - T)
    for t in ('tintA', 'tintB', 'tintC'): P.cut(t, sl, disc*0.75)
    P.cut('dark', sl, disc)
    P.put('dark', sl, disc*(left_ink*(1 - right) + right_ink*right))

def main():
    S = int(sys.argv[1]); g = json.load(open(sys.argv[2])); out = sys.argv[3]
    mirror = len(sys.argv) > 4 and sys.argv[4] == 'm'
    P = Plate(S, seed=7); u = P.u
    px0, py0, px1, py1 = 170*u, 150*u, 3926*u, 3906*u; bw = 150*u
    P.layer('dark'); P.layer('red')
    tints(P, px0 + 10*u, py0 + 10*u, px1 - 10*u, py1 - 10*u)
    frame(P, px0, py0, px1, py1, bw)
    cell = 390*u; bx = 488*u; by = 468*u
    draw_board(P, g, bx, by, cell, 10, axis=4 if mirror else None, doubles=True)
    centre(P, bx + 4*cell, by + 4*cell, 352*u)
    # corner medallions: black-line on the left, white-line on the right
    for (x, y, d) in ((px0 + bw/2, py0 + bw/2, 0), (px0 + bw/2, py1 - bw/2, 1), (px1 - bw/2, py0 + bw/2, 5), (px1 - bw/2, py1 - bw/2, 6)):
        medallion(P, x, y, 104*u, d, 10, numeral=False)
        if d < 5: P.text('dark', '100', x, y, 44*u, 'b')
        else: P.text('dark', '100', x, y, 44*u, 'b', cut=True)
    # lettering
    def strip(txt, y, size, track):
        bb = P.text('dark', txt, S/2, y, size, 'b', track=track)
    strip('ONE  HUNDRED  ORDERED  PAIRS  OF  DIGITS  ·  EACH  EXACTLY  ONCE', 384*u, 50*u, 9*u)
    strip('READ  LEFT  TO  RIGHT  AND  TOP  TO  BOTTOM', 3672*u, 40*u, 9*u)
    P.text('red', '516966', 560*u, 3672*u, 64*u, 'm', anchor='lm')
    P.text('red', '516966', 3536*u, 3672*u, 64*u, 'm', anchor='rm')
    # margin caption
    if mirror:
        P.text('dark', 'The Left Half Is the Negative of the Right', S/2, 3962*u, 62*u, 'r')
        P.text('dark', 'Sixty squares, one hundred neighbouring pairs, 00 to 99 once each; fold it down the middle and every digit meets itself plus five.', S/2, 4034*u, 37*u, 'i')
    else:
        P.text('dark', 'Sixty Rooms, One Hundred Doors', S/2, 3962*u, 62*u, 'r')
        P.text('dark', 'A chessboard without its four middle squares. Each door bears the two digits it joins, left to right or top to bottom: 00 to 99, none twice. The ten doubles are in red.', S/2, 4034*u, 37*u, 'i')
    img = P.render(INKS, ORDER, plate=(px0 - 34*u, py0 - 34*u, px1 + 34*u, py1 + 34*u))
    Image.fromarray(img).save(out)

if __name__ == '__main__': main()
