#!/usr/bin/env python3
"""Survey: exact-vs-grid validation, family areas across n, exhaustive minimum small n."""
import numpy as np, itertools, json, time
from cloth_lib import *

def main():
    rng = np.random.default_rng(7)
    # 1) validate grid vs exact
    print("== grid vs exact validation ==")
    for n in (8, 32, 128):
        for trial in range(3):
            s = rng.permutation(n)
            ae = area_exact(s)
            ag = area_grid(s, 2048)
            print(f" n={n}: exact {ae:.8f} grid2048 {ag:.8f} diff {abs(ae-ag):.2e}")
    # 2) exhaustive minimum for small n (exact)
    print("== exhaustive minima ==")
    exact_min = {}
    for n in range(2, 9):
        best = (2.0, None)
        for pm in itertools.permutations(range(n)):
            a = area_exact(np.array(pm))
            if a < best[0]: best = (a, pm)
        exact_min[n] = best
        print(f" n={n}: alpha_n = {best[0]:.8f} argmin={best[1]}  alpha*log(n)={best[0]*np.log(n):.5f}")
    json.dump({str(k): (v[0], list(v[1])) for k, v in exact_min.items()},
              open("cloth_exact_min.json", "w"))
    # 3) families across n
    print("== families ==")
    res = {}
    for n in (64, 256, 1024, 4096):
        M = 4096
        fam = {"id": sigma_id(n), "rev": sigma_rev(n),
               "faro": sigma_faro(n), "blockrev_sqrt": sigma_blockrev(n, int(np.sqrt(n)))}
        if (n & (n-1)) == 0: fam["bitrev"] = sigma_bitrev(n)
        # 3-adic digit reversal at nearest power
        m3 = 3 ** int(round(np.log(n)/np.log(3)))
        rand_areas = [area_grid(random_sigma(n, rng), 2048) for _ in range(6)]
        row = {k: area_grid(s, M) for k, s in fam.items()}
        row["random_mean"] = float(np.mean(rand_areas))
        res[n] = row
        pretty = " ".join(f"{k}={v:.5f}" for k, v in row.items())
        print(f" n={n}: {pretty}")
        print(f"     bitrev*log n = {row.get('bitrev', float('nan'))*np.log(n):.5f}")
    json.dump(res, open("cloth_families.json", "w"))

if __name__ == "__main__":
    main()
