# render_clocks.py — every zero-sum part of U as a spiral thread that winds w whole turns and comes home to noon
import numpy as np,sys,itertools
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import gaussian_filter
p=10567;M=p**3;U0=3697
res=[int(l) for l in open('zerosum/res.txt')]
parts=[list(map(int,l.split()[1:])) for l in open('zerosum/sets.txt') if len(l.split())<=7]
for s in parts: assert sum(res[e] for e in s)%M==0
parts.sort(key=lambda s:(len(s),sum(res[e] for e in s)//M,min(s)))
parts.append(list(range(629)))
N=len(parts);print('parts',N)
# sorbet wheel by position k in U (warm -> cool)
WHEEL=np.array([[0.96,0.52,0.60],[0.99,0.68,0.55],[1.0,0.84,0.52],[0.80,0.90,0.52],[0.55,0.88,0.72],[0.52,0.80,0.96],[0.62,0.66,0.98],[0.78,0.62,0.96],[0.96,0.62,0.86]])
def wheel(t):
    t=np.clip(t,0,1)*(len(WHEEL)-1);i=np.minimum(t.astype(int),len(WHEEL)-2);f=(t-i)[...,None]
    return WHEEL[i]*(1-f)+WHEEL[i+1]*f
SS=2
COLS=11;CELL=340;W=COLS*CELL+2*170;rows=int(np.ceil((N-1)/COLS))
BIG=900
H=170+rows*CELL+60+BIG+520
img=Image.new('RGB',(W*SS,H*SS),(253,251,249));dr=ImageDraw.Draw(img)
plum=(92,77,102)
def order(s):
    return sorted(s)          # natural order of k: the steps look like noise
def dial(cx,cy,R,s,big=False):
    cx*=SS;cy*=SS;R*=SS
    s=order(s);fr=[res[e]/M for e in s];w=int(round(sum(fr)))
    # plate + shadow
    sh=6*SS
    dr.ellipse((cx-R+sh*0.5,cy-R+sh,cx+R+sh*0.5,cy+R+sh),fill=(236,232,242))
    wt=int(round(sum(res[e] for e in s)/M));pc=wheel(np.array(min(wt-2,4)/4.0 if not big else 0.5))
    plate=tuple(int(255*(0.93+0.07*v)) for v in pc)
    dr.ellipse((cx-R,cy-R,cx+R,cy+R),fill=plate,outline=tuple(int(255*v*0.85) for v in (0.8+0.2*pc)),width=max(1,SS))
    # hour ticks
    for h in range(12):
        a=2*np.pi*h/12;r1,r2=R*0.92,R*0.98
        dr.line((cx+r1*np.sin(a),cy-r1*np.cos(a),cx+r2*np.sin(a),cy-r2*np.cos(a)),fill=(205,196,214),width=SS)
    # spiral: cumulative turns c in [0,w]; radius shrinks from 0.86R to rmin
    r0,r1=0.86*R,(0.22 if not big else 0.12)*R
    cum=np.concatenate([[0],np.cumsum(fr)])
    tot=cum[-1]
    pts=[];cols=[]
    for j in range(len(s)):
        ts=np.linspace(cum[j],cum[j+1],max(8,int((cum[j+1]-cum[j])*(400 if big else 160))))
        rr=r0+(r1-r0)*ts/tot;a=2*np.pi*ts
        c=wheel(np.array((s[j])/628.0))
        P=np.stack([cx+rr*np.sin(a),cy-rr*np.cos(a)],-1)
        col=tuple(int(255*v) for v in (c*0.80))
        dr.line([tuple(q) for q in P],fill=col,width=int((4.6 if big else 4.2)*SS),joint='curve')
        pts.append(P[-1]);cols.append(c)
    # beads at the end of each step
    br=(15 if big else 11)*SS
    for j,(q,c) in enumerate(zip(pts,cols)):
        last=j==len(pts)-1
        if last:
            dr.ellipse((q[0]-br*1.35,q[1]-br*1.35,q[0]+br*1.35,q[1]+br*1.35),fill=(244,128,112),outline=(196,84,84),width=SS)
        else:
            col=tuple(int(255*v) for v in c)
            dr.ellipse((q[0]-br,q[1]-br,q[0]+br,q[1]+br),fill=col,outline=tuple(int(255*v*0.78) for v in c),width=SS)
            dr.ellipse((q[0]-br*0.55,q[1]-br*0.62,q[0]-br*0.05,q[1]-br*0.15),fill=tuple(int(255*min(1,v*0.4+0.62)) for v in c))
    # start mark at noon on the rim
    dr.ellipse((cx-4*SS,cy-r0-4*SS,cx+4*SS,cy-r0+4*SS),fill=(196,84,84))
    return w
fS=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',22*SS)
ws=[]
for i,s in enumerate(parts[:-1]):
    r,c=divmod(i,COLS);cx=170+CELL*c+CELL//2;cy=170+CELL*r+CELL//2
    w=dial(cx,cy,CELL*0.40,s);ws.append(w)
    lab=f"{len(s)} reciprocals · {w} turn"+("s" if w>1 else "")
    tw=dr.textlength(lab,font=fS);dr.text((cx*SS-tw/2,(cy+CELL*0.43)*SS),lab,font=fS,fill=(140,124,150))
cy=170+rows*CELL+60+BIG//2;w=dial(W//2,cy,BIG*0.46,parts[-1],big=True)
fT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',70*SS)
fI=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',38*SS)
fM=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',31*SS)
lab=f"and the whole interval: all 629 reciprocals, {w} turns, home at noon"
tw=dr.textlength(lab,font=fS);dr.text((W//2*SS-tw/2,(cy+BIG*0.49)*SS),lab,font=fS,fill=(140,124,150))
y=H-420
dr.text((170*SS,y*SS),sys.argv[3] if len(sys.argv)>3 else 'Seventy-Seven Threads Come Home at Noon',font=fT,fill=plum)
dr.text((172*SS,(y+100)*SS),"Every subset of {1/3697, …, 1/4325} with at most six members that sums to 0 modulo 10567³: one of five, seventy-six of six, none smaller (MathOverflow 515850).",font=fI,fill=(110,96,120))
dr.text((172*SS,(y+160)*SS),"Each is a thread on a clock whose full turn is 10567³; each step advances by one reciprocal, taken in order of k, beads coloured by k (warm 3697 → cool 4325).",font=fM,fill=(130,116,140))
dr.text((172*SS,(y+210)*SS),"The steps look like noise; every thread still lands on noon after whole turns (coral). This census alone caps any partition of the 629 into zero-sum parts at 94.",font=fM,fill=(130,116,140))
img=img.resize((W,H),Image.LANCZOS);img.save(sys.argv[2]);print('saved',W,H,'turns',np.bincount(ws))
