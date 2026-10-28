"""Random sweep: for each sampled J compute e_p (p=1..PMAX), LP(3x3) lower bound, optimal period data.
Usage: python3 sweep.py SEED NSAMPLES OUTFILE"""
import sys, json, time
import numpy as np
from gs import strip_opt, lp_bound, period_lattice, energy_of

PMAX = 10
TOL = 1e-9
BIG = 10.0


def sample(rng, fam):
    if fam == "gauss":
        return rng.normal(size=16)
    if fam == "int2":
        return rng.integers(-2, 3, size=16).astype(float)
    if fam == "pm1sparse":
        J = rng.choice([-1.0, 0.0, 1.0], size=16, p=[0.2, 0.6, 0.2])
        return J
    if fam == "ising":  # spin form: h, nn (h,v), diag, antidiag, 3-spin, 4-spin with random couplings
        s = lambda b: 2 * b - 1
        c = rng.normal(size=8) * (rng.random(8) < 0.7)
        J = np.zeros(16)
        for t in range(16):
            a, b, cc, d = [s((t >> k) & 1) for k in range(4)]
            J[t] = (c[0] * a + c[1] * a * b + c[2] * a * cc + c[3] * a * d + c[4] * b * cc
                    + c[5] * a * b * cc + c[6] * a * b * cc * d + c[7] * a * b * d)
        return J
    if fam.startswith("face"):
        k = int(fam[4:])
        allowed = rng.choice(16, size=k, replace=False)
        J = np.full(16, BIG)
        J[allowed] = rng.normal(size=k) * (0.0 if rng.random() < 0.25 else 1.0)
        return J
    raise ValueError(fam)


FAMS = ["gauss", "int2", "pm1sparse", "ising", "face8", "face10", "face11", "face12", "face13"]


def analyse(J):
    es = []
    grids = []
    for p in range(1, PMAX + 1):
        e, g = strip_opt(J, p)
        es.append(e)
        grids.append(g)
    es = np.array(es)
    estar = es.min()
    scale = max(1.0, np.abs(J).max())
    pstar = int(np.argmax(es <= estar + TOL * scale)) + 1
    g = grids[pstar - 1]
    area, pv, h, s, fd = period_lattice(g)
    lb = lp_bound(J, 3, 3)
    return dict(J=J.tolist(), e=es.tolist(), estar=float(estar), pstar=pstar, area=int(area),
                pv=int(pv), h=int(h), s=int(s), fd=fd.tolist(), lp33=float(lb),
                gap=float(estar - lb))


if __name__ == "__main__":
    seed, N, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    rng = np.random.default_rng(seed)
    t0 = time.time()
    with open(out, "w") as f:
        for i in range(N):
            fam = FAMS[i % len(FAMS)]
            J = sample(rng, fam)
            r = analyse(J)
            r["fam"] = fam
            f.write(json.dumps(r) + "\n")
            if i % 200 == 0:
                f.flush()
                print(i, time.time() - t0, flush=True)
