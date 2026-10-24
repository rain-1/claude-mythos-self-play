# Small-alpha expansion of eta(alpha) = E log Y, Y = phi + sum_k alpha^k y_k (stationary).
# Stationary moments of the y_k are obtained by solving the linear moment equations exactly in Q(sqrt5).
import sympy as sp, itertools, sys
K = int(sys.argv[1]) if len(sys.argv)>1 else 4
al, s, t = sp.symbols('alpha s t')
phi = (1+sp.sqrt(5))/2
ys = sp.symbols('y1:%d'%(K+1))
Y = phi + sum(al**(k+1)*ys[k] for k in range(K))
Ynew = sp.series((1+al*s) + (1+al*t)/Y, al, 0, K+1).removeO()
Ynew = sp.expand(Ynew)
yp = [sp.expand(Ynew.coeff(al, k+1)) for k in range(K)]   # y_k' as polynomial in y, s, t
L = sp.expand(sp.series(sp.log(Y), al, 0, K+1).removeO())
# monomials in y with weight <= K
def monos(K):
    out=[]
    for e in itertools.product(*[range(K//(k+1)+1) for k in range(K)]):
        w = sum((k+1)*e[k] for k in range(K))
        if 1 <= w <= K: out.append(e)
    return out
ms = monos(K)
M = {e: sp.Symbol('M_'+'_'.join(map(str,e))) for e in ms}
def mono(e): return sp.Mul(*[ys[k]**e[k] for k in range(K)])
def Enoise(expr):
    # s,t independent +-1 symmetric; independent of y
    p = sp.Poly(expr, s, t)
    r = 0
    for (i,j), c in p.terms():
        if i%2==0 and j%2==0: r += c
    return sp.expand(r)
def Ey(expr):
    p = sp.Poly(sp.expand(expr), *ys)
    r = 0
    for e, c in p.terms():
        r += c*(1 if sum(e)==0 else M[tuple(e)])
    return r
eqs = []
for e in ms:
    img = sp.expand(sp.Mul(*[yp[k]**e[k] for k in range(K)]))
    eqs.append(sp.Eq(M[e], Ey(Enoise(img))))
sol = sp.solve(eqs, list(M.values()), dict=True)[0]
cs = {}
for k in range(1, K+1):
    ck = sp.nsimplify(sp.radsimp(sp.simplify(Ey(L.coeff(al,k)).subs(sol))))
    ck = sp.radsimp(sp.simplify(ck))
    cs[k] = ck
    print(k, ck, sp.N(ck, 20))
