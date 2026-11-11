# The 5-cube: five schools, each the cyclic shift of the next (one of the 96 shift-invariant decompositions).
import sys, json, numpy as np, math
from PIL import Image
import koi, scene
W=int(sys.argv[1]); ss=int(sys.argv[2]); rep=int(sys.argv[3]); out=sys.argv[4]; wp=float(sys.argv[5]) if len(sys.argv)>5 else 0.8
J=json.load(open('../math_cube/solutions.json'))
C=J['d5_all_shift_invariant_orbit_reps'][rep]
if isinstance(C,dict): C=C.get('cycle',C.get('C'))
d=5; rho=lambda v:((v<<1)&31)|(v>>4)
cyc=[list(C)]
for k in range(4): cyc.append([rho(v) for v in cyc[-1]])
U=set()
for c in cyc:
    A={(c[k],c[(k+1)%32]) for k in range(32)}; assert len(A)==32 and not (U&A); U|=A
    assert all(bin(a^b).count('1')==1 for a,b in A)
assert len(U)==160
e=np.array([[math.cos(2*math.pi*k/5-math.pi/2),math.sin(2*math.pi*k/5-math.pi/2)] for k in range(5)])
pos=np.array([sum(e[k] for k in range(5) if (v>>k)&1)+np.zeros(2) for v in range(32)])
pos=np.where(np.linalg.norm(pos,axis=1,keepdims=True)>1e-9, pos, 0)
r=np.linalg.norm(pos,axis=1); R0=r.max()
pos=pos*np.where(r>1e-9,(np.maximum(r,1e-9)/R0)**(wp-1),1)[:,None]
pos[0]=(-0.125,0.0); pos[31]=(0.125,0.0)
sc=scene.build(pos,cyc,[0,1,4,3,2],seed=11,R=1.93,ppu=1/4.62,center=(0.5,0.447),flen=0.25,fw=0.025,fish_per_edge=float(sys.argv[6]) if len(sys.argv)>6 else 0.625,
               pad_r=0.088,delta=0.037,rin=0.17,trail_w=0.024,petals=60,ripples=7,straight=0.80)
img=koi.finish(koi.render(sc,W,W,ss=ss,strip=256,quiet=True))
Image.fromarray(img).save(out)
