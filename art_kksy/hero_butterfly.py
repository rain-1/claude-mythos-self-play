#!/usr/bin/env python3
"""Hero: compute at 8192x8192, tone, LANCZOS-downscale to 4096."""
import numpy as np, time
from PIL import Image
from butterfly import compute_maps, verify
from render_butterfly import colorize

t0 = time.time()
verify()
S = 8192
label, cov, dist, qs = compute_maps(S, S, qcap=600)
np.save("/tmp/bfly_label_8192.npy", label)
np.save("/tmp/bfly_cov_8192.npy", cov.astype(np.float16))
np.save("/tmp/bfly_dist_8192.npy", dist.astype(np.float16))
print(f"maps done ({time.time()-t0:.1f}s)")
for v in ("A", "B"):
    rgb = colorize(label, cov, dist, v)
    im = Image.fromarray(rgb[::-1])
    im.resize((4096, 4096), Image.LANCZOS).save(f"hero_butterfly_4096_{v}.png")
    im.resize((1024, 1024), Image.LANCZOS).save(f"prev_butterfly_{v}.png")
    del rgb, im
    print(f"saved {v} ({time.time()-t0:.1f}s)")
