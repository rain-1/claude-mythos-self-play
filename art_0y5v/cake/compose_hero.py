# Hero compositor: tone-mapped render + caption band + a small top-view diagram of the fair cut.
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '..')
from caption import caption, FI, INK

src = sys.argv[1]; out = sys.argv[2]
img = Image.open(src).convert('RGB')
W, H = img.size
s = W / 4096
title = 'Two of the Three Are Always Twins'
line = ('A round cake cut into three convex pieces with equal cake and equal edge. Apart from the 120° star '
        'there is exactly one such cut, and its two big pieces are mirror images.')
legend = ('Junction 0.60826 r from the centre; arcs 141.6°, 76.7°, 141.6°; each piece πr²/3 with perimeter 4.38808 r. '
          'The areas are equal exactly when the “mean anomalies” t − r·sin t of the three cut ends are evenly spaced, as in Kepler’s equation; '
          'an interval-arithmetic search finds no other fair cut. (MathOverflow 516282 · Phil.SE 142790)')
y0 = int(H * 0.835)
img, yend = caption(img, title, line, legend, int(250 * s), y0, int(2700 * s), scale=s,
                    fade=(int(H * 0.79), int(H * 0.84), (236, 241, 252)))
# inset: top view of the cut, legs in plum ink, pieces tinted
d = ImageDraw.Draw(img)
cx, cy, R = int(3480 * s), int(y0 + 230 * s), int(205 * s)
r0 = 0.60826003; a0 = 0.66964559
P = np.array([-r0, 0.0]); angs = [-a0, a0, np.pi]
tints = [(214, 200, 250), (255, 205, 214), (255, 205, 214)]
rot = np.radians(100)
def tr(v):
    c, s_ = np.cos(rot), np.sin(rot)
    x, y = c * v[0] - s_ * v[1], s_ * v[0] + c * v[1]
    return (cx + R * x, cy - R * y)
for i in range(3):
    a = angs[i]; b = angs[(i + 1) % 3] + (2 * np.pi if i == 2 else 0)
    pts = [tr(P)] + [tr((np.cos(t), np.sin(t))) for t in np.linspace(a, b, 80)]
    d.polygon(pts, fill=tints[i])
d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=INK, width=max(2, int(4 * s)))
for a in angs:
    d.line([tr(P), tr((np.cos(a), np.sin(a)))], fill=INK, width=max(2, int(5 * s)))
rr = int(9 * s)
pp = tr(P); d.ellipse([pp[0] - rr, pp[1] - rr, pp[0] + rr, pp[1] + rr], fill=(240, 120, 110))
img.save(out)
