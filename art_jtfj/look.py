import sys, numpy as np
from core import *
from PIL import Image
def field(m,kind,M,box,W,H):
    ds,a,M0=setup(m,kind); M=M0 if M is None else M
    x0,x1,y0,y1=box   # t range (horizontal), sigma range (vertical, up)
    t=np.linspace(x0,x1,W); sg=np.linspace(y1,y0,H)
    S=sg[:,None]+1j*t[None,:]
    return logF(S,ds,a,M)
def show(lf,ph,name,step=1.0):
    h=np.clip(lf/ (8*step),-1,1)
    sea=np.array([20,30,90.]); land=np.array([240,225,190.]);
    img=np.where(lf[...,None]<0, sea+(np.array([120,160,210.])-sea)*(1+h[...,None]), land+(np.array([150,110,90.])-land)*h[...,None])
    c=np.abs(lf/step-np.round(lf/step))<0.04; img[c]*=0.75
    r=np.abs(np.angle(-np.exp(1j*ph)))<0.03; img[r]=[220,40,30]
    Image.fromarray(np.clip(img,0,255).astype(np.uint8)).save(name)
if __name__=='__main__':
    m=5040; rm=np.sqrt(m)
    for nm,kind,M,box in [('div_crit','div',rm,(0,12,-5.5,6.5)),('div_below','div',rm*0.6,(0,12,-5.5,6.5)),('div_asker','div',None,(0,6,-2.5,3.5)),
                          ('ep_crit','ep',rm,(0,12,-5.5,6.5)),('ep_asker','ep',None,(6,12,-2.5,3.5)),('ep_m','ep',float(m),(0,12,-5.5,6.5))]:
        lf,ph=field(m,kind,M,box,900,900); show(lf,ph,'proto/look_%s.png'%nm, 1.0 if 'asker' not in nm else 6.0); print(nm,np.nanmin(lf[np.isfinite(lf)]),np.nanmax(lf[np.isfinite(lf)]))
