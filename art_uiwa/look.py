import sys,numpy as np; from PIL import Image
d=np.load(sys.argv[1]); S=d['snaps']; idx=[int(i) for i in sys.argv[3:]]
ims=[]
for i in idx:
    u=S[i]; v=np.clip(u/np.percentile(u,99.9),0,1)**0.5
    ims.append((v*255).astype(np.uint8)); print(i,d['times'][i],u.mean(),u.max())
Image.fromarray(np.hstack(ims)).resize((512*len(idx),512)).save(sys.argv[2])
