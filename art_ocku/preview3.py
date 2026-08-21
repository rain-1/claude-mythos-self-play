import numpy as np, pickle
from PIL import Image
M, states, PR, PG = pickle.load(open('field400.pkl','rb'))
PB = 1 - PR - PG
idx = {s:i for i,s in enumerate(states)}
# C3 symmetry check: P_R(r,b,g) == P_B(b,g,r)?  (relabel sigma: R->B,B->G,G->R)
# under sigma, state (r,b,g) with counts of R,B,G becomes state with R'=? :
# new color of old R individuals is B: so (r',b',g') = (g, r, b)?? test both.
errs1=[]; errs2=[]
import random
random.seed(1)
for _ in range(200):
    r = random.randint(1,M-2); b = random.randint(1, M-1-r)
    g = M-r-b
    if g<1: continue
    k = idx[(r,b)]
    # candidate 1: P_R(r,b,g) == P_B evaluated at (r',b') = (b,g) i.e. state (b,g,r)
    if (b,g) in idx: errs1.append(abs(PB[idx[(b,g)]] - PR[k]))
    # candidate 2: state (g,r,b)
    if (g,r) in idx: errs2.append(abs(PB[idx[(g,r)]] - PR[k]))
print("C3 check: cand1 max err %.2e   cand2 max err %.2e" % (max(errs1), max(errs2)))
# mirror asymmetry magnitude: P_R(r,b,g) vs P_R(b,r,g) with g fixed... mirror swaps two colors, say R<->B:
mm=[]
for _ in range(200):
    r = random.randint(1,M-2); b = random.randint(1, M-1-r); g=M-r-b
    if g<1 or (b,r) not in idx: continue
    mm.append(abs(PR[idx[(b,r)]] - PB[idx[(r,b)]]))
print("mirror (swap R,B) max |P_R(b,r,g)-P_B(r,b,g)| =", max(mm))

# log-deviation render
S=1000
vR=np.array([S/2,0.06*S]); vG=np.array([0.05*S,0.95*S]); vB=np.array([0.95*S,0.95*S])
pts=np.array([((r/M)*vR+((M-r-b)/M)*vG+(b/M)*vB) for (r,b) in states])
D = np.stack([PR-1/3, PG-1/3, PB-1/3],1)
mag = np.linalg.norm(D,axis=1)
# 2-plane coords: e1 = (cR direction) — use standard simplex basis
e1 = np.array([1,-0.5,-0.5])/np.sqrt(1.5); e2 = np.array([0,1,-1])/np.sqrt(2)
u = D@e1; v = D@e2
ang = np.arctan2(v,u)
L = np.clip((np.log10(mag+1e-16)+14)/14, 0, 1)   # 1e-14..1 -> 0..1
import colorsys
img=np.zeros((S,S,3),np.float32); cnt=np.zeros((S,S),np.float32)
hue = (ang/(2*np.pi))%1.0
cols = np.array([colorsys.hsv_to_rgb(h, 0.85, 1.0) for h in hue])
xi=np.clip(pts[:,0].astype(int),0,S-1); yi=np.clip(pts[:,1].astype(int),0,S-1)
for c in range(3):
    np.add.at(img[:,:,c],(yi,xi),cols[:,c]*(L**1.5))
np.add.at(cnt,(yi,xi),1)
m=cnt>0; img[m]/=cnt[m][:,None]
Image.fromarray((np.clip(img,0,1)**0.85*255).astype(np.uint8)).save('preview_logdev.png')
print("saved preview_logdev.png; mag range %.2e .. %.2e" % (mag.min(), mag.max()))
