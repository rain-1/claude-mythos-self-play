# render_cza.py — BLUE LEAVES FIRST: the circumzenithal arc shrinking into the zenith as the sun climbs
import numpy as np,sys
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import gaussian_filter
import scene
from scene import *
P=1200;SC=1.75
HS=['22','27','30','31.3','32.2','33.2']
d=cam_dirs(P,P,0,89.999,SC)
rr=np.hypot(*np.meshgrid(np.arange(P)+0.5-P/2,np.arange(P)+0.5-P/2));R=P*0.47
def tone(x,Lw=1.25):
    lum=(x*[0.2126,0.7152,0.0722]).sum(-1,keepdims=True)
    lo=lum*(1+lum/Lw**2)/(1+lum);x=np.clip(x*lo/np.maximum(lum,1e-6),0,1)
    return np.where(x<=0.0031308,12.92*x,1.055*np.power(np.maximum(x,0),1/2.4)-0.055)
maps={h:gaussian_filter(np.fromfile(f'tmp/Z_{h}_cam.f32',np.float32).reshape(P,P,3),(1.6,1.6,0)) for h in HS}
ref=np.percentile(maps['22'][...,1],99.7)
W,H=3*1240+240,2*1300+620
sheet=np.ones((H,W,3))*np.array([0.992,0.985,0.975])
cents=[(120+620+1240*(i%3),110+600+1300*(i//3)) for i in range(6)]
for h,(cx,cy) in zip(HS,cents):
    el=float(h)*D2R;scene.SUN[:]=[np.cos(el),0,np.sin(el)]
    hal=np.clip(maps[h]@XYZ2RGB.T/ref*0.55,0,None)
    lum=(hal*[0.2126,0.7152,0.0722]).sum(-1,keepdims=True);hal=np.clip(lum+(hal-lum)*1.9,0,None)
    rgb=tone(sky_rgb(d)*1.05+hal)
    m=np.clip(R+0.5-rr,0,1)[...,None]
    x0,y0=cx-P//2,cy-P//2;reg=sheet[y0:y0+P,x0:x0+P]
    sh=gaussian_filter(np.clip((R+14)-np.hypot(*np.meshgrid(np.arange(P)+0.5-P/2-6,np.arange(P)+0.5-P/2-14)),0,30)/30,12)[...,None]*0.10
    reg*=(1-sh*np.array([0.55,0.6,0.3]))
    reg[:]=reg*(1-m)+rgb*m
    ring=np.exp(-((rr-R)/1.3)**2)[...,None]*0.5;reg[:]=reg*(1-ring)+np.array([0.42,0.33,0.46])*ring
    # zenith mark
    zm=np.exp(-((rr-7)/1.6)**2)[...,None]*0.6;reg[:]=reg*(1-zm)+np.array([0.95,0.45,0.42])*zm
img=Image.fromarray((np.clip(sheet,0,1)*255+0.5).astype(np.uint8));dr=ImageDraw.Draw(img);plum=(92,77,102)
fT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',44)
fS=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',34)
notes={'22':'the full arc, red outside, violet in','27':'smaller, closer to the zenith','30':'violet thinning',
       '31.3':'violet gone (it left at 30.6°)','32.2':'only the long waves remain','33.2':'gone: even red left at 32.7°'}
for h,(cx,cy) in zip(HS,cents):
    t=f'sun {h}° up';tw=dr.textlength(t,font=fT);dr.text((cx-tw/2,cy+R+30),t,font=fT,fill=plum)
    t=notes[h];tw=dr.textlength(t,font=fS);dr.text((cx-tw/2,cy+R+88),t,font=fS,fill=(120,104,128))
fH=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',72)
fI=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',40)
fM=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',33)
y=H-400
dr.text((150,y),'Blue Leaves First',font=fH,fill=plum)
dr.text((152,y+100),'The circumzenithal arc, the 30° of sky around the zenith (coral dot), as the sun climbs; plate crystals only, 10⁹ rays per disc, one shared exposure.',font=fI,fill=(110,96,120))
dr.text((152,y+160),'Light enters a plate’s top face and leaves through a side face only while cos h ≥ √(n² − 1): the arc sits at elevation arcsin √(n² − cos² h)',font=fM,fill=(130,116,140))
dr.text((152,y+205),'and dies in the zenith at h = 30.6° for violet (n = 1.319), 32.3° for yellow, 32.7° for red (n = 1.307). Each colour has its own last morning.',font=fM,fill=(130,116,140))
img.save(sys.argv[1]);print('ok')
