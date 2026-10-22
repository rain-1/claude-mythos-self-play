import sympy as sp
rows=[list(map(int,l.split())) for l in open('zeros7.txt')]
for r in rows[:5]:
    A=r[0::2]; C=r[1::2]
    M=sp.Matrix([[a*a for a in A],[a*c for a,c in zip(A,C)],[c*c for c in C]])
    ker=M.nullspace(); k=len(ker)
    u=sp.symbols('u0:%d'%k)
    B=sum((u[j]*ker[j] for j in range(k)), sp.zeros(6,1))
    QA=sp.factor(sum(A[i]*B[i]**2 for i in range(6)))
    QC=sp.factor(sum(C[i]*B[i]**2 for i in range(6)))
    print(list(zip(A,C)), k, '\n  QA=',QA,'\n  QC=',QC, '\n  ker=',[list(v) for v in ker])
