import numpy as np
from polylib import forced_graph, drop_triangle_graph
from verify_polygon import verify
for n in [5, 11, 13]:
    theta = np.load(f"hero_n{n}_theta.npy"); r = np.load(f"hero_n{n}_r.npy")
    comps, edges, _ = forced_graph(theta, r)
    assert comps == [n*(n-1)//2], comps
    verify(theta, r, edges, n*(n-1)//2)
    print(f"hero n={n}: VERIFIED simple {n*(n-1)//2}-gon")
for n in [7, 9]:
    theta = np.load(f"hero18_n{n}_theta.npy"); r = np.load(f"hero18_n{n}_r.npy")
    tri = tuple(int(x) for x in np.load(f"hero18_n{n}_tri.npy"))
    comps, edges = drop_triangle_graph(theta, r, tri)
    k = n*(n-1)//2 - 3
    assert comps == [k], comps
    verify(theta, r, edges, k)
    print(f"hero n={n}: VERIFIED simple {k}-gon (dropped {tri})")
