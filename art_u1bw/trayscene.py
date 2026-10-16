# trayscene.py — the same six glass sticks, all thirty ways.  Assignments that close stand up as tetrahedra;
# the others fall open: the best face lies flat as a triangle and the three remaining sticks lie radially
# outward from its corners (a tent that could not close).  Writes scene.bin for sticks.c.
import numpy as np, struct, itertools, json, sys
from stickscene import REPS, EDGES, tetra_ok, cm_vol2, tetra_coords, rest_on_face, pastel, tri

def tray(L, cols=6, pitch=7.6, rr=0.2, rb=0.42, sat=0.5, absk=0.4, out='scene_tray.bin', meta='meta_tray.json', seed=1,
         hue0=0.98, hue1=0.12, beadcol=(0.05, 0.08, 0.12)):
    rng = np.random.default_rng(seed)
    S = sum(L); cuts = np.cumsum(L)[:-1] / S
    mids = (np.r_[0, cuts] + np.r_[cuts, 1]) / 2
    hue = [hue0 + (hue1 - hue0) * m for m in mids]
    items = []
    for p in REPS:
        e = [L[i] for i in p]
        if tetra_ok(e): items.append((0, -cm_vol2(e), p))
        else:
            faces = [(0, 1, 3), (0, 2, 4), (1, 2, 5), (3, 4, 5)]   # edge indices of faces 012, 013, 023, 123
            good = [f for f in faces if tri(*[e[k] for k in f])]
            # 'how far from closing': CM determinant sign magnitude, normalised
            items.append((1, -cm_vol2(e) / S ** 6 if good else 1e9, p))
    items.sort(key=lambda t: (t[0], t[1]))
    sph, cap, info = [], [], []
    rows = (len(items) + cols - 1) // cols
    placed = []; xlim = (-(cols / 2) * pitch - 1, (cols / 2) * pitch + 1); ylim = (-(rows / 2) * pitch - 1, (rows / 2) * pitch + 1)
    def rod(A, B, piece, off=rb + rr + 0.01):
        u = B - A; ln = np.linalg.norm(u); u /= ln
        t = pastel(hue[piece], sat); col = -np.log(np.clip(t, 1e-3, 1)) * absk
        if ln > 2 * off + 0.02: cap.append([*(A + u * off), *(B - u * off), rr, 0, *col, 0])
    def rod_from(A, u, length, piece, off=rb + rr + 0.01):
        t = pastel(hue[piece], sat); col = -np.log(np.clip(t, 1e-3, 1)) * absk
        cap.append([*(A + u * off), *(A + u * (off + length - 2 * rr)), rr, 0, *col, 0])
    for n, (bad, key, p) in enumerate(items):
        r, c = divmod(n, cols)
        cx = (c - (cols - 1) / 2) * pitch; cy = (r - (rows - 1) / 2) * pitch
        e = [L[i] for i in p]
        if not bad:
            P = rest_on_face(tetra_coords(e), rng, True); P[:, :2] += [cx, cy]; P[:, 2] += rb
            placed.extend(P[:, :2].tolist())
            for v in P: sph.append([*v, rb, 0, *beadcol, 0])
            for k, (i, j) in enumerate(EDGES): rod(P[i], P[j], p[k])
        else:
            faces = {(0, 1, 2): (0, 1, 3), (0, 1, 3): (0, 2, 4), (0, 2, 3): (1, 2, 5), (1, 2, 3): (3, 4, 5)}
            good = [(sum(1 for _ in [0]) and v, f) for f, v in faces.items() if tri(*[e[k] for k in v])]
            if good:
                # largest-area valid face lies flat
                def area(v):
                    a, b, c_ = [e[k] for k in v]; s = (a + b + c_) / 2; return np.sqrt(max(s * (s - a) * (s - b) * (s - c_), 0))
                v, f = max(good, key=lambda g: area(g[0]))
                i, j, k = f; o = [q for q in range(4) if q not in f][0]
                eid = lambda a_, b_: EDGES.index(tuple(sorted((a_, b_))))
                dij, dik, djk = e[eid(i, j)], e[eid(i, k)], e[eid(j, k)]
                Pi = np.array([0, 0.0]); Pj = np.array([dij, 0]); x = (dij ** 2 + dik ** 2 - djk ** 2) / (2 * dij)
                Pk = np.array([x, np.sqrt(max(dik ** 2 - x ** 2, 0))])
                T = np.array([Pi, Pj, Pk]); T -= T.mean(0)
                # choose the rotation whose spokes keep farthest from everything already placed
                best = None
                for ang in np.linspace(0, 2 * np.pi, 72, endpoint=False) + rng.uniform(0, 0.08):
                    R = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]]); TT = T @ R.T + [cx, cy]
                    pts = []
                    for q, vv in enumerate((i, j, k)):
                        u = TT[q] - TT.mean(0); u /= np.linalg.norm(u)
                        pts += [TT[q] + u * s_ for s_ in np.linspace(0, e[eid(vv, o)] + rb, 12)]
                    pts = np.array(pts)
                    d = 1e9 if not placed else np.min(np.linalg.norm(pts[:, None, :] - np.array(placed)[None], axis=2))
                    d = min(d, np.min(np.c_[pts[:, 0] - xlim[0], xlim[1] - pts[:, 0], pts[:, 1] - ylim[0], ylim[1] - pts[:, 1]]) * 2)
                    if best is None or d > best[0]: best = (d, ang, pts)
                ang = best[1]; placed.extend(best[2].tolist())
                R = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
                T = T @ R.T
                T3 = np.c_[T + [cx, cy], np.full(3, rb)]
                for q in T3: sph.append([*q, rb, 0, *beadcol, 0])
                rod(T3[0], T3[1], p[eid(i, j)]); rod(T3[0], T3[2], p[eid(i, k)]); rod(T3[1], T3[2], p[eid(j, k)])
                # rods from the corners, lying flat and pointing outward, slightly fanned
                for q, vv in enumerate((i, j, k)):
                    u = T3[q] - T3.mean(0); u[2] = 0; u /= np.linalg.norm(u)
                    rod_from(T3[q] + [0, 0, rr - rb], u, e[eid(vv, o)], p[eid(vv, o)])
                # spokes are shrunk with the triangle so proportions stay honest
            else:
                pass
        info.append(dict(r=r, c=c, assign=list(p), closes=not bad, key=float(key)))
    with open(out, 'wb') as fh:
        fh.write(struct.pack('ii', len(sph), len(cap)))
        fh.write(np.array(sph, dtype=np.float64).tobytes()); fh.write(np.array(cap, dtype=np.float64).tobytes())
    json.dump(info, open(meta, 'w'))
    return info

if __name__ == '__main__':
    L = np.array([1.52, 3.52, 2.67, 4.53, 3.43, 2.33])
    I = tray(L)
    print(sum(i['closes'] for i in I), 'close')
