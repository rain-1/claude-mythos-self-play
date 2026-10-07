"""Eisenstein-integer arithmetic for the quasi-RH pictures.
n = a + b*w, w = e^{2 pi i/3}, N(n) = a^2 - a b + b^2. primary: n = 1 mod 3  <=>  a = 1, b = 0 (mod 3).
Sextic residue symbol (u/p)_6 for primary primes p (split: O/p = F_p; inert p=-q: O/p = F_{q^2}),
extended multiplicatively to squarefree primary n. Normalized cubic Gauss sums gamma_2(p) with the paper's
additive character e(z) = exp(4 pi i Im z / sqrt3)."""
import numpy as np, math
from functools import lru_cache
W=complex(-0.5,math.sqrt(3)/2)
Z6=[np.exp(2j*np.pi*k/6) for k in range(6)]
def norm(a,b): return a*a-a*b+b*b
def mulw(a,b): return (-b,a-b)            # w*(a+bw)
def conj(a,b): return (a-b,-b)            # conj(a+bw) = (a-b) - b w
def tocx(a,b): return a+b*W
def primary(a,b):
    cands=[(a,b)]
    x,y=a,b
    for k in range(5):
        x,y=mulw(x,y); cands.append((x,y))
    for (x,y) in cands+[(-x,-y) for (x,y) in cands]:
        if (x-1)%3==0 and y%3==0: return (x,y)
    return None
def rational_primes(M):
    s=np.ones(M+1,bool); s[:2]=False
    for i in range(2,int(M**0.5)+1):
        if s[i]: s[i*i::i]=False
    return np.nonzero(s)[0]
