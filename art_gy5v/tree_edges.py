import numpy as np
from math import lcm
L = lcm(*range(1, 29)); NT = 22
pos = np.array([0], dtype=np.int64); mass = np.array([1.0])
out = {}
for n in range(1, NT+1):
    w = L // n
    child = np.concatenate([pos - w, pos + w])
    cmass = np.concatenate([mass, mass])*0.5
    par = np.concatenate([pos, pos])
    uniq, inv = np.unique(child, return_inverse=True)
    um = np.zeros(len(uniq)); np.add.at(um, inv, cmass)
    out[f'par{n}'] = par.astype(np.float64)/L
    out[f'chi{n}'] = child.astype(np.float64)/L
    out[f'mas{n}'] = cmass
    pos, mass = uniq, um
np.savez_compressed('tree_edges.npz', **out)
print("saved, final level", len(pos))
