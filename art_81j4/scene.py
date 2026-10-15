# scene.py — writer for studio.c scenes (spheres + capsules with materials)
import numpy as np, struct
GLASS, CANDY, METAL, EMIT, MATTE = 0, 1, 2, 3, 4
SORBET = dict(strawberry=(1.0,0.60,0.66), coral=(1.0,0.55,0.48), peach=(1.0,0.76,0.58), butter=(1.0,0.91,0.55),
              honey=(1.0,0.82,0.45), lime=(0.80,0.95,0.55), mint=(0.62,0.96,0.80), sky=(0.58,0.82,1.0),
              periwinkle=(0.68,0.72,1.0), lilac=(0.82,0.68,0.98), bubblegum=(1.0,0.66,0.88), rose=(1.0,0.72,0.78),
              white=(0.97,0.97,0.98))
BRASS = (0.95, 0.80, 0.52)
def glass_abs(name_or_rgb, strength=1.0):
    c = SORBET[name_or_rgb] if isinstance(name_or_rgb, str) else name_or_rgb
    return tuple(-np.log(max(v, 1e-3)) * 0.5 * strength for v in c)
class Scene:
    def __init__(s): s.S = []; s.C = []
    def sphere(s, p, r, mat, col, rough=0.0): s.S.append([*p, r, mat, *col, rough])
    def cap(s, a, b, r, mat, col, rough=0.0): s.C.append([*a, *b, r, mat, *col, rough])
    def poly(s, pts, r, mat, col, rough=0.0, closed=False):
        pts = list(pts); n = len(pts)
        for i in range(n if closed else n - 1): s.cap(pts[i], pts[(i + 1) % n], r, mat, col, rough)
    def circle(s, c, R, u, v, r, mat, col, n=160, rough=0.0):
        c, u, v = map(np.asarray, (c, u, v))
        s.poly([tuple(c + R * (np.cos(t) * u + np.sin(t) * v)) for t in np.linspace(0, 2 * np.pi, n, endpoint=False)], r, mat, col, rough, closed=True)
    def save(s, fn):
        with open(fn, 'wb') as f:
            f.write(struct.pack('ii', len(s.S), len(s.C)))
            for r in s.S: f.write(np.array(r, dtype=np.float64).tobytes())
            for r in s.C: f.write(np.array(r, dtype=np.float64).tobytes())
