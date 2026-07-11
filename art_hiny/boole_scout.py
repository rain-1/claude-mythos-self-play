"""Scout single-orbit windows for the bundle render: want 6-20 arcs with a
good spread of heights, tallest arc not eating the whole window."""
import numpy as np

def orbit(x0, T):
    x = x0
    xs = np.empty(T)
    for t in range(T):
        x = x - 1.0 / x
        xs[t] = x
    return xs

def census(xs):
    s = xs > 0
    cuts = np.nonzero(s[1:] != s[:-1])[0] + 1
    bounds = np.concatenate([[0], cuts, [len(xs)]])
    durs = np.diff(bounds)
    peaks = np.array([np.abs(xs[a:b]).max() for a, b in zip(bounds[:-1], bounds[1:])])
    return durs, peaks

T = 90_000
print("x0        #exc  #arcs>T/60  maxdur/T  maxpeak  #peaks>30")
for x0 in np.linspace(1.41, 1.79, 24):
    xs = orbit(x0, T)
    durs, peaks = census(xs)
    big = np.count_nonzero(durs > T / 60)
    print(f"{x0:.5f}  {len(durs):5d}  {big:6d}     {durs.max()/T:.2f}   {peaks.max():8.1f}  {np.count_nonzero(peaks>30):4d}")
