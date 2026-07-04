"""Render the six-vertex hero: Byzantine jewel-mosaic of the 6 vertex types.
4 cool ferroelectric corners (frozen) + gold c-vertex 'turns' filling the
temperate ice-sea; the arctic curve is the boundary where the gold vanishes."""
import numpy as np, sys
from scipy.ndimage import gaussian_filter
sys.path.insert(0,'art_eygo'); import common as C
from PIL import Image

tag=sys.argv[1] if len(sys.argv)>1 else "hero512"
OUT=int(sys.argv[2]) if len(sys.argv)>2 else 4096
H=np.load(f"art_eygo/H_{tag}.npy").astype(np.int32)
f00=H[:-1,:-1]; f10=H[1:,:-1]; f11=H[1:,1:]; f01=H[:-1,1:]
s0=f10-f00; s2=f01-f11
isc=(s0*s2>0)
gx=(f10-f00)>0; gy=(f01-f00)>0
code=np.where(isc, 4+((s0>0)), (gx.astype(int)+2*gy.astype(int)))
n=code.shape[0]

# ---- palette by class frequency: 4 cool jewel ferro corners + gold c accents ----
pal=np.array([
 [0.13,0.11,0.42],   # 0 indigo   (TR)
 [0.09,0.27,0.60],   # 1 sapphire (BR)
 [0.07,0.34,0.42],   # 2 teal     (TL)
 [0.26,0.12,0.50],   # 3 violet   (BL)
 [0.98,0.74,0.24],   # 4 c-vertex gold
 [0.92,0.52,0.13],   # 5 c-vertex amber
])
img=pal[code]                                  # (n,n,3) float

# subtle facet sheen: faint iso-height contours give the frozen facets life
Hf=H[:-1,:-1].astype(float)
sh=0.5+0.5*np.sin(Hf*0.11)
img*= (0.93+0.07*sh)[...,None]

# gold shimmer: soft bloom on the c-vertices so the temperate sea glows
cg=isc.astype(float)
glow=C.bloom(cg,(1.0,2.5,6),(0.35,0.22,0.14))
img[...,0]+=glow*0.35; img[...,1]+=glow*0.24; img[...,2]+=glow*0.05

# orient so BL is bottom-left (array is [x,y]); transpose+flip to image coords
img=np.transpose(img,(1,0,2))[::-1]
img=C.filmic(img,1.35)**(1/1.18)

# upscale NEAREST -> crisp mosaic tiles
im=C.to_img(img).resize((OUT,OUT),Image.NEAREST)
im.save(f"art_eygo/01_hero.png"); print("saved 01_hero.png", im.size, "N",n)
