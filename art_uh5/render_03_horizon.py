"""03 — Nearness Is a Tree (the Bruhat-Tits tree of Q_p). 2048^2.

Seed: "p-adic valuation of products" (MathOverflow).
In the p-adic numbers, distance is ULTRAMETRIC: every triangle is isosceles,
and "close" no longer means "along a line" -- it means "agreeing far down a
branch". The Bruhat-Tits tree of Q_p is the (p+1)-regular tree whose every
infinite end is a p-adic number; its boundary circle is Q_p itself. Drawn in
the Poincare disk with geodesic edges (a fixed hyperbolic step per generation),
the tree opens vast empty hyperbolic 'rooms' in the middle and crowds all its
infinitely many ends onto the rim -- a glowing horizon where the p-adic
numbers live. Cool violet at the root, hot amber at the edge of the knowable.
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

def Rot(phi):
    return np.array([[np.exp(1j*phi/2),0],[0,np.exp(-1j*phi/2)]],complex)
def Trans(d):
    c=np.cosh(d/2); s=np.sinh(d/2)
    return np.array([[c,s],[s,c]],complex)
def mob(M,z):
    return (M[0,0]*z+M[0,1])/(M[1,0]*z+M[1,1])

def build(p, depth, delta, nseg=14):
    """returns (segments, leaves): segment=(points,level); leaves=complex endpoints
    of the deepest generation (the ends of the tree = points of Q_p)."""
    segs=[]; leaves=[]
    base_steps=np.linspace(0,1,nseg)
    Tcache=[Trans(s*delta) for s in base_steps]
    Tfull=Trans(delta)
    def edge(M, ang, lvl):
        b=M@Rot(ang)
        pts=[mob(b@T,0) for T in Tcache]
        segs.append((pts,lvl))
        Mc=b@Tfull
        if lvl==depth-1:
            leaves.append(mob(Mc,0))
        return Mc
    def rec(M,lvl):
        if lvl>=depth: return
        for j in range(1,p+1):
            ang=np.pi+2*np.pi*j/(p+1)
            Mc=edge(M,ang,lvl)
            rec(Mc,lvl+1)
    I=np.eye(2,dtype=complex)
    for k in range(p+1):
        Mc=edge(I,2*np.pi*k/(p+1),0)
        rec(Mc,1)
    return segs, np.array(leaves)

def palette(t):
    # cool sky-blue root -> hot amber horizon (the edge of the knowable)
    stops=np.array([[0.30,0.65,1.00],[0.25,0.55,0.98],[0.55,0.35,0.95],
                    [0.95,0.30,0.70],[1.00,0.45,0.30],[1.00,0.78,0.40],[1.00,0.97,0.85]])
    pos=np.array([0.0,0.35,0.55,0.72,0.85,0.94,1.0])
    return tuple(int(255*np.interp(t,pos,stops[:,c])) for c in range(3))

def render(p=2, depth=17, delta=0.95, S=2048, ss=2, bloom=2.4, glow=0.7):
    W=S*ss; R=W*0.455; cx=cy=W/2
    segs,leaves=build(p,depth,delta)
    maxl=max(s[1] for s in segs)
    img=Image.new('RGB',(W,W),(2,2,7))
    d=ImageDraw.Draw(img)
    # draw deepest (rim) last so the horizon sits on top
    segs.sort(key=lambda s:s[1])
    for pts,lvl in segs:
        xy=[(cx+R*z.real, cy+R*z.imag) for z in pts]
        w=max(1, int(round(3.5*(1-lvl/maxl))))   # thick near root, thin at rim
        d.line(xy, fill=palette(lvl/maxl), width=w, joint='curve')
    # faint horizon circle: the boundary of the tree = Q_p itself
    d.ellipse([cx-R,cy-R,cx+R,cy+R], outline=(90,55,30), width=1)
    arr=np.asarray(img).astype(np.float32)/255.0
    # splat the ENDS of the tree (= points of Q_p) as a luminous amber ring
    if len(leaves):
        ends=np.zeros((W,W),np.float32)
        xi=np.clip((cx+R*leaves.real).astype(int),0,W-1)
        yi=np.clip((cy+R*leaves.imag).astype(int),0,W-1)
        np.add.at(ends, (yi,xi), 1.0)
        ends=gaussian_filter(ends, 1.6); ends*= (2*np.pi*1.6**2)   # restore peak after blur
        ends=np.clip(ends,0,1.4)
        amber=np.array([1.0,0.80,0.45],np.float32)
        arr=arr + 0.9*ends[...,None]*amber
    if bloom:
        tight=np.stack([gaussian_filter(arr[...,c],bloom) for c in range(3)],-1)
        wide =np.stack([gaussian_filter(arr[...,c],bloom*5) for c in range(3)],-1)
        arr=arr + glow*tight + 0.35*wide
    arr=1.0-np.exp(-1.25*arr)            # filmic exposure lift, bounded
    out=Image.fromarray((np.clip(arr,0,1)*255).astype('uint8')).resize((S,S),Image.LANCZOS)
    return out

if __name__=="__main__":
    import sys,time
    t0=time.time()
    out=sys.argv[1] if len(sys.argv)>1 else 'art_uh5/03_nearness_is_a_tree.png'
    render().save(out)
    print('done',out,time.time()-t0)
