import sys, math
def square(q):
    n=len(q); return [[(i+q[j])%n for j in range(n)] for i in range(n)]
def incremental(L):
    n=len(L)
    for key in (lambda i,j:i+j, lambda i,j:i-j):
        h={}
        for i in range(n):
            for j in range(n):
                h.setdefault(key(i,j),[0]*n)[L[i][j]]+=1
        for d,hist in h.items():
            c=0
            for k in range(n):
                c+=hist[k]
                if c>k+1: return False
    return True
def D4(L):
    n=len(L); R=range(n)
    maps={'id':lambda i,j:(i,j),'colrev':lambda i,j:(i,n-1-j),'rowrev':lambda i,j:(n-1-i,j),
          'rot180':lambda i,j:(n-1-i,n-1-j),'transpose':lambda i,j:(j,i),'antitr':lambda i,j:(n-1-j,n-1-i),
          'rot90':lambda i,j:(n-1-j,i),'rot270':lambda i,j:(j,n-1-i)}
    return {k:[[L[f(i,j)[0]][f(i,j)[1]] for j in R] for i in R] for k,f in maps.items()}
def as_cyclic(L):
    n=len(L); q=L[0]
    if all(L[i][j]==(i+q[j])%n for i in range(n) for j in range(n)): return tuple(q)
    return None
def linear(q):
    n=len(q); a=(q[1]-q[0])%n if n>1 else 0
    return all(q[j]==(a*j+q[0])%n for j in range(n))
if __name__=='__main__':
    for n in range(1,int(sys.argv[1])+1):
        S=[tuple(map(int,l.split())) for l in open(f'sols_{n}.txt')]
        Sset=set(S)
        lin=[q for q in S if linear(q)]
        closed={}
        orbits=set()
        for q in S:
            imgs=D4(square(q)); orb=[]
            for g,M in imgs.items():
                c=as_cyclic(M)
                closed.setdefault(g,0)
                if c is not None:
                    assert c in Sset; closed[g]+=1; orb.append(c)
            orbits.add(min(orb))
        print(n,len(S),'linear',len(lin),'orbits',len(orbits),'g->cyclic:',{g:v for g,v in closed.items() if v})
