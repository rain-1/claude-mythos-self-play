import numpy as np, json
from cpack_rect import *
class Disc(Leaf):
    def __init__(self): self.terms=()
for h in (0.1, 0.05):
    P = build(h, region=Disc(), verbose=False, ncert=400)
    c = P['cert']
    print(h, {k: c[k] for k in ('V','modulus_discrete','modulus_exact','modulus_rel_err','map_err_max','map_err_mean','map_err_relative_to_width','map_symmetry','corner_vertex_off_boundary')})
