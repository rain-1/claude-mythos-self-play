"""openai/math family 237: n-step honeycomb self-avoiding walks have diameter n^{3/4+o(1)}.
Four pivot-sampled walks, each shrunk by n^{-3/4}: if the exponent is right they come out the same size."""
import numpy as np, sys
from PIL import Image, ImageDraw
from caption import caption, CORAL, SOFT, F
from PIL import ImageFont
S=int(sys.argv[1]); out=sys.argv[2]
ns=[1000,4000,16000,64000]
SS=2; W=S*SS; H=int(W*1.20)
PAL=np.array([[250,140,160],[255,175,140],[253,214,120],[180,224,140],[130,214,184],[130,196,240],[156,160,240],[196,150,236]],float)
def grad(t):
    h=t*(len(PAL)-1); i=np.minimum(h.astype(int),len(PAL)-2); f=(h-i)[:,None]; return PAL[i]*(1-f)+PAL[i+1]*f
img=Image.new('RGB',(W,H),(252,251,249))
pw=W/2; top=W*0.03
fs=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(W*0.016))
HUES=[np.array([[246,120,146],[253,190,170]]),np.array([[96,200,166],[186,236,206]]),np.array([[128,140,236],[200,196,250]])]
for k,n in enumerate(ns):
    cx=(k%2+0.5)*pw; cy=top+(k//2+0.5)*pw
    sc=pw*0.46/(n**0.75)
    dd=ImageDraw.Draw(img); R=pw*0.44; dd.ellipse([cx-R,cy-R,cx+R,cy+R],outline=(230,220,232),width=max(2,W//1400))
    ee=[]
    for j,seed in enumerate(['', '_11', '_23']):
        A=np.loadtxt(f'proto/saw_{n}{seed}.txt'); x=A[:,0]-A[:,1]/2; y=A[:,1]*np.sqrt(3)/2
        x-=x.mean(); y-=y.mean(); ee.append(np.hypot(x[-1]-x[0],y[-1]-y[0])/n**0.75)
        X=cx+x*sc; Y=cy-y*sc
        t=np.linspace(0,1,n+1)[:,None]; col=(HUES[j][0]*(1-t)+HUES[j][1]*t).astype(int)
        lw=max(2,int(W*0.0026*(1000/n)**0.18))
        for width,alpha,light in ((lw*3,40,0.6),(lw,215,0.0)):
            lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
            pts=list(zip(X,Y))
            seg=max(1,n//4000)
            for i in range(0,n,seg):
                c=col[i]; c=(c+(255-c)*light).astype(int)
                d.line(pts[i:i+seg+1],fill=tuple(c)+(alpha,),width=width,joint='curve')
            img=Image.alpha_composite(img.convert('RGBA'),lay).convert('RGB')
        dd=ImageDraw.Draw(img)
        for (px,py) in ((X[0],Y[0]),(X[-1],Y[-1])):
            r=W*0.004; dd.ellipse([px-r,py-r,px+r,py+r],fill=CORAL,outline=(255,255,255),width=max(1,W//1600))
    lab=f'n = {n:,}   ·   ends apart {np.mean(ee):.2f} n^(3/4) on average'
    tw=dd.textlength(lab,font=fs); dd.text((cx-tw/2,cy+pw*0.455),lab,font=fs,fill=SOFT)
caption(img,W/2,top+2*pw+W*0.035,'Every Length, One Size',
  'self-avoiding walks on the honeycomb, 1,000 to 64,000 steps, each shrunk by n^(3/4): they come out the same size',
  'three pivot-algorithm samples per length, each in its own silk, lightening from start to end  ·  coral: the ends',
  W*0.040,align='center',line3='openai/math family 237 claims Nienhuis’s predicted exponent: diameter n^(3/4 + o(1)); the faint ring is the same in every panel')
img.resize((S,int(H/SS)),Image.LANCZOS).save(out)
