import sympy as sp, json
from sympy import Rational as R
d = json.load(open('curve_model.json'))
def gr(v): return R(int(v[0]), int(v[1]))
r1 = gr(d['r1']); q = gr(d['q'])
a4,a3,a2,a1,a0 = [gr(v) for v in d['quart']]
A3,A2,A1,A0 = [gr(v) for v in d['Delta']]
ll = int(d['l']); e2,e4,e6 = [sp.Integer(v) for v in d['E']]
xS, yS = gr(d['seed'][0]), gr(d['seed'][1])
def ell_add(P1, P2):
    (x1,y1),(x2,y2) = P1,P2
    if x1 == x2 and y1 == -y2: return None
    lam = (3*x1**2 + 2*e2*x1 + e4)/(2*y1) if (x1,y1)==(x2,y2) else (y2-y1)/(x2-x1)
    x3 = lam**2 - e2 - x1 - x2
    y3 = lam*(x1-x3) - y1
    return (x3,y3)
def to_r(xE,yE,branch):
    t = xE/(A3*ll**2); Y = branch*yE/(A3*ll**3)
    c2 = 2*q*t - (a2 - a3**2/(4*q**2)); c1 = a3*t/q - a1
    if c2 == 0: return None
    w = (-c1 + Y)/(2*c2)
    if w == 0: return None
    return r1 + 1/w
def e_of_r(r):
    p = R(-1488,13355) - R(5511,13355)*(48044056139 + 1242748*r)/(r**2 - 6190029774)
    D2 = -(18958669594580211381729967107 + 1093490321304049798772416*r
           + 15172317493269316128*r**2 + 3306770731944*r**3 + 35534992*r**4)
    D = sp.sqrt(D2); assert D.is_rational
    qq = 3*D/(13355*(r**2 - 6190029774))
    best = None
    for sgn in (1,-1):
        x=(p+sgn*qq)/2; y=(p-sgn*qq)/2; z=3+(R(2,1837)-1)*(3+p)
        l = sp.lcm([sp.fraction(v)[1] for v in (x,y,z)])
        a,b,c,dd = sp.Integer(l), sp.Integer(l*x), sp.Integer(l*y), sp.Integer(l*z)
        e = a+27*(b+c+dd)
        g = sp.gcd(sp.gcd(sp.gcd(a,b), sp.gcd(c,dd)), e)
        a,b,c,dd,e = [v//g for v in (a,b,c,dd,e)]
        assert a**4+b**4+c**4+dd**4 == e**4
        cand = (len(str(abs(e))), (a,b,c,dd,e))
        if best is None or cand[0] < best[0]: best = cand
    return best
G = (xS,yS)
G2 = ell_add(G,G); G3 = ell_add(G2,G)
import math
for name, P in [("G",G), ("2G",G2), ("3G",G3)]:
    hnum = None
    for br in (1,-1):
        rr = to_r(*P, br)
        if rr is None or not rr.is_rational: continue
        digs, sol = e_of_r(rr)
        den_digits = len(str(sp.fraction(rr)[1]))
        print(f"{name} branch {br}: r-denominator digits {den_digits}, |e| digits {digs}")
