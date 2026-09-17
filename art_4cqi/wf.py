"""wf.py — haploid Wright–Fisher population of N with N distinct names at generation 0, run forward
until one name is left (fixation = the whole present descends from one founder).  Records parents
(G x N int16) and the PLANAR layout: each generation sorted by the rank of its parent, so the
lineage lines between consecutive rows never cross and every family is a contiguous block.
    python3 wf.py N seed  -> cache/wf_N_seed.npz + a line of numbers
"""
import sys, json, numpy as np

def run(N, seed, gmax=None):
    rng = np.random.default_rng(seed)
    gmax = gmax or 12 * N
    parents = []
    names = np.arange(N)
    alive = [N]
    for t in range(gmax):
        p = rng.integers(0, N, N)
        parents.append(p.astype(np.int16 if N < 32000 else np.int32))
        names = names[p]
        k = len(np.unique(names))
        alive.append(k)
        if k == 1:
            break
    P = np.array(parents)                    # P[t, j] = parent (in generation t) of child j in generation t+1
    G = len(P)
    # planar layout: pos[t, j] = rank of individual j in row t
    pos = np.zeros((G + 1, N), np.int32)
    pos[0] = np.arange(N)
    for t in range(G):
        order = np.argsort(pos[t][P[t]], kind='stable')
        r = np.empty(N, np.int32); r[order] = np.arange(N)
        pos[t + 1] = r
    # names of every individual (founder index) and forward descendant counts at the present
    nm = np.zeros((G + 1, N), np.int32)
    nm[0] = np.arange(N)
    for t in range(G):
        nm[t + 1] = nm[t][P[t]]
    desc = np.zeros((G + 1, N), np.int32)        # number of present-day descendants
    desc[G] = 1
    for t in range(G - 1, -1, -1):
        desc[t] = np.bincount(P[t], weights=desc[t + 1], minlength=N).astype(np.int32)
    return P, pos, nm, desc, np.array(alive)

if __name__ == '__main__':
    N = int(sys.argv[1]); seed = int(sys.argv[2])
    P, pos, nm, desc, alive = run(N, seed)
    G = len(P)
    winner = int(nm[G, 0])
    # the last forgetting: the generation at which the second-to-last name died
    last2 = int(np.argmax(alive == 1))
    t2 = int(np.argmax(alive <= 2))
    # survivors at decades
    dec = {int(t): int(alive[t]) for t in [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000] if t <= G}
    print(json.dumps(dict(N=N, seed=seed, G=G, winner=winner, two_names_from=t2, one_name_from=last2,
                          alive=dec)))
    np.savez_compressed(f'cache/wf_{N}_{seed}.npz', P=P, pos=pos, nm=nm, desc=desc, alive=alive)
