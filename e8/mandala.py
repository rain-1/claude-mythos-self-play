"""E8 Coxeter-plane mandala renderer (fast batched glow)."""
import numpy as np, sys, math
sys.path.insert(0,'e8')
import e8
from scipy.ndimage import gaussian_filter
from PIL import Image
import colorsys

def setup():
    R=e8.roots(); u,t,C=e8.coxeter_plane()
    P=np.stack([R@u,R@t],1)
    rad=np.linalg.norm(P,axis=1)
    rings=np.unique(np.round(rad,3))
    ring_idx=np.array([int(np.argmin(np.abs(rings-r))) for r in np.round(rad,3)])
    G=R@R.T
    E=np.array([(i,j) for i in range(240) for j in range(i+1,240) if abs(G[i,j]-1)<1e-6])
    return P,rad,ring_idx,len(rings),E,R

def ring_color(k,n):
    r,g,b=colorsys.hsv_to_rgb(0.62-0.62*k/(n-1),0.55,1.0); return np.array([r,g,b])

def render(P,ring_idx,nring,E, S=1600, ss=2, ang=0.0, scale_frac=0.46,
           edge_bright=0.05, pt_bright=1.4):
    W=S*ss
    c,s=math.cos(ang),math.sin(ang)
    Rm=np.array([[c,-s],[s,c]])
    Q=(P@Rm.T)
    sc=W*scale_frac/(np.abs(Q).max()+1e-9)
    scr=np.stack([W/2+Q[:,0]*sc, W/2-Q[:,1]*sc],1)
    img=np.zeros((W,W,3),np.float32)+np.array([0.01,0.011,0.022])
    cols=np.array([ring_color(k,nring) for k in range(nring)])
    pcol=cols[ring_idx]
    A=scr[E[:,0]]; B=scr[E[:,1]]
    ec=0.5*(pcol[E[:,0]]+pcol[E[:,1]])
    K=24; ts=np.linspace(0,1,K)
    XY=A[:,None,:]+(B-A)[:,None,:]*ts[None,:,None]
    EC=np.repeat(ec[:,None,:],K,axis=1).reshape(-1,3)
    Xr=XY[...,0].reshape(-1); Yr=XY[...,1].reshape(-1)
    flat=img.reshape(-1,3)
    lw=max(1,int(round(ss*1.3)))
    offs=[(ox,oy,math.exp(-(ox*ox+oy*oy)/(2*(lw*0.7)**2)))
          for ox in range(-lw,lw+1) for oy in range(-lw,lw+1)]
    for ox,oy,wt in offs:
        X=np.clip((Xr+ox).astype(int),0,W-1); Y=np.clip((Yr+oy).astype(int),0,W-1)
        idx=Y*W+X
        for ch in range(3):
            np.add.at(flat[:,ch], idx, edge_bright*wt*EC[:,ch])
    img=flat.reshape(W,W,3)
    pr=int(W*0.006)
    yy,xx=np.mgrid[-pr:pr+1,-pr:pr+1]; g=np.exp(-(xx**2+yy**2)/(2*(pr*0.5)**2))
    for i in range(len(scr)):
        x,y=int(scr[i,0]),int(scr[i,1])
        if pr<=x<W-pr and pr<=y<W-pr:
            img[y-pr:y+pr+1, x-pr:x+pr+1]+= g[...,None]*pcol[i]*pt_bright
            img[y-pr:y+pr+1, x-pr:x+pr+1]+= g[...,None]*np.array([1,1,1])*pt_bright*0.4
    tigh=np.stack([gaussian_filter(img[...,c],ss*1.2) for c in range(3)],-1)
    wide=np.stack([gaussian_filter(img[...,c],ss*7.0) for c in range(3)],-1)
    out=img+0.55*tigh+0.30*wide
    out=1.0-np.exp(-1.25*out)
    im=Image.fromarray((np.clip(out,0,1)*255).astype('uint8'))
    if ss>1: im=im.resize((S,S),Image.LANCZOS)
    return im

if __name__=="__main__":
    P,rad,ring_idx,nring,E,R=setup()
    print("rings",nring,"edges",len(E))
    im=render(P,ring_idx,nring,E,S=1200,ss=2,ang=0.0)
    im.save("e8/_static.png"); print("done")
