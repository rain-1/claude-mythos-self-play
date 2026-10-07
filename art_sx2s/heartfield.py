"""Winding-number field of Duistermaat's Riemann curve on a table grid. saves int8 W (G x G) + extent."""
import numpy as np, sys
from riemann import phi
from wind import winding
G=int(sys.argv[1]); out=sys.argv[2]; M=1<<int(sys.argv[3]) if len(sys.argv)>3 else 1<<23
z=phi(M, nmax=300000)
# table coords: u = 10*Re z, v = 10*Im z ; grid covers u in [-4.6,4.6], v in [-5.6,4.4]
U0,U1,V0,V1=[float(x) for x in (sys.argv[4] if len(sys.argv)>4 else "-4.6,4.6,-5.6,4.4").split(",")]
X=(10*z.real-U0)/(U1-U0)*G-0.0; Y=(10*z.imag-V0)/(V1-V0)*G
w=-winding(X,Y,G,G)   # w[j,i]: j along v, i along u
print(np.unique(w,return_counts=True))
np.savez_compressed(out,w=np.clip(w,-1,40).astype(np.int8),ext=np.array([U0,U1,V0,V1]))
# nearest-curve-time map (mirror-folded s = min(t, 2-t)) via EDT
from scipy.ndimage import distance_transform_edt
t=np.arange(len(z))*2.0/len(z); s=np.minimum(t,2-t)
ii=np.clip(X.astype(np.int64),0,G-1); jj=np.clip(Y.astype(np.int64),0,G-1)
grid=np.full((G,G),-1.0,np.float32); grid[jj,ii]=s
d,(J,I)=distance_transform_edt(grid<0,return_indices=True)
smap=grid[J,I].astype(np.float16)
np.savez_compressed(out,w=np.clip(w,-1,40).astype(np.int8),ext=np.array([U0,U1,V0,V1]),s=smap)
print('smap done')
