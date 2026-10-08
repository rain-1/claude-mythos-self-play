# Tree of chains a0=1, a_{n+1} = a_n * s_b(a_{n+1}) (MO 515823, OEIS A114440 for base 10).
# Children of a: all k>1 with s_b(a*k) == k.  s_b(m) <= (b-1)*ndigits(m) bounds k.
import sys, json, gmpy2
from gmpy2 import mpz
_V={ord(c):i for i,c in enumerate('0123456789abcdefghijklmnopqrstuvwxyz')}
def s(m,b):
    t=gmpy2.digits(m,b).encode()
    if b<=10: return sum(t)-48*len(t)
    return sum(_V[c] for c in t)
def children(a,b):
    nd=len(gmpy2.digits(a,b))
    K=(b-1)*(nd+4)
    am=(a-1)%(b-1)
    return [k for k in range(2,K+1) if (k*am)%(b-1)==0 and s(a*k,b)==k]
def tree(b,cap=200000):
    nodes=[(mpz(1),-1,0,1)]  # value,parent,depth,k
    i=0
    while i<len(nodes) and len(nodes)<cap:
        a,_,d,_=nodes[i]
        for k in children(a,b): nodes.append((a*k,i,d+1,k))
        i+=1
    return nodes, i>=len(nodes)
if __name__=="__main__":
    bases=[int(x) for x in sys.argv[1:]] or range(2,17)
    for b in bases:
        T,done=tree(b); D=max(n[2] for n in T)
        lv=[0]*(D+1)
        for n in T: lv[n[2]]+=1
        print(b,len(T),'finished' if done else 'CAPPED','depth',D,'levels',lv[:40],flush=True)
        json.dump([(str(v),p,d,k) for v,p,d,k in T],open(f'tree{b}.json','w'))
