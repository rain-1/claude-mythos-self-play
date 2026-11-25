"""THE COMB — ridgeline engraving of the 1-D run: each line is the population along a road at one moment, later lines in front.
usage: comb.py W out.png"""
import sys, numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont
W=int(sys.argv[1]); OUT=sys.argv[2]; S=W/2048.0; SS=2; WW=W*SS
d=np.load('data/st_t3000.npz'); rows=d['rows'].astype(float); L=float(d['L']); T=float(d['T']); nt,nx=rows.shape
x=np.linspace(-L/2,L/2,nx); keep=np.abs(x)<10.5; rows=rows[:,keep]; x=x[keep]
NL=150; ti=np.linspace(0,nt-1,NL).astype(int)
im=Image.new('RGB',(WW,WW),(244,238,222)); dr=ImageDraw.Draw(im)
mx=0.10*WW; top=0.20*WW; bot=0.80*WW; amp=0.022*WW
ink=(24,34,84); red=(205,52,42)
X=mx+(x-x[0])/(x[-1]-x[0])*(WW-2*mx)
for n,i in enumerate(ti):                 # earliest at the back (top), latest in front (bottom)
    base=top+(bot-top)*n/(NL-1); y=base-amp*rows[i]
    poly=list(zip(X,y))+[(X[-1],base+4*SS),(X[0],base+4*SS)]
    dr.polygon(poly,fill=(244,238,222))
    wdt=int((1.2+1.6*n/NL)*SS*S)
    dr.line(list(zip(X,y)),fill=red if n==0 else ink,width=max(wdt,1),joint='curve')
im=im.resize((W,W),Image.LANCZOS)
a=np.asarray(im).astype(float)/255
r=np.random.default_rng(3).standard_normal((W,W)); a*= (1+0.018*gaussian_filter(r,0.8)/gaussian_filter(r,0.8).std())[...,None]
r2=gaussian_filter(np.random.default_rng(4).standard_normal((W,W)),40*S); a*=(1+0.012*r2/r2.std())[...,None]
im=Image.fromarray((np.clip(a,0,1)*255+.5).astype(np.uint8)); dr=ImageDraw.Draw(im)
F=lambda nm,sz: ImageFont.truetype(f'/usr/share/fonts/truetype/liberation/LiberationSerif-{nm}.ttf',int(sz*S))
pc=(78,78,90); m=int(0.10*W)
dr.text((m,int(0.845*W)),'The Comb',font=F('Regular',50),fill=pc)
dr.text((m,int(0.845*W)+int(64*S)),'One road, 150 moments, the latest in front. Two fronts walk outward at a steady pace; each tooth is born a little',font=F('Italic',24),fill=pc)
dr.text((m,int(0.845*W)+int(96*S)),'more than one earshot from the last and never moves again. A tooth holds two earshots of people; an even crowd holds one.',font=F('Italic',24),fill=pc)
dr.text((m,int(0.845*W)+int(140*S)),'R²/D = 3000: teeth 1.345 R apart, 1.96 R of people in each, so 1.46 times the even crowd.  Red: the first moment.',font=F('Regular',20),fill=pc)
im.save(OUT); print('saved',OUT, rows.shape)
