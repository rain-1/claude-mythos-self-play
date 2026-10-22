from analyze import *
def queens(r):
    n=len(r)
    return len({r[j]+j for j in range(n)})==n and len({r[j]-j for j in range(n)})==n
def toroidal(r):
    n=len(r)
    return len({(r[j]+j)%n for j in range(n)})==n and len({(r[j]-j)%n for j in range(n)})==n
for n in range(1,14):
    S=[tuple(map(int,l.split())) for l in open(f'sols_{n}.txt')]
    strong=sum(all(queens([(k-x)%n for x in q]) for k in range(n)) for q in S)
    tor=sum(toroidal([(-x)%n for x in q]) for q in S)
    print(n,len(S),'every-layer-queens',strong,'toroidal',tor)
