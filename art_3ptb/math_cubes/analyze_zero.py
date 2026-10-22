import sympy as sp, sys
rows=[list(map(int,l.split())) for l in open('zeros7.txt')]
stats={}
for r in rows[:400]:
    A=r[0::2]; C=r[1::2]
    M=sp.Matrix([[a*a for a in A],[a*c for a,c in zip(A,C)],[c*c for c in C]])
    ker=M.nullspace()
    k=len(ker)
    u=sp.symbols('u0:%d'%k)
    B=sum((u[j]*ker[j] for j in range(k)), sp.zeros(6,1))
    QA=sp.expand(sum(A[i]*B[i]**2 for i in range(6)))
    QC=sp.expand(sum(C[i]*B[i]**2 for i in range(6)))
    # proportional?
    prop = sp.Matrix([[QA.coeff(m) if False else 0]]) 
    polyA=sp.Poly(QA,*u); polyC=sp.Poly(QC,*u)
    mons=set(polyA.monoms())|set(polyC.monoms())
    va=[polyA.coeff_monomial(m) for m in mons]; vc=[polyC.coeff_monomial(m) for m in mons]
    rk=sp.Matrix([va,vc]).rank()
    key=(k,rk)
    stats[key]=stats.get(key,0)+1
print(stats)
