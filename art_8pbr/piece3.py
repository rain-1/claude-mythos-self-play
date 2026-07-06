"""PIECE 3: 'The Ways Home Are Numbered' — nested Brillouin zones of a lattice.
On a flat torus, the cut locus of a point is its Wigner-Seitz cell boundary.
The k-th Brillouin zone is where the origin is the k-th-NEAREST lattice image:
the k-th 'way home'.  zone(x) = 1 + #{ v != 0 : |x-v| < |x| }.  Boundaries =
perpendicular bisectors = the equidistance (cut) loci.  Nested star-polygon
shells = a crystalline stained-glass mandala.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

def lattice_pts(v1, v2, nmax):
    ij=np.arange(-nmax,nmax+1)
    I,J=np.meshgrid(ij,ij)
    P=I.ravel()[:,None]*np.array(v1)+J.ravel()[:,None]*np.array(v2)
    return P  # (M,2), includes origin

def compute(S, span, v1, v2, nmax=14, chunk=131072):
    xs=np.linspace(-span,span,S); ys=np.linspace(span,-span,S)
    X,Y=np.meshgrid(xs,ys)
    pts=np.stack([X.ravel(),Y.ravel()],1)   # (P,2)
    V=lattice_pts(v1,v2,nmax)                # (M,2)
    # drop origin from V for the "others" comparison; keep separately
    r0all=np.hypot(pts[:,0],pts[:,1])
    Vn=V[np.hypot(V[:,0],V[:,1])>1e-9]       # non-origin
    P=pts.shape[0]
    zone=np.empty(P,np.int32)
    margin=np.empty(P,np.float32)            # distance to nearest bisector (approx)
    Vn=Vn.astype(np.float32); pts=pts.astype(np.float32); r0all=r0all.astype(np.float32)
    for s in range(0,P,chunk):
        e=min(P,s+chunk)
        xc=pts[s:e]                          # (c,2)
        r0=r0all[s:e]                        # (c,)
        dif=xc[:,None,:]-Vn[None,:,:]        # (c,M,2)
        dist=np.sqrt((dif*dif).sum(2))       # (c,M)
        zone[s:e]=1+(dist<r0[:,None]).sum(1)
        margin[s:e]=np.min(np.abs(dist-r0[:,None]),axis=1)
    return (zone.reshape(S,S), margin.reshape(S,S), None, X, Y)

PAL=np.array([
    [0.16,0.20,0.52],  # 1 indigo
    [0.12,0.42,0.60],  # 2 blue
    [0.10,0.55,0.52],  # 3 teal
    [0.30,0.60,0.32],  # 4 green
    [0.78,0.66,0.22],  # 5 gold
    [0.82,0.45,0.20],  # 6 amber
    [0.72,0.26,0.34],  # 7 rose
    [0.52,0.25,0.55],  # 8 violet
    [0.34,0.30,0.62],  # 9 periwinkle
])

def shade(zone, margin, ang=None, zmax=13, edge_gain=0.8, mscale=0.22, ss=1):
    S=zone.shape[0]
    col=PAL[(zone-1)%len(PAL)]               # cycle palette through all shells
    body=np.clip(margin/mscale,0,1)**0.6
    body=0.22+0.78*body                      # jewel cells glow from centre
    img=col*body[...,None]
    zf=zone.astype(float)
    ez=(np.abs(np.gradient(zf)[0])+np.abs(np.gradient(zf)[1]))>0
    eg=gaussian_filter(ez.astype(float),0.7*ss)
    # gold leading for all zone boundaries
    img[...,0]+=edge_gain*1.00*eg; img[...,1]+=edge_gain*0.80*eg; img[...,2]+=edge_gain*0.40*eg
    # the FIRST-zone boundary = the torus cut locus: mark cyan/white
    first=((zone==1)&(margin<mscale*0.16))
    firstb=gaussian_filter(first.astype(float),0.8*ss)
    if firstb.max()>0: firstb/=firstb.max()
    img[...,0]+=0.25*firstb; img[...,1]+=1.05*firstb; img[...,2]+=1.25*firstb
    # bloom the whole leading gently
    bl=gaussian_filter(eg,2.2*ss)
    img[...,0]+=0.25*bl; img[...,1]+=0.20*bl; img[...,2]+=0.11*bl
    img[zone>zmax]=0.015
    return img

def render(S=2048, out="03_ways_home_numbered.png", span=3.15, ss=2,
           v1=(1.0,0.0), v2=(0.5,np.sqrt(3)/2), zmax=13, nmax=10):
    Sr=S*ss
    zone,margin,ang,X,Y=compute(Sr,span,v1,v2,nmax=nmax,chunk=32768)
    img=shade(zone,margin,ang,zmax=zmax,ss=ss)
    img=(255*np.clip(img,0,1)**0.9).astype(np.uint8)
    im=Image.fromarray(img)
    if ss>1: im=im.resize((S,S),Image.LANCZOS)
    im.save(out)
    print("saved",out,"max zone shown",zmax)

if __name__=="__main__":
    render(S=680,ss=1)   # quick check

