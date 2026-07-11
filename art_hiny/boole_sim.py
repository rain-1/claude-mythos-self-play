"""Stream a very long Boole orbit; save per-excursion subsampled profiles."""
import sys
import numpy as np

T   = int(float(sys.argv[1])) if len(sys.argv) > 1 else 300_000_000
X0  = float(sys.argv[2]) if len(sys.argv) > 2 else 1.54217
OUT = sys.argv[3] if len(sys.argv) > 3 else "cache/boole_orbit.npz"
MAXKEEP = 1400   # profile samples kept per excursion

CH = 5_000_000
x = X0
profiles = []   # list of float32 arrays (|x| samples)
durs = []
sides = []
cur = []        # running current-excursion samples (python list of chunks)
cur_side = None
cur_len = 0

def close_exc():
    global cur, cur_len
    if cur_len == 0:
        return
    seg = np.concatenate(cur) if len(cur) > 1 else cur[0]
    if len(seg) > MAXKEEP:
        idx = np.unique(np.round(np.linspace(0, len(seg) - 1, MAXKEEP)).astype(int))
        seg = seg[idx]
    profiles.append(np.abs(seg).astype(np.float32))
    durs.append(cur_len)
    sides.append(cur_side)
    cur = []; cur_len = 0

done = 0
while done < T:
    n = min(CH, T - done)
    buf = np.empty(n, np.float64)
    for i in range(n):
        x = x - 1.0 / x
        buf[i] = x
    done += n
    s = buf > 0
    cuts = np.nonzero(s[1:] != s[:-1])[0] + 1
    bnds = np.concatenate([[0], cuts, [n]])
    for a, b in zip(bnds[:-1], bnds[1:]):
        piece = buf[a:b]
        side = bool(s[a])
        if cur_len > 0 and side == cur_side:
            cur.append(piece); cur_len += b - a
        else:
            close_exc()
            cur = [piece]; cur_len = b - a; cur_side = side
    if done % 50_000_000 < CH:
        print(f"  {done/1e6:.0f}M steps, {len(durs)} breaths", flush=True)
close_exc()

durs = np.array(durs, np.int64)
sides = np.array(sides, bool)
peaks = np.array([p.max() for p in profiles], np.float32)
lens = np.array([len(p) for p in profiles], np.int32)
flat = np.concatenate(profiles).astype(np.float32)
import os
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
np.savez_compressed(OUT, flat=flat, lens=lens, durs=durs, sides=sides, peaks=peaks, x0=X0, T=T)
print("breaths:", len(durs), "| max peak:", peaks.max(), "| max dur:", durs.max(),
      "| time in top-10:", np.sort(durs)[-10:].sum() / T)
