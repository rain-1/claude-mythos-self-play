"""Temporal ignition: one pinwheel spun up while a rolling-shutter camera films it (k = turns per frame)."""
import numpy as np
from PIL import Image
from paint import SORBET, paint_pinwheel, paint_hub, caption
S, OUT = 2, 512
W = OUT*S
frames = []
nF = 180
ks = 2.6*(np.linspace(0, 1, nF)**2)
phase = 0.0
Y, X = np.mgrid[0:W, 0:W].astype(np.float32)
cols = [SORBET[c] for c in ['strawberry', 'peach', 'butter', 'mint', 'sky', 'lilac']]
for f, k in enumerate(ks):
    img = np.ones((W, W, 3), np.float32)*np.array([0.99, 0.985, 0.975], np.float32)
    paint_pinwheel(img, X, Y, W/2, W/2, W*0.43, 6, k, W, cols, phase=phase, ink=1.5*S)
    paint_hub(img, X, Y, W/2, W/2, W*0.035, SORBET['butter'], ink=1.5*S)
    if 2*np.pi*k*0.43 > 1:
        rs = W/(2*np.pi*k); r = np.hypot(X - W/2, Y - W/2); ang = np.arctan2(Y - W/2, X - W/2)
        a = (np.clip(1 - np.abs(r - rs)/(1.4*S), 0, 1)*np.clip((np.sin(ang*30) + 0.2)*3, 0, 1))[..., None]
        img = img*(1 - 0.9*a) + SORBET['coral']*0.9*a
    im = Image.fromarray((np.clip(img, 0, 1)*255).astype(np.uint8)).resize((OUT, OUT), Image.LANCZOS)
    caption(im, 14, OUT - 30, [(f'{k:.2f} turns per frame', 'i', 16)])
    frames.append(im.convert('P', palette=Image.ADAPTIVE, colors=128))
    phase += 2*np.pi*k + 0.06          # the blades really move between frames (plus a slow drift)
frames += [frames[-1]]*20
frames[0].save('ignition.gif', save_all=True, append_images=frames[1:], duration=60, loop=0, optimize=True)
print('gif', len(frames))
