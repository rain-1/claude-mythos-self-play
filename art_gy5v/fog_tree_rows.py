"""Histogram rows (2048 bins over [-4,4]) for exact levels 15..22 from tree recursion."""
import numpy as np
from math import lcm
L = lcm(*range(1, 29))
pos = np.array([0], dtype=np.int64); mass = np.array([1.0])
rows = {}
for n in range(1, 23):
    w = L // n
    child = np.concatenate([pos - w, pos + w])
    cmass = np.concatenate([mass, mass])*0.5
    uniq, inv = np.unique(child, return_inverse=True)
    um = np.zeros(len(uniq)); np.add.at(um, inv, cmass)
    pos, mass = uniq, um
    if n >= 15:
        x = pos.astype(np.float64)/L
        hist, _ = np.histogram(x, bins=2048, range=(-4, 4), weights=mass)
        rows[f'r{n}'] = hist.astype(np.float32)
np.savez_compressed('fog_tree_rows.npz', **rows)
print("saved levels 15..22")
