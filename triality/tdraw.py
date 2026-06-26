"""Glowing additive 3D renderer (numpy float canvas + bloom).
Used across the triality gallery for polytopes / graphs / root systems."""
import numpy as np
from scipy.ndimage import gaussian_filter

CV=(70,190,255)   # 8_v vector  (azure)
CS=(255,200,80)   # 8_s spinor  (gold)
CC=(255,95,180)   # 8_c cospinor(rose)
CLASS_COL=[np.array(CV,float)/255, np.array(CS,float)/255, np.array(CC,float)/255]

def rot4(a,b,th):
    R=np.eye(4); c,s=np.cos(th),np.sin(th)
    R[a,a]=c;R[a,b]=-s;R[b,a]=s;R[b,b]=c; return R

def rot3(a,b,th):
    R=np.eye(3); c,s=np.cos(th),np.sin(th)
    R[a,a]=c;R[a,b]=-s;R[b,a]=s;R[b,b]=c; return R

def proj4to3(P4, wdist=3.2):
    w=P4[:,3]; k=1.0/(wdist-w)
    return P4[:,:3]*k[:,None]

def proj3to2(P3, cam=4.2, f=2.6):
    z=P3[:,2]; k=f/(cam-z)
    xy=P3[:,:2]*k[:,None]
    return xy, z, k

class Canvas:
    def __init__(self, W, bg=(0.01,0.012,0.025)):
        self.W=W; self.img=np.zeros((W,W,3),np.float32)
        self.img[:]=np.array(bg,np.float32)
    def _splat_line(self,p0,p1,col0,col1,width,bright):
        W=self.W
        n=int(max(abs(p1[0]-p0[0]),abs(p1[1]-p0[1]))/1.0)+2
        ts=np.linspace(0,1,n)
        xs=p0[0]+(p1[0]-p0[0])*ts; ys=p0[1]+(p1[1]-p0[1])*ts
        cols=col0[None,:]*(1-ts)[:,None]+col1[None,:]*ts[:,None]
        lw=int(max(1,round(width)))
        for dx in range(-lw,lw+1):
            for dy in range(-lw,lw+1):
                if dx*dx+dy*dy>lw*lw+0.5: continue
                xi=np.clip((xs+dx).astype(int),0,W-1); yi=np.clip((ys+dy).astype(int),0,W-1)
                np.add.at(self.img,(yi,xi),bright*cols)
    def line(self,p0,p1,c0,c1,width=1.5,bright=0.5):
        self._splat_line(np.asarray(p0,float),np.asarray(p1,float),
                         np.asarray(c0,float),np.asarray(c1,float),width,bright)
    def splat(self,p,col,radius,bright):
        W=self.W; r=int(max(2,radius*3))
        x0=int(p[0]); y0=int(p[1])
        xs=np.arange(max(0,x0-r),min(W,x0+r+1)); ys=np.arange(max(0,y0-r),min(W,y0+r+1))
        if len(xs)==0 or len(ys)==0: return
        gx=np.exp(-((xs-p[0])**2)/(2*radius**2)); gy=np.exp(-((ys-p[1])**2)/(2*radius**2))
        g=np.outer(gy,gx)*bright
        self.img[ys[0]:ys[0]+len(ys),xs[0]:xs[0]+len(xs)]+=g[...,None]*np.asarray(col,float)
    def finish(self, S, bloom=(1.4,9.0), gloss=(0.7,0.4), expo=1.25, gamma=1.0):
        arr=self.img
        t=np.stack([gaussian_filter(arr[...,c],bloom[0]) for c in range(3)],-1)
        w=np.stack([gaussian_filter(arr[...,c],bloom[1]) for c in range(3)],-1)
        out=arr+gloss[0]*t+gloss[1]*w
        out=1.0-np.exp(-expo*out)
        if gamma!=1.0: out=np.clip(out,0,1)**(1/gamma)
        from PIL import Image
        im=Image.fromarray((np.clip(out,0,1)*255).astype('uint8'))
        if im.size[0]!=S: im=im.resize((S,S),Image.LANCZOS)
        return im

def world_to_screen(P2, z, W, scale):
    cx=cy=W/2
    sx=cx+P2[:,0]*scale; sy=cy-P2[:,1]*scale
    return np.stack([sx,sy],1)

def render_4d(V4, edges, classes, S=2048, ss=2, R4=None, R3=None, scale_frac=0.34,
              edge_bright=0.42, vtx_bright=1.5, vtx_r_frac=0.010, bg=(0.01,0.012,0.025),
              bloom_frac=(0.0009,0.006), gloss=(0.7,0.4), expo=1.25, edge_w=1.6,
              colors=None, zrange=None, edge_colors=None):
    W=S*ss
    if R4 is None: R4=np.eye(4)
    if R3 is None: R3=np.eye(3)
    P3=proj4to3((R4@V4.T).T)
    P3=(R3@P3.T).T
    P2,z,k=proj3to2(P3)
    scr=world_to_screen(P2,z,W,W*scale_frac)
    cv=Canvas(W,bg)
    cols=colors if colors is not None else [CLASS_COL[c] for c in classes]
    order=np.argsort(z)   # far first
    zmin,zmax=(z.min(),z.max()) if zrange is None else zrange
    def depth(zz): return (zz-zmin)/(zmax-zmin+1e-9)
    for ei,(i,j) in enumerate(edges):
        d=0.5*(depth(z[i])+depth(z[j]))
        br=edge_bright*(0.4+0.9*d)
        wdt=edge_w*ss*(0.6+0.8*d)
        if edge_colors is not None:
            cv.line(scr[i],scr[j],edge_colors[ei],edge_colors[ei],width=wdt,bright=br)
        else:
            cv.line(scr[i],scr[j],cols[i],cols[j],width=wdt,bright=br)
    for i in order:
        d=depth(z[i]); r=W*vtx_r_frac*(0.6+1.0*d)
        cv.splat(scr[i],cols[i],radius=r,bright=vtx_bright*(0.5+1.0*d))
        cv.splat(scr[i],(1,1,1),radius=r*0.4,bright=vtx_bright*0.6*(0.5+1.0*d))
    return cv.finish(S,bloom=(W*bloom_frac[0]+0.6,W*bloom_frac[1]),gloss=gloss,expo=expo)
