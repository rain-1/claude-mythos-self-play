import sys, numpy as np
from PIL import Image
ims=[]
for f in sys.argv[2:]:
    P=np.load(f); row=[]
    for ax in [(0,1),(0,2),(2,1)]:
        a,b=P[:,ax[0]],P[:,ax[1]]
        c=np.median(P,0); s=np.percentile(np.abs(P-c),99.5)*1.1
        H,_,_=np.histogram2d(b,a,bins=300,range=[[c[ax[1]]-s,c[ax[1]]+s],[c[ax[0]]-s,c[ax[0]]+s]])
        row.append(255-np.clip(255*(1-np.exp(-H/np.percentile(H[H>0],60)*0.4)),0,255))
    ims.append(np.hstack(row))
Image.fromarray(np.vstack(ims).astype(np.uint8)[::-1]).save(sys.argv[1])