def split_prime(p):
    """primary pi with N(pi)=p, p = 1 mod 3; returns (a,b)."""
    for b in range(0,int(math.isqrt(4*p//3))+2):
        d=4*p-3*b*b
        if d<0: break
        r=math.isqrt(d)
        if r*r==d and (r+b)%2==0:
            a=(r+b)//2
            if norm(a,b)==p: return primary(a,b)
    raise ValueError(p)
def eisenstein_primes(D):
    """all primary primes with norm <= D: list of (a,b,norm,kind) kind 's' split, 'i' inert (p=-q, norm q^2)."""
    out=[]
    for p in rational_primes(D):
        p=int(p)
        if p==3: continue
        if p%3==1:
            a,b=split_prime(p); c=primary(*conj(a,b)); out.append((a,b,p,'s')); out.append((c[0],c[1],p,'s'))
        elif p*p<=D:
            out.append((-p,0,p*p,'i'))
    out.sort(key=lambda t:t[2]); return out
def divides(pa,pb,na,nb):
    """does pi=(pa,pb) divide n=(na,nb)? n*conj(pi)/N(pi) integral?"""
    ca,cb=conj(pa,pb); P=norm(pa,pb)
    # (na+nb w)(ca+cb w) = (na ca - nb cb) + (na cb + nb ca - nb cb) w
    x=na*ca-nb*cb; y=na*cb+nb*ca-nb*cb
    return x%P==0 and y%P==0
def divide(pa,pb,na,nb):
    ca,cb=conj(pa,pb); P=norm(pa,pb); x=na*ca-nb*cb; y=na*cb+nb*ca-nb*cb; return (x//P,y//P)
def factor(a,b,primes_by_p):
    """factor n (coprime to 3 not required) into primary primes: dict {(pa,pb):e}; lam=(1-w) counted under key (1,-1)."""
    N=norm(a,b); f={}
    # rational factorization of N
    m=N; p=2; rp=[]
    while p*p<=m:
        if m%p==0:
            e=0
            while m%p==0: m//=p; e+=1
            rp.append((p,e))
        p+=1
    if m>1: rp.append((m,1))
    for p,e in rp:
        if p==3:
            f[(1,-1)]=e
        elif p%3==2:
            f[(-p,0)]=e//2
        else:
            for (pa,pb) in primes_by_p[p]:
                k=0; x,y=a,b
                while divides(pa,pb,x,y): x,y=divide(pa,pb,x,y); k+=1
                if k: f[(pa,pb)]=k
    return f
# ---- residue symbols ----
def cube_root_mod(p):
    """w mod p: a root of w^2+w+1 = 0 mod p (p = 1 mod 3)."""
    for g in range(2,p):
        r=pow(g,(p-1)//3,p)
        if r!=1 and (r*r+r+1)%p==0: return r
    raise ValueError
def omega_image(pa,pb,p):
    """the w mod p with pi | (w - omega): identify O/pi = F_p via omega -> w."""
    r=cube_root_mod(p)
    for w in (r,(-1-r)%p):
        # w - omega = w + 0*? : element (w, -1): is it divisible by pi?
        if divides(pa,pb,w,-1): return w
    raise ValueError
def root6_index_split(r,p,w):
    """r in F_p a sixth root of unity; return k with r = zeta_6^k, where omega -> w. zeta_6 = -omega^2 = 1+omega."""
    table={1:0, (1+w)%p:1, w%p:2, (p-1):3, (p-1-w)%p:4, (p-w)%p:5}   # zeta6^2=omega, ^3=-1, ^4=omega^2=-1-w, ^5=-omega
    return table[r%p]
def pow_fq2(a,b,e,q):
    """(a+bw)^e in F_q[w]/(w^2+w+1)."""
    ra,rb=1,0; xa,xb=a%q,b%q
    while e:
        if e&1: ra,rb=(ra*xa-rb*xb)%q,(ra*xb+rb*xa-rb*xb)%q
        xa,xb=(xa*xa-xb*xb)%q,(2*xa*xb-xb*xb)%q; e>>=1
    return ra,rb
def root6_index_inert(ra,rb,q):
    table={(1,0):0,(1,1):1,(0,1):2,(q-1,0):3,(q-1,q-1):4,(0,q-1):5}
    return table[(ra%q,rb%q)]
class Sextic:
    """(u/p)_6 for a primary prime p, for many u."""
    def __init__(self,pa,pb,kind):
        self.pa,self.pb,self.kind=pa,pb,kind; self.N=norm(pa,pb)
        if kind=='s': self.w=omega_image(pa,pb,self.N)
    def sym(self,ua,ub):
        """index k in 0..5 (value zeta6^k) or -1 for zero."""
        if self.kind=='s':
            p=self.N; r=(ua+ub*self.w)%p
            if r==0: return -1
            return root6_index_split(pow(r,(p-1)//6,p),p,self.w)
        q=-self.pa
        if ua%q==0 and ub%q==0: return -1
        ra,rb=pow_fq2(ua,ub,(q*q-1)//6,q); return root6_index_inert(ra,rb,q)
# ---- cubic Gauss sums gamma_2(pi) for split primary primes ----
def gamma2_split(pa,pb,p,w):
    """gamma_2(pi) = p^{-1/2} sum_{x mod pi} chi_pi(x)^2 e(x/pi), e(z)=exp(4 pi i Im z/sqrt3), x = 0..p-1 integers."""
    x=np.arange(1,p)
    r=pow_mod_array(x,(p-1)//3,p)                # cube residue character values in F_p: 1, w, -1-w
    chi=np.where(r==1,0,np.where(r==w%p,1,2))    # omega^j, j in {0,1,2}
    phase=np.exp(2j*np.pi*chi/3)
    # e(x/pi): Im(x/pi) = x Im(conj pi)/p = -x b sqrt3/(2p) -> e = exp(-2 pi i b x/p)
    add=np.exp(-2j*np.pi*((pb*x)%p)/p)
    return np.sum(phase*add)/math.sqrt(p)
def pow_mod_array(x,e,p):
    r=np.ones_like(x); b=x.copy()
    while e:
        if e&1: r=(r*b)%p
        b=(b*b)%p; e>>=1
    return r
if __name__=="__main__":
    # sanity: Lemma 4.2  gamma_2(p)^3 = -alpha(p) = -p/|p|
    for p in (7,13,19,31,97,1009,10009):
        a,b=split_prime(p); w=omega_image(a,b,p); g=gamma2_split(a,b,p,w)
        al=tocx(a,b)/abs(tocx(a,b)); print(p,(a,b),'|g|=%.6f'%abs(g),'g^3 + alpha =',abs(g**3+al))
    # sextic symbol multiplicativity / sanity: (u/p)_6^3 = quadratic symbol
    S=Sextic(*split_prime(13),'s'); print([S.sym(u,0) for u in range(1,13)])
    S=Sextic(-5,0,'i'); print([S.sym(u,v) for u in range(0,5) for v in range(0,5)][:12])
