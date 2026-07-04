import numpy as np, sys
from scipy.ndimage import gaussian_filter
sys.path.insert(0,'art_eygo'); import common as C
from PIL import Image
dist=np.load("art_eygo/fpp2048_dist.npy"); flow=np.load("art_eygo/fpp2048_flow.npy")
W=dist.shape[0]; fin=np.isfinite(dist); dmax=np.nanmax(dist[fin])
eq=C.histeq(np.log1p(flow)); Lm=np.log1p(flow).max(); lg=np.log1p(flow)/Lm
ds=gaussian_filter(np.where(fin,dist,dmax),3.0); lv=ds/dmax
g=(lv*15)%1.0; ring=np.exp(-(np.minimum(g,1-g)/0.045)**2)*np.clip(1.15-lv,0,1)

def compose(tree, ringcol, ringstr=0.9):
    tb=tree.max(-1)
    gap=np.clip(1.0-tb*1.4,0,1)
    rgb=tree+ringstr*ring[...,None]*ringcol*gap[...,None]
    core=np.zeros((W,W)); cc=W//2; core[cc-1:cc+2,cc-1:cc+2]=1
    gl=C.bloom(core*8+(tb>0.98)*tb,(3,10,34),(0.5,0.35,0.22))
    rgb=rgb+gl[...,None]*np.array([1,0.85,0.55])
    return C.filmic(rgb,1.25)**(1/1.12)

variants={}
# A: raw-log gold (dark bg, sparse bright)
tb=lg**0.8
variants['A_rawlog_gold']=compose(C.ramp([(0,(0,0,0)),(0.4,(0.2,0.1,0.03)),(0.7,(0.9,0.55,0.15)),(0.9,(1,0.83,0.42)),(1,(1,0.98,0.9))],tb), np.array([0.2,0.62,0.95]))
# B: histeq bone-white on black, cool rings
tb=eq**1.5
variants['B_histeq_bone']=compose(C.ramp([(0,(0,0,0)),(0.5,(0.10,0.10,0.13)),(0.8,(0.55,0.52,0.5)),(0.93,(0.93,0.88,0.75)),(1,(1,0.99,0.96))],tb), np.array([0.25,0.6,0.95]))
# C: histeq long dark foot, gold
tb=eq
variants['C_darkfoot_gold']=compose(C.ramp([(0,(0,0,0)),(0.45,(0,0,0)),(0.6,(0.18,0.09,0.03)),(0.78,(0.8,0.43,0.1)),(0.9,(1,0.82,0.4)),(1,(1,0.98,0.9))],tb), np.array([0.25,0.62,0.95]))
# D: cool silver free tree + WARM gold rings (swap)
tb=eq**1.4
variants['D_silver_goldring']=compose(C.ramp([(0,(0,0,0)),(0.5,(0.08,0.10,0.14)),(0.8,(0.45,0.55,0.62)),(0.93,(0.8,0.9,0.98)),(1,(1,1,1))],tb), np.array([1.0,0.72,0.25]))

for k,v in variants.items():
    C.to_img(v).resize((560,560),Image.LANCZOS).save(f"art_eygo/fpptone_{k}.png")
# 2x2 sheet
ks=list(variants); sheet=Image.new('RGB',(1120,1120))
for i,k in enumerate(ks):
    im=Image.open(f"art_eygo/fpptone_{k}.png"); sheet.paste(im,((i%2)*560,(i//2)*560))
sheet.save("art_eygo/fpptone_sheet.png"); print("done", ks)
