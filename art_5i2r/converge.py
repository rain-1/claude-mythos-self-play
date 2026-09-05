import numpy as np, json
from cpack_rect import *
rows = []
for h in (0.1, 0.05, 0.025, 0.0125):
    P = build(h, verbose=False, ncert=800)
    c = P['cert']
    row = {k: c[k] for k in ('h','V','iters','max_angle_err','max_tangency_rel','boundary_off_rectangle_max','modulus_discrete','modulus_exact','modulus_rel_err','map_err_mean','map_err_max','map_err_relative_to_width','mfs_boundary_resid','k')}
    rows.append(row); print(json.dumps(row, default=str), flush=True)
    json.dump(rows, open('convergence_table.json','w'), indent=1, default=str)
