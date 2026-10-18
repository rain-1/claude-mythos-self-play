"""Select ~12 diverse polygons per n from exploration pools, re-verify, write gallery.json + preview png."""
import os, sys, json, glob
import numpy as np
from poly import exact_check, turns, canon, orient_ccw, interior_angles

K = 12
SYMS = [lambda V: V, lambda V: np.c_[1 - V[:, 0], V[:, 1]], lambda V: np.c_[V[:, 0], 1 - V[:, 1]],
        lambda V: 1 - V, lambda V: V[:, ::-1], lambda V: np.c_[1 - V[:, 1], V[:, 0]],
        lambda V: np.c_[V[:, 1], 1 - V[:, 0]], lambda V: 1 - V[:, ::-1]]


def aligned_forms(V):
    """All copies of V under the 8 square symmetries, re-oriented CCW and cyclically
    shifted to every start index where the turn string equals its canonical form."""
    out = []
    for S in SYMS:
        W = orient_ccw(S(np.asarray(V)))
        t = turns(W); c = canon(t); n = len(W)
        for k in range(n):
            if t[k:] + t[:k] == c:
                out.append(np.roll(W, -k, axis=0).ravel())
    return out


def dist(fa, fb_ref):
    return min(np.linalg.norm(a - fb_ref) for a in fa)


def descriptor(V):
    V = orient_ccw(np.asarray(V)); n = len(V)
    t = turns(V); ia = interior_angles(V)
    on = (np.abs(V) < 1e-7) | (np.abs(V - 1) < 1e-7)
    sides = sorted(set(([ "left"] if np.any(np.abs(V[:, 0]) < 1e-7) else []) +
                       (["right"] if np.any(np.abs(V[:, 0] - 1) < 1e-7) else []) +
                       (["bottom"] if np.any(np.abs(V[:, 1]) < 1e-7) else []) +
                       (["top"] if np.any(np.abs(V[:, 1] - 1) < 1e-7) else [])))
    c = canon(t)
    # base edge: middle edge of the LLLL run (zigzag class)
    tilt = None
    if c.startswith("LLLL"):
        for k in range(n):
            if (t[k:] + t[:k]) == c:
                a, b = V[(k + 1) % n], V[(k + 2) % n]
                ang = np.degrees(np.arctan2(*(b - a)[::-1])) % 90
                tilt = float(min(ang, 90 - ang)); break
    return dict(reflex=t.count("R"), convex=t.count("L"), canon=c,
                max_convex_angle=float(ia[ia < 180].max()), min_angle=float(ia.min()),
                boundary_vertices=int(np.sum(np.any(on, axis=1))), sides_touched=sides,
                base_tilt_deg=tilt)


def select(pool):
    feats = [aligned_forms(np.array(p["verts"])) for p in pool]
    # group by class; take classes round-robin, farthest-point within
    rng = np.random.default_rng(0)
    chosen = [int(np.argmax([p["clearance"] for p in pool]))]
    dmin = np.array([dist(f, feats[chosen[0]][0]) for f in feats])
    while len(chosen) < min(K, len(pool)):
        i = int(np.argmax(dmin)); chosen.append(i)
        dmin = np.minimum(dmin, [dist(f, feats[i][0]) for f in feats])
    return chosen, dmin


def main():
    gal = {}; stats = {}
    files = sorted(glob.glob("runs/g*.json"), key=lambda f: int(f.split("g")[-1][:-5]))
    for f in files:
        d = json.load(open(f)); n = d["n"]
        pool = []
        for p in d["found"]:
            V = np.array(p["verts"]); c = exact_check(V)
            if c["ok"] and c["clearance"] >= min(0.004, 0.2 / (n - 1) ** 2):
                pool.append(dict(p, clearance=c["clearance"], len_err=c["len_err"], box_err=c["box_err"]))
        if not pool: continue
        # thin pool for speed
        if len(pool) > 1500:
            idx = np.random.default_rng(1).choice(len(pool), 1500, replace=False); pool = [pool[i] for i in idx]
        ch, _ = select(pool)
        items = []
        for i in ch:
            p = pool[i]; V = orient_ccw(np.array(p["verts"]))
            items.append(dict(verts=V.tolist(), turns=turns(V), clearance=p["clearance"],
                              len_err=p["len_err"], box_err=p["box_err"], descriptor=descriptor(V)))
        gal[n] = items
        cls = {}
        for p in d["found"]:
            cls[p["canon"]] = cls.get(p["canon"], 0) + 1
        rc = {}
        for p in d["found"]:
            r = p["turns"].count("R"); rc[r] = rc.get(r, 0) + 1
        stats[n] = dict(valid_found=len(d["found"]), tries=d["tries"], classes=cls, reflex_counts=rc,
                        gallery=len(items), min_clear=min(x["clearance"] for x in items))
        print(n, stats[n])
    json.dump(gal, open("gallery.json", "w"))
    json.dump(stats, open("gallery_stats.json", "w"), indent=1)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    ns = sorted(gal)
    fig, axs = plt.subplots(len(ns), K, figsize=(K * 1.2, len(ns) * 1.25))
    for r, n in enumerate(ns):
        for c in range(K):
            ax = axs[r, c]; ax.set_xlim(-.03, 1.03); ax.set_ylim(-.03, 1.03); ax.set_aspect(1); ax.axis("off")
            ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color="0.7", lw=0.5)
            if c < len(gal[n]):
                V = np.array(gal[n][c]["verts"]); W = np.vstack([V, V[:1]])
                ax.fill(W[:, 0], W[:, 1], alpha=0.25); ax.plot(W[:, 0], W[:, 1], lw=0.7)
        axs[r, 0].text(-0.25, 0.5, f"n={n}", transform=axs[r, 0].transAxes, ha="right", va="center", fontsize=8)
    plt.tight_layout(); plt.savefig("gallery_preview.png", dpi=110)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
