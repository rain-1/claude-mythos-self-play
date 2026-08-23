#!/usr/bin/env python3
"""MO 514552: reciprocal-addition Pascal triangle A(n+1,k)=1/A(n,k-1)+1/A(n,k), edges=1.
Test the derived mechanism:
  (1) boundary layer: diagonal limits B_j satisfy B_j = (u+sqrt(u^2+4))/2, u=1/B_{j-1},
      B_0=1, B_1=phi, B_j -> sqrt2 with ratio -1/3.
  (2) gauge d(n,k)=(-1)^n (A(n,k)-sqrt2): interior evolves by plain averaging
      d' = (d_{k-1}+d_k)/2 + O(d^2), so "mass" M_n = sum_k d(n,k) has alternating
      bounded increments; parity-averaged mass Mbar converges.
  (3) center: d(n, n/2) ~ Mbar * sqrt(2/(pi n)); hence C = sqrt(2/pi)*Mbar.
  (4) profile: d(n,k) ~ Mbar * 2^-n C(n,k) (Gaussian heart of width sqrt(n)/2),
      geometric skin at edges, near-zero in between.
"""
import numpy as np, json, math

SQRT2 = math.sqrt(2.0)

def boundary_layer(J=40):
    B = [1.0]
    for j in range(1, J):
        u = 1.0/B[-1]
        B.append((u + math.sqrt(u*u+4.0))/2.0)
    return np.array(B)

def run(nmax, snap_rows, diag_j=48):
    A = np.array([1.0])
    center = np.zeros(nmax+1); mass = np.zeros(nmax+1)
    diag = {}          # row -> first diag_j entries
    snaps = {}
    center[0] = 1.0 - SQRT2; mass[0] = 1.0 - SQRT2
    for n in range(1, nmax+1):
        inv = 1.0/A
        Anew = np.empty(n+1)
        Anew[0] = Anew[n] = 1.0
        if n >= 2:
            Anew[1:n] = inv[:-1] + inv[1:]
        s = 1.0 if n % 2 == 0 else -1.0
        d = s*(Anew - SQRT2)
        mass[n] = d.sum()
        # central entry (use exact center for even rows, average two for odd)
        if n % 2 == 0:
            center[n] = Anew[n//2] - SQRT2
        else:
            center[n] = 0.5*(Anew[n//2] + Anew[n//2+1]) - SQRT2
        if n in snap_rows:
            snaps[n] = Anew.copy()
        if n == nmax:
            diag['last'] = Anew[:diag_j].copy()
        A = Anew
    return center, mass, snaps, diag

if __name__ == "__main__":
    import sys
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 65536
    snap_rows = {64, 256, 1024, 4096, 16384, 65536, nmax}
    center, mass, snaps, diag = run(nmax, snap_rows)

    # (1) boundary layer check
    B = boundary_layer(30)
    dev = B - SQRT2
    print("B_j - sqrt2 and ratios:")
    for j in range(0, 12):
        r = dev[j+1]/dev[j] if dev[j] != 0 else float('nan')
        print(f"  j={j:2d}  B={B[j]:.12f}  dev={dev[j]:+.3e}  ratio={r:+.6f}")
    last = diag['last']
    print("empirical diagonal (last row) vs B_j, first 12:")
    for j in range(12):
        print(f"  j={j:2d}  A(n,j)={last[j]:.12f}  B_j={B[j]:.12f}  diff={last[j]-B[j]:+.2e}")

    # (2) mass convergence: parity-averaged
    Mbar_seq = 0.5*(mass[:-1] + mass[1:])
    for n in [100, 1000, 10000, nmax//4, nmax//2, nmax-1]:
        print(f"  n={n:7d}  M_n={mass[n]:+.9f}  Mbar~{Mbar_seq[n]:+.9f}")

    # (3) C measurement: center*(-1)^n*sqrt(n) -> C, Richardson in 1/n
    ns = np.array([nmax//16, nmax//8, nmax//4, nmax//2, nmax])
    for n in ns:
        s = 1.0 if n % 2 == 0 else -1.0
        print(f"  n={n:7d}  C_est={s*center[n]*math.sqrt(n):.9f}")
    # Richardson using even rows only
    evens = np.arange(2, nmax+1, 2)
    Cev = center[evens]*np.sqrt(evens)*np.where(evens % 2 == 0, 1.0, -1.0)
    # fit C + a/n + b/n^2 on tail
    tail = evens > nmax//4
    X = np.vstack([np.ones(tail.sum()), 1.0/evens[tail], 1.0/evens[tail]**2]).T
    coef, *_ = np.linalg.lstsq(X, Cev[tail], rcond=None)
    C_fit = coef[0]
    Mbar = Mbar_seq[-1]
    pred = math.sqrt(2.0/math.pi)*Mbar
    print(f"\nC (Richardson fit)      = {C_fit:.9f}")
    print(f"Mbar (last)             = {Mbar:.9f}")
    print(f"sqrt(2/pi)*Mbar         = {pred:.9f}")
    print(f"ratio C/pred            = {C_fit/pred:.9f}")

    # (4) profile test at nmax: d vs Mbar*binomial-gaussian
    n = nmax; Arow = snaps[n]
    s = 1.0 if n % 2 == 0 else -1.0
    d = s*(Arow - SQRT2)
    k = np.arange(n+1)
    gauss = Mbar*np.sqrt(2.0/(math.pi*n))*np.exp(-2.0*(k-n/2.0)**2/n)
    i0 = n//2
    for off in [0, int(0.25*math.sqrt(n)), int(0.5*math.sqrt(n)), int(math.sqrt(n)), int(2*math.sqrt(n)), int(4*math.sqrt(n))]:
        print(f"  k=center+{off:6d}  d={d[i0+off]:+.3e}  gauss={gauss[i0+off]:+.3e}")
    np.save('tri_snap_last.npy', Arow)
    json.dump({'C_fit': C_fit, 'Mbar': float(Mbar), 'pred': pred,
               'mass_tail': mass[-8:].tolist()}, open('tri_science.json','w'), indent=1)
    print("saved tri_snap_last.npy, tri_science.json")
