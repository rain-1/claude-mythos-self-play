import numpy as np, time
from chameleon import solve_triangle
import scipy.sparse as spa, scipy.sparse.linalg as sla
from PIL import Image

M = 400
states, idx, PR, PG = solve_triangle(M)
PB = 1 - PR - PG
S = 800
img = np.zeros((S, S, 3), np.float32)
cnt = np.zeros((S, S), np.float32)
# barycentric: red top, green lower-left, blue lower-right
vR = np.array([S/2, 0.08*S]); vG = np.array([0.06*S, 0.94*S]); vB = np.array([0.94*S, 0.94*S])
cR = np.array([1.0, 0.30, 0.18]); cG = np.array([0.25, 1.0, 0.45]); cB = np.array([0.25, 0.55, 1.0])
pts = np.array([( \
    (r/M)*vR + ((M-r-b)/M)*vG + (b/M)*vB) for (r,b) in states])
cols = (PR[:,None]*cR + PG[:,None]*cG + PB[:,None]*cB)
xi = np.clip(pts[:,0].astype(int), 0, S-1); yi = np.clip(pts[:,1].astype(int), 0, S-1)
for c in range(3):
    np.add.at(img[:,:,c], (yi, xi), cols[:,c])
np.add.at(cnt, (yi, xi), 1.0)
mask = cnt > 0
img[mask] /= cnt[mask][:,None]
out = (np.clip(img, 0, 1)**0.85 * 255).astype(np.uint8)
Image.fromarray(out).save('preview_destiny.png')
print("saved preview; PR range", PR.min(), PR.max())
