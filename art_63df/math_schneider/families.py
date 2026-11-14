import numpy as np
from convex_union import a_seq
T = np.array([(0, 0), (1, 0), (0.5, 3**.5/2)])
print("corner pieces of the triangle boundary (t = kept fraction at each end of each edge)")
for t in (0.05, 0.1, 0.2, 0.25, 0.3, 1/3, 0.4, 0.45, 0.5):
    P = []
    for i in range(3):
        A, B = T[i], T[(i+1) % 3]
        P.append(np.array([A, A + t*(B-A)])); P.append(np.array([B, B + t*(A-B)]))
    a, _ = a_seq(P, 4)
    print(f"t={t:.3f}", np.round(a, 5), "drops", np.round(-np.diff(a), 5))
print("circle (60-gon boundary) with g equal gaps of total fraction q")
k = 120
th = np.linspace(0, 2*np.pi, k+1); C = np.stack([np.cos(th), np.sin(th)], 1)
for g in (3, 4, 6):
    for q in (0.1, 0.2, 0.3, 0.5, 0.7, 0.9):
        keep = [i for i in range(k) if ((i * g / k) % 1.0) >= q]
        P = [C[i:i+2] for i in keep]
        a, _ = a_seq(P, 3, res=200)
        print(f"g={g} q={q}", np.round(a, 4), "drops", np.round(-np.diff(a), 4))
