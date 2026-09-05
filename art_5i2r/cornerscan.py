import numpy as np, json
from cpack_rect import *
region = Leaf(); h = 0.05
mesh = hex_mesh(region, h)
out = []
for sd in np.linspace(0, 2*np.pi, 16, endpoint=False):
    corners, rc, ex = corners_by_harmonic_measure(region, mesh, (0.30,0.20,0.30), start_dir=sd)
    r, th, it, tg = pack_euclid_fast(mesh, corners, verbose=False)
    rc_ = r[corners] / r.mean()
    bdr = r[mesh['boundary']] / r.mean()
    out.append((sd, rc_.max(), rc_.tolist(), bdr.max()))
    print(f'start_dir={sd:.2f} corner radii/mean={np.round(rc_,2)} max boundary coin={bdr.max():.2f}', flush=True)
best = min(out, key=lambda t: t[3])
print('best start_dir', best[0])
