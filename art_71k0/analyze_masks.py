"""Atlas 41: does residue-class refinement explain the fence deficit?
For each gap g: patterns (n, 128-bit window mask) from diag2.
Models for P(occ = 0):
  M0: aggregate independence  prod_j (1 - qbar_j)
  M_c(M): class mixture       sum_{c mod M} w_c prod_j (1 - q_j^c)
Observed: W5/C5.
Classes tested: mod 8, 16, 32, 64, then x3, x9, x5 refinements.
Also: pairwise correlation check within the best class model (residual)."""
import numpy as np, json

def load(g):
    raw = np.fromfile(f"diag2_g{g}.bin", dtype=np.uint64).reshape(-1, 3)
    n = raw[:, 0]
    m0, m1 = raw[:, 1], raw[:, 2]
    offs = np.array([j for j in range(1, 4*g) if j % g != 0])
    bits = np.zeros((len(n), len(offs)), np.uint8)
    for k, j in enumerate(offs):
        if j < 64: bits[:, k] = (m0 >> np.uint64(j)) & np.uint64(1)
        else:      bits[:, k] = (m1 >> np.uint64(j-64)) & np.uint64(1)
    return n, bits, offs

def indep_P0(bits):
    q = bits.mean(0)
    return np.prod(1 - q)

def class_P0(n, bits, M):
    cls = n % M
    P0, wtot = 0.0, 0
    sizes = []
    for c in np.unique(cls):
        sel = cls == c
        k = sel.sum(); sizes.append(k)
        q = bits[sel].mean(0)
        P0 += k * np.prod(1 - q)
        wtot += k
    return P0 / wtot, len(sizes), int(np.min(sizes))

results = {}
for g in [14, 15, 16, 17, 18]:
    n, bits, offs = load(g)
    C5 = len(n)
    occ = bits.sum(1)
    obs0 = int((occ == 0).sum())
    r = dict(C5=C5, obs0=obs0, obs_rate=obs0/C5)
    r['M0'] = float(indep_P0(bits))
    for M in [8, 16, 32, 64, 24, 48, 96, 192, 288, 576, 1440]:
        p0, ncls, minsz = class_P0(n, bits, M)
        r[f'mod{M}'] = float(p0)
        r[f'mod{M}_minclass'] = minsz
    results[g] = r
    print(f"g={g}: C5={C5} observed occ0={obs0} rate={obs0/C5:.3e}")
    print(f"   M0(indep)={r['M0']:.3e}  E={C5*r['M0']:.1f}")
    for M in [8, 16, 32, 64, 24, 48, 96, 192, 288, 576, 1440]:
        print(f"   mod{M:>4}: P0={r[f'mod{M}']:.3e}  E={C5*r[f'mod{M}']:.2f} "
              f"(min class size {r[f'mod{M}_minclass']})")
json.dump(results, open("mask_models.json", "w"), indent=1)

# class barcodes for the art: g=17 per-class offset profiles mod 32
n, bits, offs = load(17)
prof = {}
for M in [8, 32]:
    cls = n % M
    for c in np.unique(cls):
        sel = cls == c
        prof[f"{M}_{int(c)}"] = dict(count=int(sel.sum()),
                                     q=[float(x) for x in bits[sel].mean(0)])
prof['offs'] = [int(j) for j in offs]
json.dump(prof, open("g17_class_profiles.json", "w"), indent=1)
print("saved g17 class profiles")
