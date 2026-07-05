"""color.py — colourise cached amoeba density + tropical-spine gap fields.
Palette: deep void (holes) -> indigo flesh -> teal -> gold ridge; the tropical
spine drawn as a bright, thin, cool-white PL skeleton laid over the warm flesh."""
import numpy as np
from PIL import Image
import sys

def ramp(anchors):
    xs=np.array([a[0] for a in anchors])
    cols=np.array([a[1] for a in anchors],float)
    def f(t):
        t=np.clip(t,0,1)
        r=np.interp(t,xs,cols[:,0]); g=np.interp(t,xs,cols[:,1]); b=np.interp(t,xs,cols[:,2])
        return np.stack([r,g,b],-1)
    return f

# flesh palette: near-black indigo -> blue -> teal -> warm gold -> white
FLESH = ramp([
    (0.00,(6,7,20)),
    (0.18,(24,26,64)),
    (0.38,(30,74,120)),
    (0.58,(36,150,150)),
    (0.78,(214,150,58)),
    (0.92,(246,214,140)),
    (1.00,(255,248,232)),
])

def colorize(dens, gap, half, S, spine_w=0.9, spine_gain=0.85,
             dens_gamma=0.80, flesh_gain=1.12, vignette=0.0, bloom=0.0,
             blur_px=0.0, tag='out'):
    from scipy import ndimage
    dd=dens.copy()
    if blur_px>0: dd=ndimage.gaussian_filter(dd,blur_px)
    if vignette>0:
        yy,xx=np.mgrid[0:S,0:S]; r=np.hypot(xx-S/2,yy-S/2)/(S/2)
        dd=dd*np.clip(1.0-vignette*r**1.6,0.12,1.0)
    d=np.clip(dd*flesh_gain,0,1)**dens_gamma
    img=FLESH(d)
    # tropical spine: bright where the top two tropical terms tie (gap ~ 0)
    px=2*half/S
    w=spine_w*px*6
    spine=np.exp(-(gap/ w)**2)
    # keep the skeleton strictly inside the amoeba flesh (no rays into the void)
    supp=ndimage.gaussian_filter((dens>0.03).astype(float),1.5)
    spine=spine*np.clip(supp*1.5,0,1)*spine_gain
    spine_col=np.array([210,228,255],float)
    img=img+spine[...,None]*spine_col*0.9
    # soft bloom on the brightest (gold heart) so it blazes without clipping
    if bloom>0:
        lum=img.mean(2)
        hot=np.clip((lum-160)/95,0,1)[...,None]*img
        for sg in (2.5, 7.0, 16.0):
            img=img+bloom*ndimage.gaussian_filter(hot,(sg,sg,0))*0.5
    img=np.clip(img,0,255)
    Image.fromarray(img.astype(np.uint8)).save(f'{tag}.png')
    print(tag,'saved')

if __name__=='__main__':
    import glob,os
    tags=sys.argv[1:] if len(sys.argv)>1 else [os.path.basename(f)[:-9]
            for f in glob.glob('*_meta.npz')]
    for tag in tags:
        try:
            dens=np.load(f'{tag}_dens.npy'); gap=np.load(f'{tag}_gap.npy')
            meta=np.load(f'{tag}_meta.npz'); half=float(meta['half'])
        except FileNotFoundError:
            print('skip',tag); continue
        colorize(dens,gap,half=half,S=dens.shape[0],tag=f'{tag}_color')
