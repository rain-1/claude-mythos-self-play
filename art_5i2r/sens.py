import numpy as np, json, sys
from cpack_rect import *
def run(h, region, dirs):
    P = build(h, region=region, corner_dirs=dirs, verbose=False, ncert=300)
    c = P['cert']; return {k: round(float(c[k]),5) for k in ('modulus_discrete','modulus_exact','modulus_rel_err','map_err_mean','map_err_relative_to_width')} | {'corners': c['corners'], 'sym': c['map_symmetry']}
print('leaf h=0.05 base      ', run(0.05, Leaf(), (0.35,1.9,3.4,5.0)))
print('leaf h=0.05 dirs+0.05 ', run(0.05, Leaf(), (0.40,1.95,3.45,5.05)))
print('leaf h=0.05 dirs+0.15 ', run(0.05, Leaf(), (0.50,2.05,3.55,5.15)))
print('leaf h=0.035 base     ', run(0.035, Leaf(), (0.35,1.9,3.4,5.0)))
mild = Leaf(terms=((2,0.10,1.2),))
print('mild h=0.05           ', run(0.05, mild, (0.35,1.9,3.4,5.0)))
print('mild h=0.025          ', run(0.025, mild, (0.35,1.9,3.4,5.0)))
