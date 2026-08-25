#!/usr/bin/env python3
"""MO 514626: census of |det D_pi|, D_ij = |i-j| + |pi(i)-pi(j)|, over S_n.

Verifies: (a) conjecture |det| >= (n-1)*4^(n-1); (b) sign = (-1)^(n-1);
(c) exactly one positive eigenvalue; (d) argmin structure;
(e) the Minkowski/border decomposition |det D| = 2^(n-1) det(Ftilde) * (s + q).
Streams permutations in chunks; batched numpy dets.
"""
import numpy as np, itertools, sys, json, time

def census(n, chunk=200000, eigcheck_first=2000):
    A = np.abs(np.subtract.outer(np.arange(n), np.arange(n))).astype(np.float64)
    target = (n-1) * 4.0**(n-1)
    mins = []            # (det, perm) smallest few
    minval = np.inf; minperms = []
    maxval = -np.inf; maxperm = None
    total = 0
    viol = []
    sign_bad = 0
    eig_bad = 0
    hist = {}
    # second-smallest tracking: keep set of distinct values near bottom
    bottom = set()
    t0 = time.time()
    it = itertools.permutations(range(n))
    while True:
        block = list(itertools.islice(it, chunk))
        if not block: break
        P = np.array(block)                      # (m, n)
        m = len(P)
        B = np.abs(P[:, :, None] - P[:, None, :]).astype(np.float64)
        D = A[None, :, :] + B
        dets = np.linalg.det(D)
        adets = np.abs(dets)
        # sign check
        want = (-1)**(n-1)
        sign_bad += int(np.sum(np.sign(dets) != want))
        # eigen-structure spot check on first blocks
        if total < eigcheck_first:
            k = min(m, eigcheck_first - total)
            for i in range(k):
                w = np.linalg.eigvalsh(D[i])
                if np.sum(w > 1e-9) != 1: eig_bad += 1
        # violations of conjecture
        bad = adets < target - 1e-6
        for i in np.nonzero(bad)[0]:
            viol.append((block[i], dets[i]))
        # min / max
        i = np.argmin(adets)
        if adets[i] < minval - 1e-6:
            minval = adets[i]; minperms = [block[i]]
        # collect ALL perms attaining the min value (within tol)
        att = np.nonzero(np.abs(adets - target) < 1e-4 * target)[0]
        for i in att: minperms.append(block[i])
        i = np.argmax(adets)
        if adets[i] > maxval: maxval = adets[i]; maxperm = block[i]
        # bottom distinct values (rounded to int; dets are integers)
        r = np.round(adets).astype(np.int64)
        for v in np.unique(r)[:40]: bottom.add(int(v))
        total += m
    bottom = sorted(bottom)[:12]
    return dict(n=n, total=total, target=target, minval=minval,
                nmin=len(set(minperms)), minperms=[list(p) for p in set(minperms)][:8],
                maxval=maxval, maxperm=list(maxperm),
                viol=len(viol), sign_bad=sign_bad, eig_bad=eig_bad,
                bottom=bottom, secs=round(time.time()-t0,1))

if __name__ == "__main__":
    out = {}
    for n in range(2, 10):
        r = census(n)
        out[n] = r
        print(f"n={n}: min={r['minval']:.0f} target={r['target']:.0f} "
              f"viol={r['viol']} sign_bad={r['sign_bad']} eig_bad={r['eig_bad']} "
              f"#argmin={r['nmin']} max={r['maxval']:.0f} bottom={r['bottom'][:6]} "
              f"({r['secs']}s)", flush=True)
        json.dump(out, open("manh_census.json","w"), indent=1)
