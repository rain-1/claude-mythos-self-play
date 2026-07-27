"""Sample exact Borwein convolution curves h_n to float arrays + certificates."""
from fractions import Fraction as F
import numpy as np
from borwein_exact import PP, conv_box

h = PP([F(-1), F(1)], [[F(1)]])
curves = []; exact0 = []; plateaus = []
xs = np.linspace(-2.4, 2.4, 6001)
s = F(0)
for n in range(0, 9):
    if n > 0:
        h = conv_box(h, F(1, 2*n+1))
        s += F(1, 2*n+1)
    # float-ify pieces
    b = np.array([float(x) for x in h.b])
    ys = np.zeros_like(xs)
    for i, c in enumerate(h.p):
        m = (xs >= b[i]) & (xs < b[i+1])
        if not m.any(): continue
        cf = [float(cc) for cc in c]
        acc = np.zeros(m.sum())
        for cc in reversed(cf): acc = acc*xs[m] + cc
        ys[m] = acc
    curves.append(ys)
    v0 = h.eval(F(0))
    exact0.append(v0)
    plateaus.append(1 - s)
    print(n, "h(0) =", v0, " plateau half-width =", 1-s, float(1-s))
np.savez('mesa_curves.npz', xs=xs, curves=np.array(curves),
         plateaus=np.array([float(p) for p in plateaus]),
         deficits=np.array([float(1-v) for v in exact0]))
# sinc products for the sky
t = np.linspace(0.001, 45, 9000)
def sinc(x): return np.sin(x)/x
sk = []
prod = np.ones_like(t)
for n in range(0, 9):
    prod = prod * sinc(t/(2*n+1))
    sk.append(prod.copy())
np.savez('mesa_sky.npz', t=t, prods=np.array(sk))
# exact deficit at n=7 as string for annotation
d7 = 1 - exact0[7]
print("deficit n=7 =", d7)
print("numerator", d7.numerator, "denominator", d7.denominator)
print("float", float(d7))
d8 = 1 - exact0[8]
print("deficit n=8 =", float(d8), d8.numerator, "/", d8.denominator)
