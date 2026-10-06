import numpy as np
from PIL import Image, ImageDraw
from beam import trace
balls = [dict(c=np.array([-2.4, 0.6, 1.0]), r=1.0, kind='lune'), dict(c=np.array([0.1, -1.5, 1.0]), r=1.0, kind='fish'),
         dict(c=np.array([2.2, 0.9, 1.0]), r=1.0, kind='eaton')]
res = []
for y0 in np.linspace(-8, 8, 1601):
    for ang in np.linspace(-1.2, 1.2, 481):
        o = np.array([-9.0, y0, 1.0]); d = np.array([np.cos(ang), np.sin(ang), 0])
        segs, seq = trace(balls, o, d)
        if tuple(seq[:5]) == (0, 1, 2, 1, 0):
            res.append((y0, ang, seq))
print(len(res))
# cluster
im = Image.new('RGB', (1200, 1200), 'white'); dr = ImageDraw.Draw(im)
S = lambda p: (600 + p[0] * 60, 600 - p[1] * 60)
for B in balls: c = S(B['c']); dr.ellipse([c[0]-60, c[1]-60, c[0]+60, c[1]+60], outline='gray')
cols = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'magenta', 'cyan']
import itertools
picked = res[::max(1, len(res)//8)][:8]
for k, (y0, ang, seq) in enumerate(picked):
    segs, _ = trace(balls, np.array([-9.0, y0, 1.0]), np.array([np.cos(ang), np.sin(ang), 0]))
    for s in segs:
        pts = s[1]; dr.line([S(p) for p in pts], fill=cols[k], width=2)
    print(k, cols[k], round(y0, 3), round(ang, 4), seq)
im.save('protos/beams.png')
