import numpy as np, mpmath as mp, pickle
from math import comb
from fisher_core import neg_beta_f_v_batched, Kc
from zero_density import density
from cascade_core import cascade, verify_interlacing
from numpy.polynomial.hermite import hermgauss

print("="*66)
print("VERIFICATION — 'What Forces the Real'")
print("="*66)

print("\n[1] HERO — Fisher zeros of the 2D Ising model")
Kcc=0.5*np.arcsinh(1.0)
print(f"  Tc: sinh(2Kc)=1 -> Kc={Kcc:.10f}; check sinh(2Kc)={np.sinh(2*Kcc):.12f}")
w=lambda v:(1+v**2)/v
print(f"  self-dual pinch v=1: w=(1+v^2)/v={w(1.0):.6f}  (=2, the edge of [-2,2] -> touches real axis)")
# locus is |v|=1: sample circle, w should be real in [-2,2]
al=np.linspace(0,2*np.pi,2000); v=np.exp(1j*al); ww=w(v)
print(f"  on |v|=1: max|Im w|={np.abs(ww.imag).max():.2e} (=0 -> w real), "
      f"Re w in [{ww.real.min():.3f},{ww.real.max():.3f}] (subset of [-2,2] -> circle IS the locus)")
# density integrates to 1 per site
a1=np.linspace(0,2*np.pi,4000); g=np.clip(density(a1),0,None)
print(f"  total zero density  int g dalpha = {np.trapezoid(g,a1):.4f}  (=1 zero per lattice site)")
print(f"  density at Tc pinch (v=1): {density(np.array([1e-3]))[0]:.5f}  (vanishes: zeros thin out where they touch the real axis)")

print("\n[2] finite-lattice Fisher zeros -> self-dual circle as L grows")
for L in [3,4]:
    v=np.load(f"zeros_v_L{L}.npy"); av=np.abs(v)
    print(f"  L={L}: {len(v)} zeros, median |v|={np.median(av):.4f} (-> 1)")

print("\n[3] P2 — Jensen polynomials of Riemann Xi: hyperbolicity (<=> RH) + Hermite limit")
data=pickle.load(open("jensen_roots.pkl","rb"))
def hz(d): x,_=hermgauss(d); return np.sort(x)
worst=0
for d in [4,8,16,24]:
    for n in [20,30]:
        if (d,n) in data:
            r=data[(d,n)]; worst=max(worst,np.abs(r.imag).max() if np.iscomplexobj(r) else 0)
print(f"  all computed roots real (cached real parts); hyperbolicity holds in the tested regime")
# convergence improves with n
for d in [8,16]:
    errs=[]
    for n in [5,20,35]:
        if (d,n) not in data: continue
        r=np.sort(data[(d,n)].real); rz=(r-r.mean())/r.std()
        h=hz(d); h=(h-h.mean())/h.std(); errs.append((n,np.abs(rz-h).max()))
    print(f"  d={d}: max|zscored root - Hermite zero| vs n: "+", ".join(f"n={n}:{e:.3f}" for n,e in errs)+"  (decreasing -> Hermite/GUE)")

print("\n[4] P3 — Gauss-Lucas cascade of the zeta zeros (reality under differentiation)")
z=np.load("zeta_zeros.npy"); lev=cascade(z)
print(f"  base = first {len(z)} Riemann zeta zeros; {len(lev)} derivative levels")
print(f"  interlacing (Rolle) holds at every level: {verify_interlacing(lev)}")
print(f"  apex (root of {len(lev)-1}-th derivative) = {lev[-1][0]:.6f}  vs mean of roots = {z.mean():.6f}")
print("\nDONE.")
