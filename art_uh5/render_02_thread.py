"""02 — A Line That Learns to Be a Plane (Hilbert space-filling curve). 2048^2.

Seed: "Can a continuous bijection lower topological dimension?" (MathOverflow).
The Hilbert curve is a single continuous thread, parametrised by one number
t in [0,1] -- a LINE. Yet followed far enough it visits every region of the
square: a line that fills a plane. Here the thread is painted by its own
arc-length (deep navy at t=0, pale gold at t=1) so you can trace the one path
as it weaves the whole surface. At this order the thread is just thick enough
to read as a woven cord and just fine enough that it fills -- the liminal
moment where a line becomes a plane.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

def hilbert_points(order):
    n=1<<order; N=n*n
    pts=np.empty((N,2),np.int64)
    for d in range(N):
        t=d;x=y=0;s=1
        while s<n:
            rx=1&(t//2); ry=1&(t^rx)
            if ry==0:
                if rx==1: x=s-1-x;y=s-1-y
                x,y=y,x
            x+=s*rx;y+=s*ry;t//=4;s<<=1
        pts[d,0]=x;pts[d,1]=y
    return pts

def colormap(t, stops):
    pos=np.array([s[0] for s in stops]); cols=np.array([s[1] for s in stops])
    return np.stack([np.interp(t,pos,cols[:,c]) for c in range(3)],-1)

# bright, non-cyclic hue sweep: a single ~3/4 turn so the two ENDS of the
# thread stay distinct (a directed line) while every colour glows.
PAL=[(0.0,[0.20,0.85,0.95]),(0.20,[0.20,0.95,0.55]),(0.40,[0.75,0.98,0.25]),
     (0.58,[1.0,0.78,0.18]),(0.76,[1.0,0.40,0.30]),(0.90,[1.0,0.30,0.62]),
     (1.0,[0.90,0.45,1.0])]

def render(order, S=2048, ss=2, lw=4, bloom=4.0, glow=0.5, margin_frac=0.022):
    n=1<<order
    pts=hilbert_points(order).astype(np.float64)
    W=S*ss
    m=W*margin_frac
    scale=(W-2*m)/n
    P=(pts+0.5)*scale+m
    N=len(P)
    t=np.linspace(0,1,N)
    col=colormap(t,PAL).astype(np.float32)
    A=P[:-1];B=P[1:]
    K=int(np.ceil(scale))+2
    s=np.linspace(0,1,K)
    XY=A[:,None,:]+s[None,:,None]*(B-A)[:,None,:]
    C=np.repeat(col[:-1][:,None,:],K,axis=1).reshape(-1,3)
    X=XY[...,0].ravel(); Y=XY[...,1].ravel()
    canvas=np.zeros((W*W,3),np.float32)
    for dx in range(-lw,lw+1):
        for dy in range(-lw,lw+1):
            if dx*dx+dy*dy>lw*lw+0.5: continue
            xi=np.clip((X+dx).astype(int),0,W-1)
            yi=np.clip((Y+dy).astype(int),0,W-1)
            idx=yi*W+xi
            for ch in range(3):
                np.maximum.at(canvas[:,ch],idx,C[:,ch])
    canvas=canvas.reshape(W,W,3)
    if bloom>0:
        g=np.stack([gaussian_filter(canvas[...,c],bloom) for c in range(3)],-1)
        canvas=np.clip(canvas+glow*g,0,1)
    img=Image.fromarray((np.clip(canvas,0,1)*255).astype('uint8')).resize((S,S),Image.LANCZOS)
    return img

if __name__=="__main__":
    import sys
    o=int(sys.argv[1]) if len(sys.argv)>1 else 7
    out=sys.argv[2] if len(sys.argv)>2 else 'art_uh5/02_a_line_that_learns_to_be_a_plane.png'
    render(o).save(out)
    print('done',o,out)
