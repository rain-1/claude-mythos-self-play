#!/usr/bin/env python3
"""Data for piece 2: pencil eigenvalue rain at n=10 over many random perms +
the bottom-ladder family + extreme approach to the forbidden disk."""
import numpy as np, json
from scipy.linalg import eig

n = 10
A = np.abs(np.subtract.outer(np.arange(n), np.arange(n))).astype(float)
detA = abs(np.linalg.det(A))
rng = np.random.default_rng(99)
NS = 400000
mus = np.empty((NS, n), complex)
dets = np.empty(NS)
disp = np.empty(NS, np.int32)          # total displacement sum |pi(i)-i|
floor_ = (n-1) * 4.0**(n-1)
for k in range(NS):
    p = rng.permutation(n)
    B = np.abs(np.subtract.outer(p, p)).astype(float)
    mu = eig(A, B, right=False)
    mus[k] = mu
    dets[k] = abs(detA * np.prod(1 + mu)).real
    disp[k] = np.abs(p - np.arange(n)).sum()
    if k % 50000 == 0: print(k, flush=True)
np.savez_compressed("manh_rain.npz", mus=mus, dets=dets, disp=disp)
print("min |mu+1|:", np.min(np.abs(mus + 1)))
print("min det/floor:", dets.min()/floor_)

# ladder family: adjacent transposition tau_k and double transpositions
lad = {}
for k in range(n-1):
    p = np.arange(n); p[k], p[k+1] = p[k+1], p[k]
    B = np.abs(np.subtract.outer(p, p)).astype(float)
    mu = eig(A, B, right=False)
    D = A + B
    lad[f"tau_{k}"] = {"mu": [[float(m.real), float(m.imag)] for m in mu],
                       "det": float(abs(np.linalg.det(D)))}
json.dump(lad, open("manh_ladder.json", "w"))
print("ladder done")
