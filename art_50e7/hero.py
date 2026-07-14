"""HERO — 'The Bellows': Steffen's flexible polyhedron breathing.
Multiple-exposure ghost->blaze of the exact flex. Hue = frozen edge-length
class (the invariant IS the palette); brightness = exposure. Bellows volume
200.777 frozen to 13 digits; edges rigid to 1e-14 (verified separately)."""
import numpy as np, sys
from scipy.ndimage import gaussian_filter
from art_50e7.steffen_flex import config, EDGES
from art_50e7 import r3d

S = int(sys.argv[1]) if len(sys.argv)>1 else 1024
SS = 2
W = S*SS

# breath time-gradient palette: indigo(past) -> teal -> gold(rest) -> amber -> rose(future)
_CP=np.array([[0.22,0.24,0.62],[0.16,0.55,0.66],[1.00,0.80,0.42],
              [1.00,0.55,0.22],[0.95,0.30,0.42]])
def breath_col(u):  # u in [0,1]
    x=np.clip(u,0,1)*(len(_CP)-1); i=int(np.floor(x)); f=x-i
    i=min(i,len(_CP)-2); return _CP[i]*(1-f)+_CP[i+1]*f

# camera (angle chosen by AY,AX env for quick sweeps)
import os
AY=float(os.environ.get('AY',0.9)); AX=float(os.environ.get('AX',-0.5))
Rm = r3d.rot('y',AY)@r3d.rot('x',AX)
cam = r3d.Camera(W, Rm, cam_z=36.0, focal=2.05, center=(0,0,-0.95))

# flex frames with continuity
T=0.55
ts=np.linspace(-T,T,65)
frames=[]; prevV=None
for t in ts:
    V=config(t, prev={k+1:prevV[k] for k in range(9)} if prevV is not None else None)
    prevV=V; frames.append(V)

def kabsch(A,B):
    """Rotation R minimizing |R A - B| for centered A,B."""
    H=A.T@B; U,_,Vt=np.linalg.svd(H); d=np.sign(np.linalg.det(Vt.T@U.T))
    D=np.diag([1,1,d]); return (Vt.T@D@U.T)

# re-gauge: centroid-center every frame, align to mean shape (pure breathing)
frames=[V-V.mean(0) for V in frames]
mean=np.mean(frames,0)
for _ in range(3):
    frames=[ (kabsch(V,mean)@V.T).T for V in frames]
    mean=np.mean(frames,0)
cam.fit(frames, margin=0.82)

# breath ghosts: each exposure coloured by its flex phase (time gradient)
n=len(ts)
buf=np.zeros((W,W,3),np.float32)
for i,V in enumerate(frames):
    col=breath_col(i/(n-1))
    ec=np.repeat(col[None,:],len(EDGES),0)
    r3d.draw_edges(buf, cam, V, EDGES, ec, 0.28, samp=1.5, depthfade=0.6)

# blaze the rest frame as a stable GOLD skeleton (the frozen invariant moment),
# into its own buffer so we can FATTEN it to survive the downscale
from scipy.ndimage import gaussian_filter
skel=np.zeros((W,W,3),np.float32)
key=n//2
Vk=frames[key]
gold=np.repeat(np.array([[1.0,0.80,0.42]]),len(EDGES),0)
r3d.draw_edges(skel, cam, Vk, EDGES, gold, 2.7, samp=2.1, depthfade=0.62)
vcol=np.array([[1.0,0.97,0.9]]*9)
r3d.draw_verts(skel, cam, Vk, list(range(9)), vcol, [2.8*SS]*9, 3.0)
skel = skel + 0.85*gaussian_filter(skel,(1.1*SS,1.1*SS,0))   # widen the lines
buf += skel

bs=SS*S/1024.0   # scale bloom radii with resolution
img=r3d.bloom_tonemap(buf, k=1.7, gamma=0.85,
                      blooms=((1.5*bs,0.5),(5*bs,0.34),(16*bs,0.17),(46*bs,0.09)), sat=1.07)
# downscale
from PIL import Image
im=Image.fromarray(img).resize((S,S),Image.LANCZOS)
out='/home/user/claude-mythos-self-play/art_50e7/proto_hero.png' if S<3000 else '/home/user/claude-mythos-self-play/art_50e7/hero_bellows.png'
im.save(out)
print('saved',out,'at',S)
