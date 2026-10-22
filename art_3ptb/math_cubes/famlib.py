from math import gcd
def int_kernel(M, n):
    # M: list of rows (ints), n columns. Return integer basis of {v in Z^n: M v = 0} via column HNF.
    m=len(M)
    A=[row[:] for row in M]
    U=[[1 if i==j else 0 for j in range(n)] for i in range(n)]  # columns ops tracked: U columns
    def colop_swap(i,j):
        for r in A: r[i],r[j]=r[j],r[i]
        for r in U: r[i],r[j]=r[j],r[i]
    def colop_add(i,j,c): # col i += c*col j
        for r in A: r[i]+=c*r[j]
        for r in U: r[i]+=c*r[j]
    piv=0
    for r in range(m):
        if piv>=n: break
        while True:
            nz=[c for c in range(piv,n) if A[r][c]!=0]
            if not nz: break
            c0=min(nz,key=lambda c:abs(A[r][c]))
            colop_swap(piv,c0)
            done=True
            for c in range(piv+1,n):
                if A[r][c]:
                    q=A[r][c]//A[r][piv]
                    colop_add(c,piv,-q)
                    if A[r][c]: done=False
            if done: break
        if any(A[r][c] for c in range(piv,n)) and A[r][piv]!=0: piv+=1
    return [[U[i][c] for i in range(n)] for c in range(piv,n)]

