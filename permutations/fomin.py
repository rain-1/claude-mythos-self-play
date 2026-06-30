from bisect import bisect_right

def rsk_shape(perm):
    P=[]
    for x in perm:
        r=0; v=x
        while True:
            if r==len(P): P.append([v]); break
            row=P[r]; j=bisect_right(row,v)
            if j==len(row): row.append(v); break
            row[j],v=v,row[j]; r+=1
    return tuple(len(r) for r in P)

def add_box(lam, r):
    l=list(lam)
    while len(l)<=r: l.append(0)
    l[r]+=1
    return tuple(x for x in l if x>0)

def diff_row(lam, mu):
    l=list(lam)+[0]*8; m=list(mu)+[0]*8
    for r in range(len(l)):
        if l[r]!=m[r]: return r
    return 0

def union(lam, rho):
    L=max(len(lam),len(rho)); l=list(lam)+[0]*L; r=list(rho)+[0]*L
    return tuple(max(l[i],r[i]) for i in range(L) if max(l[i],r[i])>0)

def local(mu, lam, rho, has_x):
    if has_x:                      # only valid when lam==rho==mu
        return add_box(mu,0)
    if lam==mu and rho==mu: return mu
    if lam!=mu and rho==mu: return lam
    if rho!=mu and lam==mu: return rho
    # both grew
    if lam!=rho: return union(lam,rho)
    k=diff_row(lam,mu)             # lam==rho grew in same row k
    return add_box(lam,k+1)

def growth(perm):
    n=len(perm)
    C=[[() for _ in range(n+1)] for _ in range(n+1)]   # C[i][j], i=position(col),j=value(row)
    for i in range(1,n+1):
        for j in range(1,n+1):
            mu=C[i-1][j-1]; lam=C[i-1][j]; rho=C[i][j-1]
            C[i][j]=local(mu,lam,rho, perm[i-1]==j)
    return C

if __name__=="__main__":
    from itertools import permutations
    bad=0; tot=0
    for n in range(1,8):
        for p in permutations(range(1,n+1)):
            C=growth(list(p)); tot+=1
            if C[n][n]!=rsk_shape(list(p)): bad+=1
    print(f"growth top-right corner == RSK shape on S1..S7: mismatches {bad}/{tot}")
