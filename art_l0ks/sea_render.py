#!/usr/bin/env python3
"""Piece III: The Sea That Forgives the Edges — MO 514552 reciprocal Pascal triangle.
Warped normalized coords: v=(k-n/2)/(n/2), x = sign(v)|v|^0.4 * W(n); edges at +-W(n),
heart magnified at center, dead sea between. Selvage drawn at fixed pixel magnification.
"""
import numpy as np, math
import artlib as A

FINAL = 2560
SS = 2
S = FINAL*SS
rs = S/1024.0

NLO, NHI = 32, 131072
TOP, BOT = int(0.075*S), int(0.795*S)
CX = S//2
PW0 = 0.455*S
SQRT2 = math.sqrt(2.0)
PWR = 0.40

def W_of(n):
    return PW0*(0.62 + 0.38*(NLO/n)**0.25)

def main():
    H = BOT-TOP
    lg0, lg1 = math.log2(NLO), math.log2(NHI)
    field = np.full((S, S), np.nan, np.float32)
    insea = np.zeros((S, S), bool)
    beadbuf = A.canvas(S)
    Arow = np.array([1.0])
    ylist = np.arange(TOP, BOT)
    n_of_y = np.round(2.0**(lg0 + (lg1-lg0)*(ylist-TOP)/(H-1))).astype(np.int64)
    rows_needed = {}
    for y, n in zip(ylist, n_of_y):
        rows_needed.setdefault(int(n), []).append(int(y))
    mass_hist = []
    xs_px = np.arange(S, dtype=np.float64)
    for n in range(1, NHI+1):
        inv = 1.0/Arow
        An = np.empty(n+1); An[0] = An[n] = 1.0
        if n >= 2: An[1:n] = inv[:-1]+inv[1:]
        Arow = An
        if n <= 300:
            sgn = 1.0 if n % 2 == 0 else -1.0
            mass_hist.append(sgn*(An-SQRT2).sum())
        if n in rows_needed:
            sgn = 1.0 if n % 2 == 0 else -1.0
            d = sgn*(An-SQRT2)
            Wn = W_of(n)
            for y in rows_needed[n]:
                xr = (xs_px - CX)/Wn
                vlim = max(0.0, 1.0 - 28.0/n)
                m = np.abs(xr) <= vlim**PWR
                v = np.sign(xr[m])*(np.abs(xr[m])**(1.0/PWR))
                kk = n/2.0 + v*(n/2.0)
                vals = np.interp(kk, np.arange(n+1), d)
                field[y, m] = vals
                insea[y, m] = True
                # selvage: fixed pixel magnification, j = index from each edge
                # drawn in the NATURAL gauge (A - sqrt2): steady columns; edges never forget
                dnat = An - SQRT2
                JW = min(16, (n+1)//2)
                wj = 5.0*rs*0.5
                for side in (0, 1):
                    for j in range(JW):
                        val = dnat[j] if side == 0 else dnat[n-j]
                        xpx = (CX - Wn + j*wj) if side == 0 else (CX + Wn - j*wj)
                        mag = min(1.0, (abs(val)/0.45)**0.30)
                        col = np.array([1.0, 0.78, 0.35]) if val > 0 else np.array([0.28, 0.60, 0.95])
                        xi = int(round(xpx))
                        wjpx = 2 if j <= 1 else 1
                        if 1 <= xi < S-2:
                            for o in range(-wjpx+1, wjpx):
                                beadbuf[y, xi+o] += col*mag*(1.45 if o == 0 else 0.6)
    # ---- colorize
    img = A.canvas(S)
    val = field
    mag = np.abs(val)
    with np.errstate(divide='ignore', invalid='ignore'):
        lg = np.log10(np.clip(mag, 1e-16, None))
    l = np.clip((lg + 15.5)/15.5, 0, 1)
    frac = np.mod(lg*2.0, 1.0)
    terr = 0.58 + 0.42*(0.5 - 0.5*np.cos(2*np.pi*frac))**0.8
    L = (l**3.0)*terr
    pos = val > 0
    warm = np.stack([1.00*L, 0.80*L, 0.42*L], -1)
    cold = np.stack([0.25*L, 0.58*L, 0.95*L], -1)
    heart = np.where(pos[..., None], warm, cold)
    heart[np.isnan(val)] = 0.0
    img += heart.astype(np.float32)*1.02
    # sea-bed tint inside the column
    img += insea[..., None]*np.array([0.026, 0.032, 0.052], np.float32)
    img += A.bloom(beadbuf, sigmas=(1.2*rs*0.5, 5*rs*0.5), weights=(1.0, 0.35))
    # heart envelope guides: u=+-1 (1/e^2 of the Gaussian): v = 2u/sqrt(n)
    gd = A.canvas(S)
    for u in (-1.0, 1.0):
        pts = []
        for y in range(TOP, BOT, 4):
            n = float(2.0**(lg0 + (lg1-lg0)*(y-TOP)/(H-1)))
            v = 2.0*u/math.sqrt(n)
            x = CX + np.sign(v)*abs(v)**PWR*W_of(n)
            pts.append([x, y])
        P = np.array(pts)
        for i in range(0, len(P)-6, 8):
            A.polyline(gd, P[i:i+5], np.array([0.45, 0.78, 0.95]), amp=1.1*rs**0.85*0.5)
    img += A.bloom(gd, sigmas=(1.2*rs*0.5,), weights=(1.0,))
    # ---- mass ledger
    LT, LB = int(0.828*S), int(0.938*S)
    mh = np.array(mass_hist)
    Mbar = 0.0654503304
    x0, x1 = int(0.10*S), int(0.90*S)
    nplot = 160
    vmin, vmax = -0.55, 0.70
    def yof(v): return LB - (v-vmin)/(vmax-vmin)*(LB-LT)
    ax = A.canvas(S)
    A.polyline(ax, np.array([[x0, yof(Mbar)], [x1, yof(Mbar)]]), np.array([1.0, 0.80, 0.42]), amp=2.0*rs**0.85*0.5)
    pts = np.array([[x0 + (x1-x0)*i/(nplot-1), yof(mh[i])] for i in range(nplot)])
    for i in range(nplot-1):
        A.polyline(ax, pts[i:i+2], np.array([0.32, 0.62, 0.92]), amp=0.9*rs**0.85*0.5)
    for i in range(0, nplot):
        A.star(ax, pts[i, 0], pts[i, 1], np.array([0.9, 0.95, 1.0]), amp=0.22*rs*rs*0.25, rad=1.2*rs*0.5)
    img += A.bloom(ax, sigmas=(1.5*rs*0.5, 6*rs*0.5), weights=(1.0, 0.3))
    out = A.tonemap(img, k=1.32, gamma=0.95)
    # ---- annotations
    F = FINAL
    small = np.asarray(A.save(out, '/tmp/tmp_sea.png', final=F)).astype(np.float32)/255.0
    GOLD = (1.0, 0.86, 0.55); GREY = (0.62, 0.66, 0.72); CYAN = (0.55, 0.78, 0.95)
    texts = [
      (0.030*F, 0.020*F, "THE SEA THAT FORGIVES THE EDGES", int(0.0205*F), GOLD, True, 'ls'),
      (0.970*F, 0.016*F, "THE SHAPE OF THE ANSWER - III", int(0.0112*F), CYAN, True, 'rs'),
      (0.970*F, 0.0315*F, "symmetry not assumed, but earned in the limit", int(0.0090*F), GREY, False, 'rs'),
      (0.030*F, 0.0385*F, "A(n+1,k) = 1/A(n,k-1) + 1/A(n,k), edges 1   (live MathOverflow 514552) - the deviation field (-1)^n (A - sqrt2), rows 32..131072 (depth = log n), x = sign(v)|v|^0.4, v = (k-n/2)/(n/2)", int(0.0088*F), GREY, False, 'ls'),
      (0.030*F, 0.0505*F, "edge selvage at fixed magnification (ribbon j = distance from edge, steady down all of time) - golden shoulders: the edges' empire in youth; terraced spine: the conserved heart; cyan dashes: its 1/e^2 envelope", int(0.0088*F), GREY, False, 'ls'),
      (0.030*F, 0.806*F, "the ledger of dissent: M(n) = (-1)^n SUM(A - sqrt2) swings between -0.4416 and +0.5725 (the boundary-layer mass = -4 SUM(B_j - sqrt2), to first order) around its conserved mean M = 0.0654503304...", int(0.0086*F), GREY, False, 'ls'),
      (0.030*F, 0.9495*F, "the edges keep golden rivers: fixed diagonals converge to B_1 = phi = 1.6180..., B_j = g(1/B_(j-1)) -> sqrt2 like (-1/3)^j - the interior remembers ONE number, its total dissent M, spread binomially", int(0.0086*F), GREY, False, 'ls'),
      (0.030*F, 0.9625*F, "A(n,k) - sqrt2  ~  (-1)^n M 2^(-n) C(n,k)   =>   central constant C = sqrt(2/pi) M = 0.05222181, measured 0.05222181 - the alternation is g'(sqrt2) = -1 for the equal-parent involution g: x -> 2/x", int(0.0086*F), GOLD, False, 'ls'),
      (0.030*F, 0.9755*F, "this answers the open asymptotics question of MO 514552 - no simple closed form for M at 11 digits (it flirts with pi/48 = 0.0654498..., and declines)", int(0.0086*F), GREY, False, 'ls'),
    ]
    outb = A.bake_text(small, texts, F)
    A.save(outb, 'sea_final.png', final=None, dither=False)
    print("saved sea_final.png")

if __name__ == '__main__':
    main()
