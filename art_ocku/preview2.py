import numpy as np
from chameleon import solve_triangle
from PIL import Image
import pickle

M = 400
states, idx, PR, PG = solve_triangle(M)
PB = 1 - PR - PG
pickle.dump((M, states, PR, PG), open('field400.pkl','wb'))
# sample some interior lines
for (r,b) in [(133,133),(100,150),(200,100),(50,50),(20,300),(300,20)]:
    k = idx[(r,b)]
    print(f"(r,b,g)=({r},{b},{400-r-b}): PR={PR[k]:.4f} PG={PG[k]:.4f} PB={PB[k]:.4f}")
# deviation render
S = 800
dev = np.zeros((S,S,3), np.float32); cnt = np.zeros((S,S), np.float32)
vR = np.array([S/2, 0.08*S]); vG = np.array([0.06*S, 0.94*S]); vB = np.array([0.94*S, 0.94*S])
pts = np.array([((r/M)*vR + ((M-r-b)/M)*vG + (b/M)*vB) for (r,b) in states])
xi=np.clip(pts[:,0].astype(int),0,S-1); yi=np.clip(pts[:,1].astype(int),0,S-1)
D = np.stack([PR-1/3, PG-1/3, PB-1/3], 1)
for c in range(3):
    np.add.at(dev[:,:,c], (yi,xi), D[:,c])
np.add.at(cnt,(yi,xi),1)
m = cnt>0; dev[m] /= cnt[m][:,None]
amp = 6.0
cR=np.array([1,0.3,0.18]); cG=np.array([0.25,1,0.45]); cB=np.array([0.25,0.55,1])
img = np.clip(dev[:,:,0:1]*amp,0,1)*cR + np.clip(dev[:,:,1:2]*amp,0,1)*cG + np.clip(dev[:,:,2:3]*amp,0,1)*cB
img[~m]=0
Image.fromarray((np.clip(img,0,1)**0.8*255).astype(np.uint8)).save('preview_dev.png')
print("saved")
