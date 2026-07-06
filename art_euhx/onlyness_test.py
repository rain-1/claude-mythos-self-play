"""Does chaos just above the golden curve connect all the way to the p=0 layer?
(i.e. no other rotational barrier survives at K). And inner-sea connectivity."""
import numpy as np
import stdmap_core as sm

K = 0.969
rng = np.random.default_rng(3)

def sea_phist(pcenter, n=48, T=3000000, label=""):
    x = rng.random(n * 6); p = pcenter + rng.normal(0, 0.006, n * 6)
    lam = sm.lyapunov_classify(x, p, K, nsteps=2500)
    sel = np.where(lam > 0.08)[0][:n]
    x, p = x[sel], p[sel]
    print(label, "seeds:", len(x))
    hist = np.zeros(200)
    for _ in range(T // 100):
        for _ in range(100):
            x, p = sm.step(x, p, K)
        hist += np.bincount(((p % 1.0) * 200).astype(int) % 200, minlength=200)
    return hist

# seed just above golden curve (p~0.70): does it reach p~0 and p~0.99?
h = sea_phist(0.70, T=1200000, label="above-golden")
cover = h > 0
print("p-bins covered (of 200):", cover.sum())
print("coverage of [0.69,1.0):", cover[138:200].mean(), " of [0,0.33):", cover[0:66].mean())
print("does it enter the inner strip (0.47..0.53)?", cover[94:106].any())

# inner sea from p=0.5: coverage between the curves
h2 = sea_phist(0.5, T=1200000, label="inner")
c2 = h2 > 0
print("inner covers bins:", c2.sum(), " range p=[%.3f, %.3f]" % (np.argmax(c2) / 200, (199 - np.argmax(c2[::-1])) / 200))
