"""Triangle corner pieces with ONE short arm: all arms have length t except one of length u.
J_n = (n+3) a_n - 2 - (n+2) a_{n+1}  > 0 violates the simplex-family line."""
import numpy as np, sys
from convex_union import a_seq
T = np.array([(0, 0), (1, 0), (0.5, 3**.5/2)])
def pieces(t, u):
    P = []
    for i in range(3):
        A, B = T[i], T[(i+1) % 3]
        P.append(np.array([A, A + t*(B-A)]))
        tr = u if i == 1 else t
        P.append(np.array([B, B + tr*(A-B)]) if tr > 1e-12 else B[None])
    return P
if __name__ == "__main__":
    for t in (0.15, 0.2, 0.25, 0.3):
        for u in (0.0, 0.25*t, 0.5*t, 0.75*t, t):
            a, _ = a_seq(pieces(t, u), 5, res=300, ncand=20, iters=22)
            J = [(n+3)*a[n-1] - 2 - (n+2)*a[n] for n in range(1, 5)]
            print(f"t={t:.2f} u={u:.4f} a={np.round(a, 5)} J={np.round(J, 4)}", flush=True)
