import sympy as sp, numpy as np
x=sp.symbols('x')
f=x**3-x**2-3*x+1
print("=== VERIFICATION: newly-reducible cubic f = x^3 - x^2 - 3x + 1 ===")
print("[1] f irreducible over Q:", sp.Poly(f,x).is_irreducible)
print("[2] discriminant:", sp.discriminant(sp.Poly(f,x)), "(=148, not a square -> Galois group S3)")
G=sp.Poly(f,x).galois_group(); print("    Galois group order:", G[0].order())
print("[3] iterate factorization  f^n = product of irreducibles, degrees:")
fn=f
for n in range(1,6):
    if n>1: fn=sp.expand(fn.subs(x,f))
    fl=sp.factor_list(fn)[1]
    degs=sorted(sp.Poly(g,x).degree() for g,m in fl for _ in range(m))
    exp=[3**(n-1)] if n==1 else [3**(n-1),2*3**(n-1)]
    print(f"    f^{n}: degrees {degs}   expected {sorted(exp)}   MATCH={sorted(degs)==sorted(exp)}   (#factors {len(fl)})")
# [4] roots of f^n == preimage tree f^{-n}(0)
def preim(z): return np.roots([1.0,-1.0,-3.0,(1.0-z)])
lvl=[0j]
for _ in range(3):
    lvl=[w for z in lvl for w in preim(z)]
tree=np.sort_complex(np.array(lvl))
f3=f
for _ in range(2): f3=sp.expand(f3.subs(x,f))
polyroots=np.sort_complex(np.array([complex(r) for r in np.roots([float(c) for c in sp.Poly(f3,x).all_coeffs()])]))
print("[4] roots(f^3) == f^{-3}(0) preimage tree:",
      np.allclose(np.sort(tree.real),np.sort(polyroots.real),atol=1e-6), "(max dev %.2e)"%np.max(np.abs(np.sort(tree.real)-np.sort(polyroots.real))))
# [5] A-basin (cubic factor at level2) is a Galois transversal: one preimage per root of f
cub=np.sort(np.roots([1,0,-4,-2]).real)
rf=np.roots([1,-1,-3,1])
per_parent=[]
for r in rf:
    pr=preim(r).real
    per_parent.append(sum(np.min(np.abs(cub-p))<1e-4 for p in pr))
print("[5] A-factor picks exactly one preimage from each of f's 3 roots:",
      per_parent, "-> transversal:", all(c==1 for c in per_parent))
# [6] pinch critical values of f^2 (for the watershed)
critf=np.roots([9,-6,-3]); crit2=list(critf)
for c in critf: crit2+=list(preim(c))
crit2=np.array([c for c in crit2 if abs(c.imag)<1e-6]).real
cv=np.unique(np.round(np.abs(f(f(crit2+0j)) if False else np.array([complex(v)**3-complex(v)**2-3*complex(v)+1 for v in [complex(w)**3-complex(w)**2-3*complex(w)+1 for w in crit2]])),4))
print("[6] critical (pinch) values |f^2(crit)|:", cv)
