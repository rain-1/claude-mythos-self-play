"""Reusable additive-glow 3D wireframe renderer (numpy).
Perspective projection + bilinear line splatting + bloom + filmic tone map.
"""
import numpy as np
from scipy.ndimage import gaussian_filter

def rot(ax, ang):
    c,s=np.cos(ang),np.sin(ang)
    if ax=='x': return np.array([[1,0,0],[0,c,-s],[0,s,c]])
    if ax=='y': return np.array([[c,0,s],[0,1,0],[-s,0,c]])
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])

class Camera:
    def __init__(self, S, Rmat, cam_z=34.0, focal=1.9, center=(0,0,0)):
        self.S=S; self.R=Rmat; self.cam_z=cam_z; self.f=focal
        self.center=np.array(center,float)
        self.pscale=1.0; self.pshift=np.array([0.0,0.0])  # NDC post-fit
    def project(self, P):
        """P: (N,3) world -> (N,2) pixel coords + depth (camera z)."""
        Q=(P-self.center)@self.R.T
        z=self.cam_z - Q[:,2]           # distance in front of camera
        z=np.maximum(z,1e-3)
        u=Q[:,0]*self.f/z; v=Q[:,1]*self.f/z
        u=u*self.pscale+self.pshift[0]; v=v*self.pscale+self.pshift[1]
        px=(0.5+u)*self.S; py=(0.5-v)*self.S
        return np.stack([px,py],1), z
    def fit(self, allP, margin=0.86):
        """Set pscale/pshift so all points fit centered within +-margin/2 of frame."""
        self.pscale=1.0; self.pshift[:]=0
        uv=[]
        for P in allP:
            xy,_=self.project(P)
            u=xy[:,0]/self.S-0.5; v=0.5-xy[:,1]/self.S
            uv.append(np.stack([u,v],1))
        uv=np.concatenate(uv,0)
        lo=uv.min(0); hi=uv.max(0); c=(lo+hi)/2; ext=(hi-lo).max()
        self.pscale=margin/max(ext,1e-6)
        self.pshift=-c*self.pscale

def splat_points(buf, xy, rgb, weight):
    """Bilinear additive splat of points xy (M,2) with per-point rgb (M,3) & weight (M,)."""
    S=buf.shape[0]
    x=xy[:,0]; y=xy[:,1]
    m=(x>=0)&(x<S-1)&(y>=0)&(y<S-1)
    x=x[m]; y=y[m]; rgb=rgb[m]; w=weight[m]
    x0=np.floor(x).astype(np.int32); y0=np.floor(y).astype(np.int32)
    fx=x-x0; fy=y-y0
    for (dx,dy,wt) in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:
        ww=(wt*w)[:,None]*rgb
        idx=( (y0+dy)*S + (x0+dx) )
        for c in range(3):
            np.add.at(buf.reshape(-1,3)[:,c], idx, ww[:,c])

def draw_edges(buf, cam, P, edges, colors, exposure, samp=1.4, depthfade=0.55):
    """P:(N,3), edges list of (a,b), colors:(E,3) per-edge, exposure scalar or (E,)."""
    xy,z=cam.project(P)
    S=buf.shape[0]
    exp=np.full(len(edges),exposure,float) if np.isscalar(exposure) else exposure
    for k,(a,b) in enumerate(edges):
        pa,pb=xy[a],xy[b]; za,zb=z[a],z[b]
        L=np.hypot(*(pb-pa))
        n=max(2,int(L*samp))
        t=np.linspace(0,1,n)
        pts=pa[None,:]*(1-t)[:,None]+pb[None,:]*t[:,None]
        zz=za*(1-t)+zb*t
        # depth fade: nearer = brighter
        df=(1.0/zz); df=df/df.mean() if df.mean()>0 else df
        w=exp[k]*(1.0+depthfade*(df-1.0))/n*L/max(L,1)
        col=np.repeat(colors[k][None,:],n,0)
        splat_points(buf, pts, col, np.full(n,exp[k])* (1.0+depthfade*(df-1.0)) * (samp/ max(samp,1)) )
    return buf

def draw_verts(buf, cam, P, idxs, colors, sizes, exposure):
    xy,z=cam.project(P)
    S=buf.shape[0]
    for j,i in enumerate(idxs):
        cx,cy=xy[i]; r=sizes[j]
        if not (0<=cx<S and 0<=cy<S): continue
        x0=int(max(0,cx-3*r)); x1=int(min(S,cx+3*r+1))
        y0=int(max(0,cy-3*r)); y1=int(min(S,cy+3*r+1))
        if x1<=x0 or y1<=y0: continue
        yy,xx=np.mgrid[y0:y1,x0:x1]
        g=np.exp(-(((xx-cx)**2+(yy-cy)**2)/(2*r*r)))
        buf[y0:y1,x0:x1,:]+=exposure*g[...,None]*colors[j][None,None,:]
    return buf

def _wide_blur(buf, sigma):
    """Fast wide gaussian via downsample->blur->upsample (visually identical for halos)."""
    if sigma<=8:
        return gaussian_filter(buf, sigma=(sigma,sigma,0))
    import math
    ds=max(1,int(sigma//6))
    small=buf[::ds,::ds,:]
    sb=gaussian_filter(small, sigma=(sigma/ds,sigma/ds,0))
    # upsample back with PIL-free repeat + light smooth
    up=np.repeat(np.repeat(sb,ds,0),ds,1)[:buf.shape[0],:buf.shape[1],:]
    return gaussian_filter(up, sigma=(2,2,0))

def bloom_tonemap(buf, k=1.0, gamma=0.9, blooms=((2.0,0.5),(6.0,0.3),(18,0.15)), sat=1.0):
    out=buf.copy()
    for sig,amt in blooms:
        out+=amt*_wide_blur(buf,sig)
    rgb=1.0-np.exp(-k*out)
    if sat!=1.0:
        L=rgb.mean(2,keepdims=True); rgb=L+sat*(rgb-L)
    rgb=np.clip(rgb,0,1)**gamma
    return (np.clip(rgb,0,1)*255).astype(np.uint8)
