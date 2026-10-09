import numpy as np
from PIL import Image
from paint import *
S = 2; P = 420; n = 4
W = H = P*n
img = np.ones((H*S, W*S, 3))*np.array([0.99,0.985,0.975])
ks = [0, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 1.5, 2, 3, 4, 6, 8, 12, 16, 24]
for idx, k in enumerate(ks):
    iy, ix = divmod(idx, n)
    y0, x0 = iy*P*S, ix*P*S
    Y, X = np.mgrid[0:P*S, 0:P*S].astype(float)
    sub = img[y0:y0+P*S, x0:x0+P*S]
    N = 5
    cols = [SORBET[WHEEL[(2*i) % 9]] for i in range(N)]
    paint_pinwheel(sub, X, Y, P*S/2, P*S/2, P*S*0.42, N, k, P*S, cols, ink=1.6*S)
    paint_hub(sub, X, Y, P*S/2, P*S/2, P*S*0.05, SORBET['butter'], ink=1.6*S)
im = Image.fromarray((img*255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
im.save('proto_sheet.png')
