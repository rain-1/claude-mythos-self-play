import sympy as sp, numpy as np, json
from mpmath import mp, mpf
mp.dps = 60
x, y = sp.symbols('x y', real=True)
t = x*y - 1; h = sp.expand(t*(x*t+1)); f = sp.expand((t**2+y)*(x*t+1)**2)
Pp = sp.expand(f+h)
Qq = sp.expand(-t**2 - 6*t*h*(h+1) - 170*f*h - 91*h**2 - 195*f*h**2 - 69*h**3 - 75*f*h**3 - sp.Rational(75,4)*h**4)
J = sp.expand(sp.diff(Pp,x)*sp.diff(Qq,y) - sp.diff(Pp,y)*sp.diff(Qq,x))
Jf = sp.lambdify((x,y), J, 'mpmath')
rng = np.random.default_rng(7)
out = {}
for scale in (1, 5, 20, 100, 500):
    lo = mpf('1e9')
    for _ in range(4000):
        a = mpf(float(rng.uniform(-scale, scale))); b = mpf(float(rng.uniform(-scale, scale)))
        v = Jf(a, b)
        if v < lo: lo = v
    out[str(scale)] = float(lo)
    print(f'|x|,|y| < {scale:5d}:  exact-arith min over 4000 samples = {float(lo):.6g}', flush=True)
# targeted: det J along the curves where it is small
json.dump(out, open('jcheck.json','w'), indent=1)
