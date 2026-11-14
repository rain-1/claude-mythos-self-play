import numpy as np, sys
from convex_union import a_seq
np.set_printoptions(linewidth=200)
for N in (4, 5, 6, 8):
    th = np.linspace(0, 2*np.pi, N+1)[:-1]; T = np.stack([np.cos(th), np.sin(th)], 1)
    print("regular %d-gon boundary, corner pieces t" % N)
    for t in (0.1, 0.2, 0.3, 0.4, 0.45, 0.5):
        P = []
        for i in range(N):
            A, B = T[i], T[(i+1) % N]
            P.append(np.array([A, A + t*(B-A)])); P.append(np.array([B, B + t*(A-B)]))
        a, _ = a_seq(P, 3 if N > 5 else 4, res=160)
        S = [(n+3)*a[n-1]-2-(n+2)*a[n] for n in range(1, len(a))]
        print(f" t={t:.2f} a={np.round(a, 4)} drops={np.round(-np.diff(a), 4)} Sviol={np.round(S, 3)}", flush=True)
