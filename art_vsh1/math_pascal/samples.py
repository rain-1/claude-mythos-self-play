import numpy as np
from sim import triangle, triangle_int
T,C=triangle(0.3,512,2026)
np.save('tri_p030.npy',T); np.save('coins_p030.npy',C)
print('p=0.3 max',T.max(),'log10max',np.log10(T.max()), 'coins frac', C[np.tril_indices(512,-1)].mean())
Ti,Ci,ov=triangle_int(0.08,512,2026)
print('p=0.08 overflow',ov,'max',Ti.max())
np.save('tri_pc.npy',Ti); np.save('coins_pc.npy',Ci)
# consistency checks: parity vs binomial mod 2, edges, -1 above diagonal
from math import comb
n=np.arange(512)[:,None]; k=np.arange(512)[None,:]
par=((n & k)==k).astype(np.int64)  # C(n,k) odd iff k&n==k (Lucas)
mask=k<=n
print('parity ok p=.08:', np.all((Ti[mask]%2)==par[mask]), ' -1 elsewhere:', np.all(Ti[~mask]==-1))
print('parity ok p=.3 (rows<60, exact range):', np.all((T[:60][mask[:60]]%2)==par[:60][mask[:60]]))
