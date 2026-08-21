# 2*seed on E -> r -> (a,b,c,d,e), exact verification.  Calibrates hhat -> size(e).
import sympy as sp, json
from sympy import Rational as R
d = json.load(open('curve_model.json'))
def gr(v): return R(int(v[0]), int(v[1]))
r1 = gr(d['r1']); q = gr(d['q'])
a4,a3,a2,a1,a0 = [gr(v) for v in d['quart']]
A3,A2,A1,A0 = [gr(v) for v in d['Delta']]
ll = int(d['l']); e2,e4,e6 = [sp.Integer(v) for v in d['E']]
xS, yS = gr(d['seed'][0]), gr(d['seed'][1])

def ell_double(x, y):
    lam = (3*x**2 + 2*e2*x + e4) / (2*y)
    x3 = lam**2 - e2 - 2*x
    y3 = lam*(x - x3) - y
    return x3, y3

def to_r(xE, yE, branch=+1):
    t = xE/(A3*ll**2); Y = branch*yE/(A3*ll**3)
    c2 = 2*q*t - (a2 - a3**2/(4*q**2)); c1 = a3*t/q - a1
    w = (-c1 + Y)/(2*c2)
    return r1 + 1/w

def solution_from_r(r):
    # poster's maps (k=3 family)
    p = R(-1488,13355) - R(5511,13355)*(48044056139 + 1242748*r)/(r**2 - 6190029774)
    D2 = -(18958669594580211381729967107 + 1093490321304049798772416*r
           + 15172317493269316128*r**2 + 3306770731944*r**3 + 35534992*r**4)
    D = sp.sqrt(D2)
    assert D.is_rational, "D not rational!"
    qq = 3*D/(13355*(r**2 - 6190029774))
    sols = []
    for sgn in (+1, -1):
        qs = sgn*qq
        x = (p+qs)/2; y = (p-qs)/2
        z = 3 + (R(2,1837) - 1)*(3 + p)
        lhs = 1 + x**4 + y**4 + z**4
        rhs = (1 + 27*(x+y+z))**4
        ok = sp.nsimplify(lhs - rhs) == 0
        l = sp.lcm([sp.fraction(v)[1] for v in (x,y,z)])
        a,b,c,dd = sp.Integer(l), sp.Integer(l*x), sp.Integer(l*y), sp.Integer(l*z)
        e = a + 27*(b+c+dd)
        g = sp.gcd(sp.gcd(sp.gcd(a,b), sp.gcd(c,dd)), e)
        a,b,c,dd,e = [v//g for v in (a,b,c,dd,e)]
        assert a**4+b**4+c**4+dd**4 == e**4, "quartic identity FAILS"
        sols.append((ok,(a,b,c,dd,e)))
    return sols

# sanity: seed itself
r_check = [v for v in (to_r(xS, yS, +1), to_r(xS, yS, -1)) if getattr(v,'is_rational',False)]
print("seed roundtrip r values:", r_check)
for rr in r_check:
    for ok,(a,b,c,dd,e) in solution_from_r(rr):
        print("  identity ok:", ok, " (a,b,c,d,e) digits:", [len(str(abs(v))) for v in (a,b,c,dd,e)], " e =", e if len(str(e))<25 else str(e)[:20]+"...")

x2, y2 = ell_double(xS, yS)
print("2*seed computed")
for br in (+1,-1):
    r2 = to_r(x2, y2, br)
    if not getattr(r2,'is_rational',False): print("branch",br,"degenerate"); continue
    print("branch", br, " r height digits:", len(str(sp.fraction(r2)[0])), "/", len(str(sp.fraction(r2)[1])))
    for ok,(a,b,c,dd,e) in solution_from_r(r2):
        print("  identity ok:", ok, " digits of (a,b,c,d,e):", [len(str(abs(v))) for v in (a,b,c,dd,e)])
