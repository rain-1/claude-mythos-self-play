"""sunprint.py — 'One Print from Two Chains'  (cyanotype; Fable 5.2, day 9)
A chain of 24 beads is bent as a lattice stair (1 = up, 0 = across), turned so that it runs along
the sheet.  Bands 1 and 4: the two chains, one exposure each.  Bands 2 and 3: each chain laid 24
times, every bead in turn on the centre pin, for a 24th of the exposure -- the sum of the doses at
a lattice point is the number of bead pairs with that separation (the chain's tossprint, both
signs).  The chains differ; the prints do not.
usage: sunprint.py SIZE out.png"""
import sys, numpy as np
from PIL import Image, ImageDraw
import cyano
WA = "11011100110110111010101"; WB = "11001101110110101011101"
def pts(w):
    p = [(0, 0)]
    for c in w: p.append((p[-1][0] + (c == '0'), p[-1][1] + (c == '1')))
    return np.array(p, float)
PA, PB = pts(WA), pts(WB)
size = int(sys.argv[1]); out = sys.argv[2]
bh, gap, y0 = 0.150, 0.068, 0.045
boxes = [(0.085, y0 + i * (bh + gap), 0.915, y0 + i * (bh + gap) + bh) for i in range(4)]
sh = cyano.Sheet(size, seed=23, ss=2, coat_box=boxes)
n = size; unit = 0.0226 * n
D = PA[-1]; L = np.hypot(*D); e1 = D / L; e2 = np.array([-e1[1], e1[0]])
def to_xy(P, centre, origin):
    Q = P - origin
    return np.stack([centre[0] + (Q @ e1) * unit, centre[1] - (Q @ e2) * unit], 1)
def draw_chain(d, ss, XY, r, thread=True):
    if thread:
        d.line([tuple(q * ss) for q in XY], fill=225, width=max(1, int(round(0.34 * r * ss))))
    for q in XY:
        d.ellipse([(q[0] - r) * ss, (q[1] - r) * ss, (q[0] + r) * ss, (q[1] + r) * ss], fill=255)
r = 0.33 * unit
cy = [(b[1] + b[3]) / 2 * n for b in boxes]; cx = 0.5 * n
# ---- bands 2, 3: twenty-four exposures of each chain --------------------------------------
N2 = n * 2; acc = np.zeros((N2, N2), np.float32)
for P, yc in ((PA, cy[1]), (PB, cy[2])):
    for i in range(len(P)):
        im, d, ss = sh.canvas()
        draw_chain(d, ss, to_xy(P, (cx, yc), P[i]), r)
        acc += np.asarray(im, np.float32) / 255.0
acc /= 24.0
mean = np.asarray(Image.fromarray(acc).resize((n, n), Image.BOX), np.float32)
sh.lay(np.clip(mean, 0, 1) ** 0.44, opacity=0.97, height=0.5)
# ---- bands 1, 4: the chains themselves ---------------------------------------------------
im, d, ss = sh.canvas()
mid = (PA[0] + PA[-1]) / 2
draw_chain(d, ss, to_xy(PA, (cx, cy[0]), mid), r)
draw_chain(d, ss, to_xy(PB, (cx, cy[3]), mid), r)
sh.lay(sh.to_mask(im), opacity=0.97, height=0.6, halo=0.22)
sh.expose()
labs = ['a chain of 24 beads, bent  up up across up up up across across up up across up up across up up up across up across up across up',
        'that chain laid 24 times, each bead in turn on the centre pin, a 24th of the afternoon each',
        'the other chain, printed the same way: the same print, mark for mark',
        'the other chain: the same six flights of four beads, but the links that join them turn the other way']
for b, t in zip(boxes, labs):
    sh.text(t, (0.5, b[3] + 0.030), 14.2)
sh.text('One Print from Two Chains', (0.5, 0.925), 30)
sh.text('where a mark is paler, more pairs of beads stand that far apart: 276 pairs in each chain, and the two tallies agree', (0.5, 0.958), 14.5)
# one red stamp: an equals sign between the two prints, in the left margin
eq = np.zeros((n, n), np.float32)
ex, ey = int(0.047 * n), int((boxes[1][3] + boxes[2][1]) / 2 * n); w_, t_ = int(0.012 * n), max(2, int(0.0032 * n))
for dy in (-int(0.0055 * n), int(0.0055 * n)):
    eq[ey + dy - t_:ey + dy + t_, ex - w_:ex + w_] = 1
sh.stamp(eq)
sh.develop()
sh.save(out)
