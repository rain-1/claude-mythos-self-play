import numpy as np, sys, time
sys.path.insert(0,'/home/user/claude-mythos-self-play/art_i3k3')
from common import *
from scipy.ndimage import gaussian_filter
from PIL import Image
t0=time.time()
OUT=2560; INT=3200; S=INT
cx=0.42; half=2.9
xs=np.linspace(cx-half,cx+half,S); ys=np.linspace(-half,half,S)
X,Y=np.meshgrid(xs,ys); Z=X+1j*Y
# potential of the SECOND iterate: log|f^2|.  Its 9 wells = f^{-2}(0),
# its saddle-passes = where lowering the level R splits one lake into many.
W2=f(f(Z))
g=np.log(np.abs(W2)+1e-12)

def contour(field,d,w):
    fr=np.abs(((field/d)%1.0)-0.5)*2.0
    return np.exp(-(fr/w)**2)
per=0.40
line=contour(g,per,0.12)
fade=np.exp(-np.clip(g-2.2,0,None)*0.42)   # calm the outer rings
img=np.zeros((S,S,3),np.float32)
gline=np.array([1.0,0.66,0.20])
for i in range(3): img[:,:,i]+=(line*fade*gline[i]*0.9).astype(np.float32)

# --- the critical-value separatrix: the exact figure-eight pinch levels ---
# critical points of f^2: f'(z)=0  OR  f(z) in {crit pts of f}
critf=np.roots([9,-6,-3])            # f'(z)=3z^2-2z-3=0
crit2=list(critf)
for c in critf:
    crit2+=list(preim(c))
crit2=np.array([c for c in crit2 if abs(c.imag)<0.05]).real
critvals=np.unique(np.round(np.abs(f(f(crit2+0j))),6))
# draw each critical equipotential (the separatrix through a pass) a touch brighter
for cv in critvals:
    lv=np.log(cv+1e-12)
    band=np.exp(-((g-lv)/0.05)**2)
    for i in range(3): img[:,:,i]+=(band*fade*np.array([1.0,0.86,0.55])[i]*0.85).astype(np.float32)

# blaze the saddle passes themselves (the pinch points)
def star(pts,col,amp,rad):
    for c in pts:
        px=int((c.real-(cx-half))/(2*half)*S); py=int((c.imag+half)/(2*half)*S)
        if rad<=px<S-rad and rad<=py<S-rad:
            for dx in range(-rad,rad+1):
                for dy in range(-rad,rad+1):
                    img[py+dy,px+dx]+=col*amp*np.exp(-(dx*dx+dy*dy)/(rad*0.8))
# saddles = critical points that are NOT wells (passes on the axis)
star(crit2+0j, np.array([1.0,0.93,0.75]), 1.25, 8)
# wells (f^{-2}(0)) as bright seed rings
A2,B2=basin_split(2)
star(A2,GOLD*1.15+0.2,1.0,5); star(B2,CYAN*1.1+0.2,1.0,5)
# origin seed
star(np.array([0+0j]), np.array([1,1,1]),1.0,5)

# bloom
lum=img.mean(2); mask=np.clip((lum-0.45)/0.55,0,1)[...,None]*img
def bloom(a,sig):
    ds=max(1,int(sig/6)); sm=a[::ds,::ds]
    b=gaussian_filter(sm,(sig/ds,sig/ds,0))
    b=np.repeat(np.repeat(b,ds,0),ds,1)[:a.shape[0],:a.shape[1]]
    return gaussian_filter(b,(2,2,0))
img=img+0.6*bloom(mask,70)+0.35*bloom(mask,22)
img=filmic(img,k=1.6,g=0.88)
downscale(img,INT//OUT if INT%OUT==0 else 1).resize((OUT,OUT),Image.LANCZOS).save('/home/user/claude-mythos-self-play/art_i3k3/panelC_watershed.png')
print("saved C",time.time()-t0, "critvals",critvals)
