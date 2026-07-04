"""Shared rendering helpers for the 'Frozen and the Free' triptych."""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

def histeq(x, mask=None):
    """Rank-transform to [0,1] (histogram equalization) of the flat values."""
    x=np.asarray(x, np.float64); flat=x.ravel()
    if mask is not None:
        m=mask.ravel(); out=np.zeros_like(flat)
        v=flat[m]; r=np.argsort(np.argsort(v)); out[m]=r/(r.max()+1e-9); return out.reshape(x.shape)
    r=np.argsort(np.argsort(flat)); return (r/(r.max()+1e-9)).reshape(x.shape)

def ramp(stops, t):
    """Piecewise-linear colour ramp. stops=[(pos,(r,g,b)),...] pos in[0,1], t array in[0,1]."""
    t=np.clip(t,0,1); pos=np.array([s[0] for s in stops]); cols=np.array([s[1] for s in stops],float)
    out=np.empty(t.shape+(3,))
    for ch in range(3):
        out[...,ch]=np.interp(t,pos,cols[:,ch])
    return out

def filmic(x, k=1.0):
    return 1.0-np.exp(-k*np.clip(x,0,None))

def bloom(chan, sigmas=(2,6,18), amps=(0.5,0.3,0.2)):
    out=np.zeros_like(chan,dtype=np.float64)
    for s,a in zip(sigmas,amps): out+=a*gaussian_filter(chan,s)
    return out

def to_img(rgb):  # rgb float [0,1+] -> uint8
    return Image.fromarray((255*np.clip(rgb,0,1)).astype(np.uint8))

def save(rgb, path, size=None, resample=Image.LANCZOS):
    im=to_img(rgb)
    if size and size!=im.size[0]: im=im.resize((size,size),resample)
    im.save(path); return im

def downscale(rgb, factor):
    im=to_img(rgb); W=im.size[0]//factor
    return np.asarray(im.resize((W,W),Image.LANCZOS),float)/255.0
