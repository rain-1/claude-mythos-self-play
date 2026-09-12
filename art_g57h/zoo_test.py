"""zoo_test.py — rescale candidate Lenia species x2 (through an evolved field), run them long,
record survival / trajectory / a strobe thumbnail of the trail each would paint."""
import json, sys, time
import numpy as np
from fractions import Fraction
from scipy.ndimage import zoom
from PIL import Image
from lenia import Lenia, rle2arr

d = json.load(open('animals.json'))


def get(code):
    for a in d:
        if a.get('code') == code:
            return a


def seed_field(a, scale, settle=300):
    p = a['params']; beta = tuple(float(Fraction(b)) for b in str(p['b']).split(','))
    P0 = rle2arr(a['cells'])
    L1 = Lenia(512, R=p['R'], T=p['T'], mu=p['m'], sigma=p['s'], beta=beta); L1.place(P0, 256, 256); L1.step(settle)
    A = L1.A; ys, xs = np.nonzero(A > 0.02)
    if len(ys) == 0:
        return None, beta
    cy, cx = int(ys.mean()), int(xs.mean()); m = int(3 * p['R']) + 4
    crop = A[max(0, cy - m):cy + m, max(0, cx - m):cx + m]
    if scale != 1:
        crop = np.clip(zoom(crop, scale, order=3), 0, 1)
    return crop, beta


codes = sys.argv[1].split(',')
N = int(sys.argv[2]); steps = int(sys.argv[3]); scale = float(sys.argv[4])
out = {}
for c in codes:
    a = get(c); p = a['params']
    t0 = time.time()
    crop, beta = seed_field(a, scale)
    if crop is None:
        print(c, 'seed died'); continue
    R = int(round(p['R'] * scale))
    L = Lenia(N, R=R, T=p['T'], mu=p['m'], sigma=p['s'], beta=beta); L.place(crop, N // 2, N // 2)
    strobe = np.zeros((N, N), np.float32); cs = []; ms = []
    stride = 10
    for k in range(steps // stride):
        L.step(stride)
        strobe += L.A * (0.3 + 0.7 * k / (steps // stride))
        cs.append(L.centroid()); ms.append(L.mass())
    cs = np.array(cs); dif = np.diff(cs, axis=0); dif = (dif + N / 2) % N - N / 2
    path = np.cumsum(np.vstack([[0, 0], dif]), axis=0); seg = np.hypot(dif[:, 0], dif[:, 1])
    alive = ms[-1] > 0.3 * ms[0] and ms[-1] < 3 * ms[0]
    info = dict(R=R, mass0=float(ms[0]), mass1=float(ms[-1]), alive=bool(alive), speed=float(seg.sum() / steps),
                extent=[float(np.ptp(path[:, 0])), float(np.ptp(path[:, 1]))], net=float(np.hypot(*dif.sum(0))),
                seconds=time.time() - t0)
    out[c] = info
    print(c, a['name'], info, flush=True)
    im = np.clip(strobe / max(strobe.max(), 1e-9), 0, 1) ** 0.5
    Image.fromarray((255 - 255 * im).astype(np.uint8)).resize((512, 512)).save(f'zoo_{c.replace("+","p")}.png')
json.dump(out, open(f'zoo_test_{int(scale)}.json', 'w'), indent=1)
