import numpy as np, json, time, sys
from PIL import Image
import quill as Q, sampler as SM
gal = json.load(open('../math_poly/gallery.json'))
counts = {3:2,5:3,7:3,9:3,11:3,13:3,15:3,17:2,19:1,21:1}
polys = []; ns = []
for n, c in counts.items():
    lst = gal[str(n)]
    idx = np.linspace(0, len(lst)-1, c).round().astype(int) if c > 1 else [0]
    # prefer distinct turn strings first
    seen = []; pick = []
    for i, x in enumerate(lst):
        if x['turns'] not in seen and len(pick) < c: seen.append(x['turns']); pick.append(i)
    for i in idx:
        if len(pick) < c and i not in pick: pick.append(int(i))
    for i in pick:
        polys.append(np.array(lst[i]['verts'])); ns.append(n)
polys.insert(12, None); ns.insert(12, 4)
Wout = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
res = 2                       # world pixels per output pixel
f = Wout/4096
S_out = 590*f; g_out = 118*f; top_out = 150*f
tilt = 30; cs = np.cos(np.radians(tilt))
ksz = res*S_out/300           # size scale (proto look at 300 px tiles)
Ww = int(Wout*res); Hw = int(Wout*res/cs)
t = time.time()
H, A, G = SM.build(polys, 5, 5, S_out*res, g_out*res, g_out*res/cs, tilt, ksz/1.0, top_out*res/cs, 12, Ww, Hw)
print('build', time.time()-t, flush=True); t = time.time()
img = Q.render(H, A, tilt_deg=tilt, spp=6, out_w=Wout, out_h=Wout, light=(-0.65,0.30,0.70), amb=(0.62,0.62,0.70),
               sun=(0.75,0.72,0.68), G=G)
print('render', time.time()-t, flush=True)
np.save(f'proto/hero_{Wout}.npy', img)
Image.fromarray(Q.tonemap(img)).save(f'proto/hero_raw_{Wout}.png')
json.dump(ns, open(f'proto/hero_ns.json', 'w'))
