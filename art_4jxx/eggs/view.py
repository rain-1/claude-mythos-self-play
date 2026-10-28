import sys, numpy as np
from scipy.spatial import cKDTree
from PIL import Image, ImageDraw
R=160; out=sys.argv[1]; fs=sys.argv[2:]
cols=6; rows=(len(fs)+cols-1)//cols
canvas=Image.new('RGB',(cols*R*2,rows*R*2+0),'white')
yy,xx=np.mgrid[-R:R,-R:R]/R; m=xx**2+yy**2<1; z=np.sqrt(np.clip(1-xx**2-yy**2,0,1))
D=np.stack([xx[m],-yy[m],z[m]],1)
for i,f in enumerate(fs):
    d=np.load(f); t=cKDTree(d['V']); _,idx=t.query(D); v=d['v'][idx]
    s=np.clip(v/0.35,0,1); sh=0.55+0.45*z[m]
    img=np.ones((2*R,2*R,3)); img[m]=(np.array([1,.95,.8])*(1-s[:,None])+np.array([.9,.4,.55])*s[:,None])*sh[:,None]
    im=Image.fromarray((img*255).astype(np.uint8)); ImageDraw.Draw(im).text((5,5),f"{i+1} F{d['Fk'][0]:.4f} k{d['Fk'][1]:.4f}",fill=(0,0,0))
    canvas.paste(im,((i%cols)*2*R,(i//cols)*2*R))
canvas.save(out)
