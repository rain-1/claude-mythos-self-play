import numpy as np
from fisher_core import neg_beta_f_v_batched

# Density of Fisher zeros on the self-dual circle |v|=1:
# ReG(v) = (1/N) sum log|v - v_j| + harmonic  => the linear density along the circle
# equals (1/2pi) * jump in the OUTWARD normal derivative of ReG across the circle
#   g(alpha) = (1/2pi)[ d/dr ReG|_{1+} - d/dr ReG|_{1-} ]   (v = r e^{i alpha})
def density(alpha, eps=2e-4, Nt=6000):
    a=np.asarray(alpha,dtype=np.float64)
    e=np.exp(1j*a)
    def ReG(r):
        return neg_beta_f_v_batched(r*e, Nt=Nt).real
    # one-sided 2nd-order derivatives away from the singular circle
    r0=1.0
    dout=(-3*ReG(r0+ e)+4*ReG(r0+2*e_)-ReG(r0+3*e_))/(2*eps) if False else None
    # simpler central-ish: use points at 1+eps,1+2eps (outside) and 1-eps,1-2eps (inside)
    o1=ReG(1+eps); o2=ReG(1+2*eps)
    i1=ReG(1-eps); i2=ReG(1-2*eps)
    dr_out=(4*o1-3*ReG(1.0+1e-9)-o2)/(2*eps)   # forward from ~1
    dr_in =(3*ReG(1.0-1e-9)-4*i1+i2)/(2*eps)    # backward toward 1
    g=(dr_out-dr_in)/(2*np.pi)
    return g

e_=None
if __name__=="__main__":
    al=np.linspace(0,2*np.pi,721)
    g=density(al)
    print("g range", g.min(), g.max())
    print("g at alpha=0 (v=+1,Tc):", density(np.array([1e-3]))[0])
    print("g at alpha=pi/2 (v=i):", density(np.array([np.pi/2]))[0])
    print("g at alpha=pi (v=-1):", density(np.array([np.pi-1e-3]))[0])
    # integral over circle (arc length = dalpha since r=1) -> total 'charge' per site
    tot=np.trapezoid(np.clip(g,0,None), al)
    print("integral g dalpha =", tot, " (per-site zero count; Ising has ~ per-site density)")
