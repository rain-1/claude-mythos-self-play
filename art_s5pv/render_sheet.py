# render_sheet.py — FOUR HABITS: the whole sky as a disc for each crystal habit alone, with the crystal in glass
import numpy as np,sys
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import gaussian_filter
from scene import *
import glass_icon as gi
P=1400;SC=0.47
d=cam_dirs(P,P,0,89.999,SC)
gsun=np.degrees(np.arccos(np.clip(d@SUN,-1,1)))
rr=np.hypot(*np.meshgrid(np.arange(P)+0.5-P/2,np.arange(P)+0.5-P/2))
Rh=SC*2*P/2   # horizon radius in px
def tone(x,Lw=1.25):
    lum=(x*[0.2126,0.7152,0.0722]).sum(-1,keepdims=True)
    lo=lum*(1+lum/Lw**2)/(1+lum);x=np.clip(x*lo/np.maximum(lum,1e-6),0,1)
    return np.where(x<=0.0031308,12.92*x,1.055*np.power(np.maximum(x,0),1/2.4)-0.055)
def panel(t,gain,pct):
    a=np.fromfile(f'tmp/S_{t}_cam.f32',np.float32).reshape(P,P,3)
    a[gsun<1.2]=0;a=gaussian_filter(a,(1.4,1.4,0))
    Y=a[...,1];ref=np.percentile(Y[(d[...,2]>0.02)&(gsun>5)],pct)
    h=np.clip(a@XYZ2RGB.T/ref*gain,0,None)
    lum=(h*[0.2126,0.7152,0.0722]).sum(-1,keepdims=True);h=np.clip(lum+(h-lum)*1.9,0,None)
    sky=sky_rgb(d)*1.1+h
    sky+=(3.5*np.exp(-(gsun/0.6)**8)+0.9*np.exp(-gsun/1.5)+0.25*np.exp(-gsun/4.0))[...,None]*np.array([1,0.96,0.86])
    # soft horizon rim: a thin band of snow-lilac at the disc edge
    rgb=tone(sky)
    return rgb
PAPER=np.array([0.992,0.985,0.975])
W,H=3200,3960
sheet=np.ones((H,W,3))*PAPER
yy,xx=np.mgrid[0:H,0:W]
rng=np.random.default_rng(1);sheet*= (1-0.012*gaussian_filter(rng.random((H,W)),1.2)[...,None])
habits=[('R',0.9,99.0,'Tumbling columns','every orientation equally likely','the 22° and 46° halos',np.array([0.35,0.75,0.25]),gi.rotm([1,0.4,0.2],0.7),1.3),
        ('P',0.9,99.6,'Drifting plates','faces level, falling like leaves','sundogs, the circumzenithal arc, the parhelic circle',np.array([0.75,0.35,0.15]),np.eye(3),0.22),
        ('C',0.9,99.3,'Lying columns','axis level, free to spin','the upper and lower tangent arcs',np.array([0.55,0.15,0.45]),gi.rotm([0,1,0],np.pi/2)@gi.rotm([0,0,1],0.25),1.6),
        ('Y',0.9,99.4,'Parry columns','axis level, one face kept flat','the Parry arcs',np.array([0.12,0.40,0.70]),gi.rotm([0,1,0],np.pi/2)@gi.rotm([0,0,1],np.pi/2),1.6)]
cent=[(820,860),(2380,860),(820,2560),(2380,2560)]
fT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',46)
fI=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',40)
fS=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',34)
labels=[]
for (t,g,pc,name,how,draws,tint,Rm,ratio),(cx,cy) in zip(habits,cent):
    rgb=panel(t,g,pc)
    x0,y0=cx-P//2,cy-P//2
    m=np.clip(Rh+0.5-rr,0,1)[...,None]
    # drop shadow under the disc
    sh=np.clip((Rh+18)-np.hypot(*np.meshgrid(np.arange(P)+0.5-P/2-8,np.arange(P)+0.5-P/2-18)),0,40)/40
    sh=gaussian_filter(sh,14)[...,None]*0.10
    reg=sheet[y0:y0+P,x0:x0+P]
    reg*= (1-sh*np.array([0.55,0.6,0.3]))
    reg[:]=reg*(1-m)+rgb*m
    # thin plum ring
    ring=np.exp(-((rr-Rh)/1.4)**2)[...,None]*0.55
    reg[:]=reg*(1-ring)+np.array([0.42,0.33,0.46])*ring
    # glass crystal icon beside the label: world habit seen from 25 deg up, 35 deg round
    V=gi.rotm([1,0,0],-(90-25)*np.pi/180)@gi.rotm([0,0,1],-35*np.pi/180)
    S=250;bound=np.sqrt(4/3+ratio**2);ic,al=gi.render(S,V@Rm,ratio,tint,scale=1.12*bound)
    al=gaussian_filter(al,0.6)[...,None]
    ix,iy=cx-600,cy+P//2+10
    reg2=sheet[iy:iy+S,ix:ix+S]
    sha=gaussian_filter(al[...,0],10);sha=np.roll(np.roll(sha,14,0),8,1)[...,None]*0.16
    reg2*= (1-sha*np.array([0.5,0.55,0.2]))
    reg2[:]=reg2*(1-al)+ic*reg2*al*0.25+ic*al*0.78
    labels.append((cx,cy+P//2+30,name,how,draws))
img=Image.fromarray((np.clip(sheet,0,1)*255+0.5).astype(np.uint8))
dr=ImageDraw.Draw(img);plum=(92,77,102)
for cx,y,name,how,draws in labels:
    dr.text((cx-330,y+50),name,font=fT,fill=plum)
    dr.text((cx-330,y+112),how+',',font=fS,fill=(120,104,128));dr.text((cx-330,y+156),'they draw '+draws,font=fS,fill=(120,104,128))
# caption
fH=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',70)
dr.text((180,3620),'Every Crystal Keeps One Rule',font=fH,fill=plum)
dr.text((182,3720),'The whole sky as a disc (stereographic, zenith at the centre, sun 22° up at the bottom), lit only by one habit of hexagonal ice.',font=fI,fill=(110,96,120))
dr.text((182,3780),'Monte Carlo of 7×10⁸ rays per sky: Fresnel at every face, dispersion n(λ) = 1.3008 + 2969/λ², the sun’s disc 0.53° wide.',font=fS,fill=(130,116,140))
img.save(sys.argv[1]);print('ok')
