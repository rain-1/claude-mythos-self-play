import numpy as np, sys
from PIL import Image
from scipy.ndimage import rotate
from sympy import divisors
G=int(sys.argv[1])
for n in sys.argv[2:]:
    H=np.fromfile(f'data/c{n}.bin',np.float32).reshape(G,G)
    k=len(divisors(int(n)))
    # full symmetry: union over rotations by 2pi/k (n at every position) + mirror
    S=np.zeros_like(H)
    for r in range(k):
        S+=rotate(H, 360*r/k, reshape=False, order=1)
    S=S+S[::-1]
    t=np.log1p(S/np.percentile(S[S>0],50))
    t/=t.max()
    im=(255*(1-t)).astype(np.uint8)
    Image.fromarray(im[::-1]).save(f'proto/cloud{n}.png')
    print(n, S.sum(), (S>0).mean())
