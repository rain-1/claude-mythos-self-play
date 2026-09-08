"""census_futures.py — the finite family of futures of one defector.

Between consecutive breakpoints n/m the deterministic Nowak–May dynamics is literally the
same map, so one run per open interval is an exhaustive census.  For each interval we run
the single-defector seed for T steps and record: the D-count by time, whether the pattern
froze (no flips over the last 30 steps), the final D fraction inside the reached square,
and a hash of the final pattern, so identical futures across intervals are detected.
"""
import numpy as np, json, time, hashlib, sys
from fractions import Fraction
sys.path.insert(0, '.')
import nowak
from PIL import Image


def midpoints():
    bps = nowak.breakpoints()
    ivs = [(Fraction(1), bps[0])] + [(bps[i], bps[i + 1]) for i in range(len(bps) - 1)] + [(bps[-1], None)]
    out = []
    for lo, hi in ivs:
        mid = (lo + hi) / 2 if hi is not None else lo + 1
        out.append((lo, hi, float(mid)))
    return out


if __name__ == '__main__':
    T = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    N = 2 * T + 41
    rows = []
    tiles = []
    for lo, hi, mid in midpoints():
        t0 = time.time()
        D = np.zeros((N, N), bool); D[N // 2, N // 2] = True
        counts = []
        flips_recent = []
        prev = D
        for t in range(T):
            D = nowak.step(D, mid)
            counts.append(int(D.sum()))
            flips_recent.append(int((D != prev).sum()))
            prev = D
        c = N // 2
        # reached square: radius = furthest D from centre (Chebyshev)
        ys, xs = np.nonzero(D)
        R = int(max(np.abs(ys - c).max(), np.abs(xs - c).max())) if len(ys) else 0
        frozen = all(f == 0 for f in flips_recent[-30:])
        h = hashlib.sha1(D.tobytes()).hexdigest()[:12]
        inside = D[c - R:c + R + 1, c - R:c + R + 1].mean() if R > 0 else 1.0
        row = dict(lo=str(lo), hi=str(hi) if hi else 'inf', mid=mid, R=R, frozen=frozen,
                   Dfrac_inside=float(inside), hash=h, counts=counts[::max(1, T // 40)],
                   final=counts[-1], secs=time.time() - t0)
        rows.append(row)
        print(f"({row['lo']},{row['hi']}) b={mid:.4f} R={R} frozen={frozen} D={counts[-1]} inside={inside:.3f} hash={h} {row['secs']:.1f}s", flush=True)
        tiles.append(D[c - T:c + T + 1, c - T:c + T + 1].copy())
    json.dump(rows, open(f'futures_T{T}.json', 'w'), indent=1)
    # contact sheet
    n = len(tiles); cols = 7; rws = (n + cols - 1) // cols
    s = 2 * T + 1
    sheet = np.ones((rws * (s + 6), cols * (s + 6)), np.uint8) * 255
    for i, tl in enumerate(tiles):
        r, cc = divmod(i, cols)
        sheet[r * (s + 6):r * (s + 6) + s, cc * (s + 6):cc * (s + 6) + s] = (~tl) * 255
    Image.fromarray(sheet).save(f'futures_T{T}_sheet.png')
    print('distinct futures:', len(set(r['hash'] for r in rows)))
