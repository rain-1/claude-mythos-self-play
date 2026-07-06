"""PIECE 2: 'The Ridge of Two Ways' — eikonal wavefronts from a source sweep a
pond of stones; where two arcs of the SAME wavefront collide behind a stone the
shortest path stops being unique: the cut locus.  Holes make the domain
multiply-connected, so the cut locus is a finite GRAPH (with cycles), not a tree.
"""
import numpy as np
import skfmm
from PIL import Image
from scipy.ndimage import gaussian_filter, label

def solve(S, R, holes, src):
    xs=np.linspace(-1,1,S); ys=np.linspace(-1,1,S)
    X,Y=np.meshgrid(xs,ys); dx=float(xs[1]-xs[0])
    inside=(X**2+Y**2)<R**2
    mask=~inside
    holemask=np.zeros_like(inside)
    for (cx,cy,r) in holes:
        holemask|=((X-cx)**2+(Y-cy)**2)<r**2
    mask|=holemask
    sx,sy=src
    phi=np.sqrt((X-sx)**2+(Y-sy)**2)-0.012
    tt=skfmm.travel_time(np.ma.MaskedArray(phi,mask),
                         speed=np.ones_like(X),dx=dx)
    d=np.ma.filled(tt,np.nan)
    return X,Y,d,mask,inside,holemask,dx

def cutlocus(d, mask, dx, inside, jump=0.34, smooth=1.1, erode=5):
    from scipy.ndimage import binary_erosion
    dd=d.copy(); dd[~np.isfinite(dd)]=np.nanmax(d)+0.5
    dd=gaussian_filter(dd,smooth)
    gy,gx=np.gradient(dd,dx); ang=np.arctan2(gy,gx)
    def adiff(a,b): return np.abs(np.mod(a-b+np.pi,2*np.pi)-np.pi)
    strength=np.zeros(d.shape)
    valid=np.isfinite(d)&~mask
    for ax in (0,1):
        for sh in (1,-1):
            b=np.roll(ang,sh,axis=ax); vb=np.roll(valid,sh,axis=ax)
            strength=np.maximum(strength,np.where(valid&vb,adiff(ang,b),0))
    # erode the DOMAIN boundary heavily (grad noise there) but keep hole edges
    dom_in=binary_erosion(inside,iterations=erode)
    cut=valid&dom_in&(strength>jump)
    # drop tiny specks
    lab,n=label(cut); sizes=np.bincount(lab.ravel()); sizes[0]=0
    keep=np.isin(lab,np.where(sizes>=14)[0])
    return keep, strength

def render(S=2048, out="02_ridge_of_two_ways.png", holes=None, src=(-0.7,0.02),
           R=0.955, ss=2):
    Sr=S*ss
    X,Y,d,mask,inside,holemask,dx=solve(Sr,R,holes,src)
    cut,strength=cutlocus(d,mask,dx,inside,erode=max(4,3*ss))
    dd=np.nan_to_num(d,nan=0.0)
    dmax=np.nanmax(d)
    # soft luminous wavefronts: crest function, brightness tapers with distance
    freq=52.0
    ring=0.5+0.5*np.cos(dd*freq)
    ring=ring**2.4                     # sharpen crests -> thin bright rings
    atten=np.clip(1.0-0.35*(dd/dmax),0.45,1.0)
    wav=ring*atten*inside*(~mask)
    # cut locus, colored by distance (a tree with a gradient), bloomed
    from scipy.ndimage import binary_dilation
    cutwide=binary_dilation(cut,iterations=ss)
    cdist=np.where(cut,dd,0.0)
    cutf=gaussian_filter(cutwide.astype(float),0.6*ss)
    cutbloom=gaussian_filter(cut.astype(float),3.5*ss)
    # stone rims (creeping wave glow)
    rim=gaussian_filter(holemask.astype(float),1.2*ss)-holemask
    rim=np.clip(rim,0,1)
    # ---- compose ----
    rgb=np.zeros((Sr,Sr,3))
    # wavefronts: deep blue -> cyan on crest
    rgb[...,0]+=wav*0.10
    rgb[...,1]+=wav*0.55
    rgb[...,2]+=wav*0.95
    # faint base glow inside domain so it's not pure black between rings
    base=inside&(~mask)
    rgb[...,2]+=0.05*base; rgb[...,1]+=0.03*base
    # warm source glow
    sx,sy=src
    Rr2=(X-sx)**2+(Y-sy)**2
    sg=np.exp(-Rr2/(2*0.05**2))*base
    rgb[...,0]+=0.9*sg; rgb[...,1]+=0.7*sg; rgb[...,2]+=0.4*sg
    # cut locus gold->white
    cn=gaussian_filter(cdist,1.0*ss)/(dmax+1e-9)
    gold=cutf
    rgb[...,0]+=1.7*gold
    rgb[...,1]+=1.15*gold*(0.7+0.3*cn)
    rgb[...,2]+=0.45*gold*cn
    rgb[...,0]+=1.5*cutbloom; rgb[...,1]+=1.0*cutbloom; rgb[...,2]+=0.4*cutbloom
    # stone rims cyan
    rgb[...,1]+=0.5*rim; rgb[...,2]+=0.7*rim
    # kill holes to black
    for k in range(3): rgb[...,k][holemask]=0.0
    rgb[...,:][~inside]=0.0
    # tone
    rgb=1-np.exp(-1.5*np.clip(rgb,0,None))
    rgb=np.clip(rgb,0,1)**0.9
    img=Image.fromarray((255*rgb).astype(np.uint8))
    if ss>1: img=img.resize((S,S),Image.LANCZOS)
    img.save(out)
    # verify graph structure
    ncut=int(cut.sum()); lab,ncomp=label(cut)
    print("saved",out,"cut components:",ncomp,"cut px:",ncut)
    return d,cut,inside,mask,holemask

HOLES=[(-0.08,0.44,0.16),(0.30,0.30,0.13),(0.02,-0.02,0.19),
       (0.46,-0.10,0.12),(0.10,-0.46,0.15),(0.56,0.34,0.10),(-0.34,-0.20,0.11)]

if __name__=="__main__":
    render(S=860,ss=1,holes=HOLES,src=(-0.68,0.06))
