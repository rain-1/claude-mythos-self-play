"""Binary Lambda Calculus core: de Bruijn lambda terms, BLC encode/decode, normal-order
beta reduction.  BLC encoding (John Tromp):
    Var i        -> '1'*(i+1) + '0'
    Lam body     -> '00' + enc(body)
    App f a      -> '01' + enc(f) + enc(a)
Every closed term <-> a bitstring; the universal prior weight of a program p is 2**-|p|.
"""
import sys
sys.setrecursionlimit(100000)

# term = ('V', i) | ('L', body) | ('A', f, a)
def V(i): return ('V', i)
def L(b): return ('L', b)
def A(f, a): return ('A', f, a)

def enc(t):
    if t[0]=='V': return '1'*(t[1]+1)+'0'
    if t[0]=='L': return '00'+enc(t[1])
    return '01'+enc(t[1])+enc(t[2])

def dec(bits, i=0):
    if bits[i:i+2]=='00':
        b,i=dec(bits,i+2); return L(b),i
    if bits[i:i+2]=='01':
        f,i=dec(bits,i+2); a,i=dec(bits,i); return A(f,a),i
    j=i
    while bits[j]=='1': j+=1
    return V(j-i-1), j+1            # ones then a 0

def decode(bits):
    t,i=dec(bits,0); return t

def size(t):
    if t[0]=='V': return 1
    if t[0]=='L': return 1+size(t[1])
    return 1+size(t[1])+size(t[2])

# ---- beta reduction (de Bruijn) ----
def shift(t,d,c=0):
    if t[0]=='V': return V(t[1]+d) if t[1]>=c else t
    if t[0]=='L': return L(shift(t[1],d,c+1))
    return A(shift(t[1],d,c),shift(t[2],d,c))

def subst(t,j,s):
    if t[0]=='V':
        if t[1]==j: return s
        return t
    if t[0]=='L': return L(subst(t[1],j+1,shift(s,1)))
    return A(subst(t[1],j,s),subst(t[2],j,s))

def beta(app):  # app = A(L(b), x)
    b=app[1][1]; x=app[2]
    return shift(subst(b,0,shift(x,1)),-1)

def step(t):  # one normal-order (leftmost-outermost) beta step; None if normal form
    if t[0]=='V': return None
    if t[0]=='L':
        s=step(t[1]); return L(s) if s else None
    # App
    if t[1][0]=='L':
        return beta(t)
    s=step(t[1])
    if s: return A(s,t[2])
    s=step(t[2])
    if s: return A(t[1],s)
    return None

def normalize(t,maxsteps=100000):
    n=0; seq=[t]
    while n<maxsteps:
        s=step(t)
        if s is None: break
        t=s; n+=1; seq.append(t)
    return t,n,seq

# ---- handy terms ----
I=L(V(0))
K=L(L(V(1)))
S=L(L(L(A(A(V(2),V(0)),A(V(1),V(0))))))
Omega=A(L(A(V(0),V(0))),L(A(V(0),V(0))))
def church(n):
    body=V(0)
    for _ in range(n): body=A(V(1),body)
    return L(L(body))
SUCC=L(L(L(A(V(1),A(A(V(2),V(1)),V(0))))))   # succ = λn.λf.λx. f (n f x)
PLUS=L(L(L(L(A(A(V(3),V(1)),A(A(V(2),V(1)),V(0)))))))

if __name__=="__main__":
    # round-trip + reduction sanity
    for name,t in [("I",I),("K",K),("S",S),("c0",church(0)),("c1",church(1)),("c2",church(2)),("c3",church(3))]:
        b=enc(t); assert decode(b)==t, name
        print(f"{name:4} size={size(t):2} |bits|={len(b):2}  {b}")
    # 2+1 = 3 ?
    t=A(A(PLUS,church(2)),church(1))
    nf,n,_=normalize(t)
    print("PLUS 2 1 ->",("c3" if nf==church(3) else nf),"in",n,"steps")
    # SUCC c2 = c3
    nf,n,_=normalize(A(SUCC,church(2)))
    print("SUCC c2 ->",("c3" if nf==church(3) else "?"),"in",n,"steps")
    print("|self bits| check: enc(S) decodes back:",decode(enc(S))==S)
