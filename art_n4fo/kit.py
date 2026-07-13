"""Shared render kit: complex-plane rasterizer, splats, rings, tone map, bloom."""
import numpy as np
from scipy.ndimage import gaussian_filter

class Canvas:
    """Maps a complex-plane window to an S x S pixel accumulator (3 channels)."""
    def __init__(self, S, zc, half):
        self.S=S; self.zc=complex(zc); self.half=half
        self.buf=np.zeros((S,S,3),np.float64)
    def to_px(self, z):
        z=np.asarray(z,complex)
        x=(z.real-(self.zc.real-self.half))/(2*self.half)*self.S
        y=((self.zc.imag+self.half)-z.imag)/(2*self.half)*self.S   # y down
        return x,y
    def grid_Z(self):
        xs=np.linspace(self.zc.real-self.half,self.zc.real+self.half,self.S)
        ys=np.linspace(self.zc.imag+self.half,self.zc.imag-self.half,self.S)
        X,Y=np.meshgrid(xs,ys)
        return X+1j*Y
    def add_field(self, field, color):
        """field: S x S scalar; color: (3,) rgb. Adds field[...,None]*color."""
        self.buf += field[...,None]*np.asarray(color,float)[None,None,:]
    def splat(self, z, color, sigma_px, amp):
        """Additive Gaussian splat(s) at complex z (bilinear center, then blur handled globally)."""
        x,y=self.to_px(z)
        color=np.asarray(color,float)
        S=self.S
        xi=np.floor(x).astype(int); yi=np.floor(y).astype(int)
        fx=x-xi; fy=y-yi
        for dxp,wx in ((0,1-fx),(1,fx)):
            for dyp,wy in ((0,1-fy),(1,fy)):
                xx=xi+dxp; yy=yi+dyp
                m=(xx>=0)&(xx<S)&(yy>=0)&(yy<S)
                w=(wx*wy*amp)[m]
                np.add.at(self.buf, (yy[m],xx[m]), w[:,None]*color[None,:])

def disc_field(Z, center, radius, edge=0.0):
    """Soft indicator of disc |z-c|<=r, smooth falloff over 'edge' (in plane units)."""
    d=np.abs(Z-center)
    if edge<=0:
        return (d<=radius).astype(np.float64)
    return np.clip((radius-d)/edge+0.5,0,1)

def ring_field(Z, center, radius, width):
    """Gaussian ring at |z-c|=r, width in plane units. Resolution-independent."""
    d=np.abs(np.abs(Z-center)-radius)
    return np.exp(-(d/width)**2)

def tonemap(buf, k=1.0, gamma=0.85):
    """Filmic 1-exp(-k x) then gamma; returns uint8 image."""
    x=np.nan_to_num(np.clip(buf,0,None), nan=0.0, posinf=0.0)
    y=1.0-np.exp(-k*x)
    y=np.clip(y,0,1)**gamma
    return (y*255+0.5).astype(np.uint8)

def bloom(buf, sigmas_amps):
    """Add blurred copies for glow. sigmas_amps: list of (sigma_px, amp)."""
    out=buf.copy()
    for s,a in sigmas_amps:
        out += a*gaussian_filter(buf, sigma=(s,s,0))
    return out
