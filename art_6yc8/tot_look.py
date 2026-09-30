import numpy as np
from PIL import Image
L=60000
phi=np.arange(L+1)
for p in range(2,L+1):
    if phi[p]==p:
        phi[p::p]-=phi[p::p]//p
order=np.argsort(phi[1:],kind='stable')+1
vals=phi[order]
cuts=np.nonzero(np.diff(vals))[0]+1
groups=np.split(order,cuts)
A=[];B=[]
for g in groups:
    if len(g)<2: continue
    g=np.sort(g)
    i,j=np.triu_indices(len(g),1)
    A.append(g[i]);B.append(g[j])
A=np.concatenate(A);B=np.concatenate(B)
print(len(A))
G=1400
H=np.zeros((G,G))
np.add.at(H,(np.minimum(B*G//(L+1),G-1),np.minimum(A*G//(L+1),G-1)),1)
t=np.log1p(H)/np.log1p(H).max()
Image.fromarray((255*(1-t)).astype(np.uint8)[::-1]).save('proto/tot_pairs.png')
np.save('data/tot_pairs_60k.npy',np.stack([A,B]))
