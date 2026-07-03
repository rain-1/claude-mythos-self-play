"""Hero phase 1: run the full-length Levy flight, save decimated positions
for window search. Rerun deterministically later for the final splat."""
import sys
import numpy as np

ALPHA = 1.45
N = 1_600_000_000
DEC = 40          # keep every 40th position -> 40M points


def walk_stream(n, alpha, seed, chunk=20_000_000):
    """Yield (start_index, positions_chunk[float64->float32])."""
    rng = np.random.default_rng(seed)
    pos = np.zeros(2)
    done = 0
    while done < n:
        m = min(chunk, n - done)
        u = rng.random(m)
        L = u ** (-1.0 / alpha)
        th = rng.random(m) * (2 * np.pi)
        xs = np.cumsum(L * np.cos(th)) + pos[0]
        ys = np.cumsum(L * np.sin(th)) + pos[1]
        p = np.stack([xs, ys], 1)
        pos = p[-1].copy()
        yield done, p
        done += m


if __name__ == "__main__":
    seed = int(sys.argv[1])
    dec = []
    for start, p in walk_stream(N, ALPHA, seed):
        dec.append(p[::DEC].astype(np.float32))
    dec = np.concatenate(dec)
    np.save(f"walk_dec_s{seed}.npy", dec)
    print("saved", dec.shape)
