# Several lattice-point soap bubbles on one sheet of paper (go-deeper companion of the hero).
import numpy as np, sys
from scipy.spatial import cKDTree, SphericalVoronoi
from PIL import Image
from render_foam import shade, rot, PAPER, E

def render(bubbles, W=2560, H=2560, ss=2, out='_bubbles.png', strip=128):
    B=[]
    for b in bubbles:
        n=b['n']; U=E(n).astype(float)/n
        area=SphericalVoronoi(U).calculate_areas()
        P=dict(dome=0.35,thick=(250,700),mix=0.25,tk=0.10,ak=0.10,bw=0.9)
        P.update(b.get('kw',{}))
        Rp=b['r']*W; P['px']=1.0/Rp; P['sc']=W/1024*b['r']/0.34; P['bw']*=P['sc']**0.5
        B.append(dict(U=U,area=area,tree=cKDTree(U),R=rot(*b['tilt']),P=P,cx=b['cx']*W*ss,cy=b['cy']*H*ss,Rp=Rp*ss))
    Ws,Hs=W*ss,H*ss; img=np.empty((Hs,Ws,3),np.float32); xx=np.arange(Ws)
    for y0 in range(0,Hs,strip):
        yy=np.arange(y0,min(Hs,y0+strip)); X,Y=np.meshgrid(xx,yy)
        bg=np.ones(X.shape+(3,))*PAPER
        for b in B:   # shadows first
            sx=(X-b['cx'])/(0.85*b['Rp']); sy=(Y-(b['cy']+1.15*b['Rp']))/(0.11*b['Rp']); q=np.hypot(sx,sy)
            bg=bg*(1-0.10*np.exp(-q**2)[...,None]*np.array([0.45,0.5,0.15]))
            bg=bg+0.035*np.exp(-((q-0.55)/0.12)**2)[...,None]*np.array([1.0,0.85,0.9])
        for b in sorted(B,key=lambda b:b['Rp']):   # small bubbles behind? draw big last
            x=(X-b['cx'])/b['Rp']; y=-(Y-b['cy'])/b['Rp']; ins=x*x+y*y<1
            if ins.any():
                bg[ins]=shade(x[ins],y[ins],b['U'],b['area'],b['tree'],b['R'],b['P'])
        img[y0:y0+len(yy)]=bg
    im=Image.fromarray((np.clip(img,0,1)**(1/2.2)*255).astype(np.uint8))
    if ss>1: im=im.resize((W,H),Image.LANCZOS)
    im.save(out); return im

TRIO=[dict(n=25,  cx=0.115,cy=0.700,r=0.0255,tilt=(0.3,0.5,0.1)),
      dict(n=125, cx=0.20, cy=0.625,r=0.057,tilt=(0.5,0.3,0.2)),
      dict(n=625, cx=0.355,cy=0.50, r=0.128,tilt=(0.2,0.7,0.1)),
      dict(n=3125,cx=0.665,cy=0.37, r=0.285,tilt=(0.42,0.63,0.17))]
if __name__=="__main__":
    W=int(sys.argv[1]); render(TRIO,W=W,H=W,ss=int(sys.argv[2]),out=sys.argv[3])
