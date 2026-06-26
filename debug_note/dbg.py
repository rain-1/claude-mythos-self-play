"""Render a {7,3} tiling for an ARBITRARY heptagon circumradius, to show the
difference between the buggy (inradius) value and the correct one."""
import numpy as np, math, sys
sys.path.insert(0,'psl168'); sys.path.insert(0,'octonions')
import p168
from PIL import Image, ImageDraw
import colorsys

def Rot(th): return np.array([[np.exp(1j*th/2),0],[0,np.exp(-1j*th/2)]],complex)
def Trans(v):
    s=1/math.sqrt(1-abs(v)**2); return np.array([[s,s*v],[s*np.conj(v),s]],complex)
def mob(M,z): return (M[0,0]*z+M[0,1])/(M[1,0]*z+M[1,1])
def nrm(M):
    a,b=M[0,0],M[0,1]; s=math.sqrt((a*np.conj(a)-b*np.conj(b)).real)
    return np.array([[a,b],[np.conj(b),np.conj(a)]],complex)/s
def key(M): z=mob(M,0); return (round(z.real,3),round(z.imag,3))

def reldefect(Re):
    verts=[Re*np.exp(1j*2*math.pi*k/7) for k in range(7)]
    a=Rot(2*math.pi/7); V0=verts[0]; T=Trans(V0); Ti=Trans(-V0); b=T@Rot(2*math.pi/3)@Ti
    ab=a@b; P=ab@ab; P=P/P[0,0]
    return float(np.max(np.abs(P-np.eye(2))))

def tiling(Re, maxn=260, rmax=0.93):
    verts=[Re*np.exp(1j*2*math.pi*k/7) for k in range(7)]
    a=Rot(2*math.pi/7); ai=Rot(-2*math.pi/7)
    V0=verts[0]; T=Trans(V0); Ti=Trans(-V0)
    b=T@Rot(2*math.pi/3)@Ti; bi=T@Rot(-2*math.pi/3)@Ti
    gens=[a,ai,b,bi]; I=np.eye(2,dtype=complex)
    seen={key(I):I}; frontier=[I]; order=[I]
    while frontier and len(order)<maxn:
        nf=[]
        for M in frontier:
            for g in gens:
                P=nrm(g@M); k=key(P)
                if k not in seen and abs(mob(P,0))<rmax:
                    seen[k]=P; nf.append(P); order.append(P)
        frontier=nf
    return order, verts

def panel(Re, W=760, accent=(120,210,235)):
    tiles,verts=tiling(Re)
    img=Image.new("RGB",(W,W),(7,8,16)); d=ImageDraw.Draw(img,"RGBA")
    cx=cy=W/2; sc=W*0.47; S=lambda z:(cx+z.real*sc,cy-z.imag*sc)
    tiles=sorted(tiles,key=lambda M:-abs(mob(M,0)))
    for M in tiles:
        c=abs(mob(M,0)); hue=(0.55-0.42*min(c,1))%1
        r,g,bl=colorsys.hsv_to_rgb(hue,0.6,1.0); col=(int(r*255),int(g*255),int(bl*255))
        tv=[mob(M,v) for v in verts]
        for k in range(7):
            pts=[S(z) for z in p168.geodesic_arc(tv[k],tv[(k+1)%7],n=16)]
            d.line(pts,fill=col+(220,),width=2,joint="curve")
    # disk boundary
    d.ellipse([cx-sc,cy-sc,cx+sc,cy+sc],outline=(60,66,86,255),width=3)
    return img
