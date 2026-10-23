import numpy as np, sys, time, json
from PIL import Image
from cake import *
W = int(sys.argv[1]); out = sys.argv[2]; spp = int(sys.argv[3]) if len(sys.argv) > 3 else 1
cfg = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
lin = lambda c: (np.array(c)/255.0)**2.2
R = 1.0; H = cfg.get('H', 0.82)
P = np.zeros(24)
P[0]=R; P[1]=H; P[2]=-0.95; P[4]=0.05; P[5]=cfg.get('spr',0.55); P[6]=0.032; P[7]=0.0065
P[8]=3.0; P[9]=2.5; P[10]=1.30
kn=cfg.get('knife',[0.9,-1.95,0.35]); P[11]=kn[0]; P[12]=kn[1]; P[13]=kn[2]
pl=cfg.get('plates',[]);
for i,(x,y) in enumerate(pl): P[14+2*i]=x; P[15+2*i]=y
r0 = 0.60826003; a0 = 0.66964559
p = (-r0, 0.0); angs = [-a0, a0, np.pi]
PC = pieces_from_y(p, angs, cfg.get('gap', 0.09), cfg.get('rot', np.radians(-120)))
LC = lin([[255,170,190],[255,196,160],[255,232,150],[178,230,170],[160,215,240],[200,180,240]])
SC = np.r_[lin([188,232,222]), lin([255,205,214]), lin([205,190,245])]
L = np.array(cfg.get('L', [-0.55, -0.45, 0.70])); L /= np.linalg.norm(L)
cam = look(cfg.get('eye', [0.0, -5.2, 3.6]), cfg.get('tgt', [0, 0.0, 0.1]), cfg.get('fov', 34))
Hh = int(W * cfg.get('aspect', 1.0))
t = time.time()
img = render(W, Hh, cam, P, PC, LC, SC, L, spp, 7, cfg.get('ap', 0.0), cfg.get('focus', 6.0))
print('render', time.time() - t)
np.save(out.replace('.png', '.npy'), img.astype(np.float32)) if cfg.get('save') else None
Image.fromarray(tonemap(img, cfg.get('exp', 1.0))).save(out)
