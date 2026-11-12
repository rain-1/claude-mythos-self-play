"""Machine checks for PROOF.md (MO 514916).
 (a) the 16 four-step maps z = c - 4*E*w  (digit table) reproduce D_{k+4} from D_k;
 (b) base case of Theorem A: missing points of D_7 with |z| < 4 are exactly -3 and -3+i;
 (c) Theorem A itself against brute force for j = 1..5 (k = 7, 11, 15, 19, 23);
 (d) the closed form for k = 1..24 (covers the small cases k <= 7 used in the proof)."""
import numpy as np, itertools
B=1+1j
def dragon_set(k):
    x=np.zeros(1,np.int64); y=np.zeros(1,np.int64)
    for _ in range(k):
        bx=x-y; by=x+y; x=np.concatenate([bx,1-bx]); y=np.concatenate([by,-by])
    return x,y
def closed(k):
    if k<2: return 1
    j=(k-2)//4; r=(k-2)%4; u=(2**(2*j+1)+1)//3
    return [(u*u+1)//2,u*u,2*u*u,4*u*u][r]
# (a) digit table
table=[]
for d in itertools.product((0,1),repeat=4):
    c=0; E=1; p=1
    for di in d:
        c+=E*p*di; E*=(1-2*di); p*=B
    table.append((complex(c),E))
    assert abs(p-(-4))<1e-12
print('digit table (c, E):',[(int(c.real),int(c.imag),E) for c,E in table])
assert all(c.real>=0 for c,E in table if E==1), 'E=+ maps must have Re c >= 0'
assert sorted((int(c.real),int(c.imag)) for c,E in table if E==-1 and c.real>0)==[(1,0),(1,1)]
assert max(abs(c) for c,E in table)<4
for k in (3,5,8):
    x,y=dragon_set(k); S={complex(a,b) for a,b in zip(x.tolist(),y.tolist())}
    x2,y2=dragon_set(k+4); S2={complex(a,b) for a,b in zip(x2.tolist(),y2.tolist())}
    img={c-4*E*w for c,E in table for w in S}
    assert img==S2 and len(S2)==2**(k+4)
print('(a) four-step maps reproduce D_{k+4}: ok')
def missing_within(k,R):
    x,y=dragon_set(k); W=int(R)+2
    g=np.zeros((2*W+1,2*W+1),bool); m=(abs(x)<=W)&(abs(y)<=W); g[y[m]+W,x[m]+W]=True
    out=[]
    for a in range(-W,W+1):
        for b in range(-W,W+1):
            if not g[b+W,a+W] and a*a+b*b<R*R: out.append((a,b))
    return sorted(out)
print('(b) missing points of D_7 with |z|<4:',missing_within(7,4)); assert missing_within(7,4)==[(-3,0),(-3,1)]
def moser(limit):
    Y=[0]; p=1
    while p<=limit:
        Y+= [v+p for v in Y]; p*=4
    return {v for v in Y if v<=limit}
for j in range(1,6):
    k=4*j+3; u=(2**(2*j+1)+1)//3; got=missing_within(k,u+1)
    want=sorted((-u,yv) for yv in moser(2*u) if u*u+yv*yv<(u+1)**2)
    assert got==want,(k,got,want)
    print(f'(c) k={k}: missing points with |z|<u+1 = (-u, y), y in',[b for a,b in got])
for k in range(1,25):
    x,y=dragon_set(k); R=int(closed(k)**.5)+3
    g=np.zeros((2*R+1,2*R+1),bool); m=(abs(x)<=R)&(abs(y)<=R); g[y[m]+R,x[m]+R]=True
    yy,xx=np.nonzero(~g); assert int(((xx-R)**2+(yy-R)**2).min())==closed(k)
print('(d) closed form, k=1..24: ok')
