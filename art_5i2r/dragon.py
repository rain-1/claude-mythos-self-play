"""dragon.py — MO 514916 'Nearest missing points of the Binary Dragon'.

D_0 = {0}, D_{k+1} = beta D_k  U  (1 - beta D_k),  beta = 1+i.
s_k = min { |z|^2 : z in Z[i] \\ D_k }.

Claim (found 2026-09-05): the nearest missing point is beta^(k-1)/3 rounded AWAY from zero
coordinate-wise, i.e. with c = beta^(k-1)/3 = u + i v,
    z_k = sgn(u)*ceil(|u|) + i * sgn(v)*ceil(|v|),   s_k = |z_k|^2.
(For k = 2 mod 4 the two coordinates of c are 2^j/3 with fractional part 1/3 and only ONE of them
rounds outward; the formula below handles all residues by explicit cases and is checked against the
poster's 64-row table and against exhaustive enumeration of D_k for k <= 24.)
"""
import numpy as np, json, sys, time

TABLE = {1:1,2:1,3:1,4:2,5:4,6:5,7:9,8:18,9:36,10:61,11:121,12:242,13:484,14:925,15:1849,16:3698,
17:7396,18:14621,19:29241,20:58482,21:116964,22:233245,23:466489,24:932978,25:1865956,26:3729181,
27:7458361,28:14916722,29:29833444,30:59655965,31:119311929,32:238623858,33:477247716,34:954451741,
35:1908903481,36:3817806962,37:7635613924,38:15271053085,39:30542106169,40:61084212338,
41:122168424676,42:244336150301,43:488672300601,44:977344601202,45:1954689202404,46:3909375608605,
47:7818751217209,48:15637502434418,49:31275004868836,50:62549998552861,51:125099997105721,
52:250199994211442,53:500399988422884,54:1000799932106525,55:2001599864213049,56:4003199728426098,
57:8006399456852196,58:16012798734747421,59:32025597469494841,60:64051194938989682,
61:128102389877979364,62:256204779040130845,63:512409558080261689,64:1024819116160523378}


def s_formula(k):
    """closed form: j = floor((k-1)/2); q = 2^j / 3 (exact rational, j >= 0).
    k odd  : s = ceil(q)^2                       (c = unit * 2^j/3 on an axis)
    k even : c = 2^j/3 * (±1 ± i)  ->  s = ceil(q)^2 + (ceil(q)^2 if frac(q)=2/3 else floor(q)^2)
    """
    j = (k - 1) // 2
    p = 2 ** j
    cq, fq = -(-p // 3), p // 3          # ceil, floor of p/3
    if k % 2 == 1:
        return cq * cq
    # k even: beta^(k-1) = beta^(2j+1) = (2i)^j (1+i): coordinates ±2^j, ±2^j -> c = 2^j/3 (±1±i)
    if p % 3 == 2:                        # frac = 2/3 : both coordinates round outward
        return 2 * cq * cq
    return cq * cq + fq * fq             # frac = 1/3 : one outward, one inward


def s_from_c(k):
    """the geometric statement: round beta^(k-1)/3 outward (for k = 2 mod 4 one coord inward)."""
    c = (1 + 1j) ** (k - 1) / 3
    u, v = c.real, c.imag
    out = lambda t: 0 if abs(t) < 1e-9 else int(np.sign(t)) * int(np.ceil(abs(t) - 1e-9))
    inn = lambda t: 0 if abs(t) < 1e-9 else int(np.sign(t)) * int(np.floor(abs(t) + 1e-9))
    z = complex(out(u), out(v))
    if k % 4 == 2:
        z2 = complex(inn(u), out(v))
        return z, z2
    return z, None


def enumerate_D(k):
    D = np.array([0], dtype=np.complex128)
    b = 1 + 1j
    for _ in range(k):
        D = np.concatenate([b * D, 1 - b * D])
        D = np.unique(np.round(D.real).astype(np.int64) + 1j * np.round(D.imag).astype(np.int64))
    return D


def s_enum(k):
    D = enumerate_D(k)
    Dset = set(zip(D.real.astype(np.int64).tolist(), D.imag.astype(np.int64).tolist()))
    # scan Gaussian integers by |z|^2 until one is missing
    R = int(np.sqrt(2 ** k / 18.0) * 1.6) + 3
    best = None
    for a in range(-R, R + 1):
        for b_ in range(-R, R + 1):
            n2 = a * a + b_ * b_
            if best is not None and n2 >= best[0]:
                continue
            if (a, b_) not in Dset:
                best = (n2, a, b_)
    return best, len(D)


if __name__ == '__main__':
    ok = all(s_formula(k) == TABLE[k] for k in TABLE)
    print('closed form vs poster table k=1..64:', 'ALL 64 AGREE' if ok else 'MISMATCH')
    for k in TABLE:
        if s_formula(k) != TABLE[k]:
            print('  mismatch', k, s_formula(k), TABLE[k])
    # geometric rounding statement
    ok2 = True
    for k in TABLE:
        z, z2 = s_from_c(k)
        s = int(round(abs(z) ** 2)) if z2 is None else int(round(abs(z2) ** 2))
        if s != TABLE[k]:
            ok2 = False; print('  rounding mismatch', k, z, z2, TABLE[k])
    print('outward-rounding statement:', 'AGREES' if ok2 else 'FAILS')
    # exhaustive enumeration
    rows = []
    for k in range(1, 25):
        t = time.time()
        (s, a, b_), card = s_enum(k)
        z, z2 = s_from_c(k)
        rows.append(dict(k=k, s_enum=s, z=[a, b_], s_formula=s_formula(k), card=card,
                         c=[((1+1j)**(k-1)/3).real, ((1+1j)**(k-1)/3).imag]))
        print(f'k={k:2d} |D_k|={card:9d} s_enum={s:9d} at {a:+d}{b_:+d}i  formula={s_formula(k):9d}  '
              f'c={(1+1j)**(k-1)/3:.3f}  {time.time()-t:.1f}s', flush=True)
        assert s == s_formula(k)
    json.dump(rows, open('dragon_census.json', 'w'), indent=1)
    print('exhaustive k<=24: formula holds; |D_k| = 2^k (all distinct):',
          all(r['card'] == 2 ** r['k'] for r in rows))
