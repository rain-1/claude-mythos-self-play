"""recolour a render_coxeter density stack: overlap COUNT -> one sorbet ramp (no hue mixing)."""
import sys, numpy as np
from PIL import Image
from sorbet import absorb, Sheet
src, out = sys.argv[1], sys.argv[2]
ARG = dict(a.split('=', 1) for a in sys.argv[3:]); P = lambda k, d: type(d)(ARG.get(k, d))
A = np.load(src + '_A.npy').astype(np.float32); E = np.load(src + '_E.npy').astype(np.float32)
c = A.sum(-1); c = c / np.percentile(c[c > 0], 99.5)
ramp = [absorb(t) for t in P('ramp', 'sky,periwinkle,lilac,bubblegum,strawberry').split(',')]
u = np.clip(c, 0, 1) ** P('gam', 0.7) * (len(ramp) - 1)
i = np.clip(u.astype(int), 0, len(ramp) - 2); t = (u - i)[..., None]
R = np.stack(ramp)
ab = (1 - t) * R[i] + t * R[i + 1]
S = A.shape[0]
sh = Sheet(S, S, seed=3)
sh.wash_rgb(ab * (P('k', 0.9) * np.clip(c, 0, 1.3) ** P('dg', 0.6))[..., None])
dmax = P('dmax', 1.7)
AA = dmax * (1 - np.exp(-sh.A / dmax))
lin = np.clip(sh.paper * np.exp(-AA), 0, 1)
e = (P('edge', 0.5) * (1 - np.exp(-P('ek', 1.0) * E)))[..., None]
lin = lin + (1 - lin) * e
srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
Image.fromarray(np.clip(srgb * 255 + 0.5, 0, 255).astype(np.uint8)).save(out)
