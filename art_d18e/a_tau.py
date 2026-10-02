import numpy as np
a = np.fromfile('a124056.bin', dtype=np.uint32)
V = int(a.max()) + 1
tau = np.zeros(V, np.uint16)
for d in range(1, V):
    tau[d::d] += 1
np.save('tau.npy', tau)
tp = tau[a[:-1]]              # tau of predecessor for terms 2..N
print(np.bincount(tp)[:40])
