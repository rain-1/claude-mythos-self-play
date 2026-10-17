"""Specimen tray of permutation-Wordle games (MO 497111), n = 4: every secret, the optimal strategy's guesses as rows
of beads (row 1 nearest the viewer), value = colour; a bead the secret confirms is clear glass, a miss is frosted candy.
Writes scene.bin + tex.f32 (printed compartments on the paper) for sticks.c."""
import numpy as np, json, struct, sys
from PIL import Image, ImageDraw, ImageFilter
n=int(sys.argv[1]) if len(sys.argv)>1 else 4
G=json.load(open('games_n%d.json'%n))
items=sorted(G.items(),key=lambda kv:(len(kv[1]),kv[0]))
cols,rows=(6,4) if n==4 else (12,10)
R=0.42; SP=1.0; BW=n*SP; BD=n*SP; GX=BW+1.5; GY=BD+1.6
HUE={0:(1.00,0.62,0.66),1:(1.00,0.86,0.52),2:(0.56,0.90,0.74),3:(0.62,0.72,1.00),4:(0.86,0.66,1.00)}
sph=[]
X0=-(cols*GX-1.5)/2; Y0=-(rows*GY)/2
boards=[]
GX=BW+1.0; GY=BD+1.0
X0=-(cols*GX-1.0)/2; Y0=-(rows*GY-1.0)/2
for idx,(sec,game) in enumerate(items):
    ci,ri=idx%cols,idx//cols
    bx=X0+ci*GX; by=Y0+(rows-1-ri)*GY          # reading order from the back row: short games far, long games near
    L=len(game); boards.append((bx,by,L))
    for t,(perm,fb) in enumerate(game):
        y=by+(n-L+t)*SP+SP/2                   # rows end at the back edge of the compartment: final row aligned
        for i,v in enumerate(perm):
            x=bx+i*SP+SP/2; hit=(fb>>i)&1; c=np.array(HUE[v])
            if hit: sph.append([x,y,R,R,0,*(1.25*(1-c)+0.03),0])
            else:   sph.append([x,y,R*0.56,R*0.56,1,*(0.55*c+0.46),0])
with open('scene.bin','wb') as f:
    f.write(struct.pack('ii',len(sph),0))
    for s in sph: f.write(struct.pack('9d',*s))
# printed paper: rounded compartments, row ticks
y0=float(sys.argv[2]) if len(sys.argv)>2 else 40
TS=0.02; xa,xb=X0-3,X0+cols*GX+1.5; ua,ub=(Y0-3)-y0,(Y0+rows*GY+3)-y0
TW,TH=int((xb-xa)/TS),int((ub-ua)/TS)
im=Image.new('RGB',(TW,TH),(255,255,255)); d=ImageDraw.Draw(im)
def P(x,y): return ((x-xa)/TS,((y-y0)-ua)/TS)
for bx,by,L in boards:
    a=P(bx-0.35,by-0.35); b=P(bx+BW+0.35,by+BD+0.35)
    TINT={1:(255,206,196),2:(252,234,190),3:(206,240,222),4:(208,222,252),5:(234,212,252)}
    oc=(255,140,120) if L in (1,n) else (216,204,234)
    d.rounded_rectangle([a[0],a[1],b[0],b[1]],radius=0.5/TS,fill=TINT[L],outline=oc,width=int(0.06/TS))
    for t in range(n):
        p=P(bx-0.18,by+t*SP+SP/2); r=0.07/TS
        d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=(225,214,240) if t>=n-L else (240,236,246))
im=im.filter(ImageFilter.GaussianBlur(1.2))
T=np.asarray(im).astype(np.float32)/255
with open('tex.f32','wb') as f:
    f.write(struct.pack('ii',TW,TH)); f.write(struct.pack('3d',xa,ua,TS)); f.write(T.astype(np.float32).tobytes())
print(len(sph),'beads; tray extent x',X0,X0+cols*GX,'y',Y0,Y0+rows*GY)
