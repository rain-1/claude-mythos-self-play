import numpy as np

# 2D isotropic square-lattice Ising, Onsager exact free energy as a SINGLE-VALUED
# analytic function of v = sinh(2K):
#   c0 = cosh^2(2K) = 1 + v^2 ,  b = sinh(2K) = v
#   -beta f = ln2 + (1/4pi) int_0^2pi ln[ (c + sqrt(c^2 - v^2))/2 ] dtheta,  c = 1 + v^2 - v cos(theta)
# Fisher zeros accumulate on the Kramers-Wannier self-dual circle |v| = 1
# (there w = (1+v^2)/v = 2 cos(theta) in [-2,2]); the physical pinch (Tc) is v = +1.

def neg_beta_f_v(v, Nt=2000):
    v = np.asarray(v, dtype=np.complex128)
    theta = (np.arange(Nt)+0.5)*(2*np.pi/Nt)
    cost = np.cos(theta)
    acc = np.zeros(v.shape, dtype=np.complex128)
    v2 = v*v
    for i in range(Nt):
        c = 1.0 + v2 - v*cost[i]
        disc = np.sqrt(c*c - v2)
        val1 = 0.5*(c+disc); val2 = 0.5*(c-disc)
        val = np.where(np.abs(val1) >= np.abs(val2), val1, val2)
        acc += np.log(val)
    return np.log(2.0) + acc*(2*np.pi/Nt)/(4*np.pi)

def neg_beta_f_v_batched(v, Nt=2000, chunk=64):
    """Memory-lean vectorised version: sum over theta in chunks broadcast against a flat v."""
    v = np.asarray(v, dtype=np.complex128)
    shp = v.shape
    vf = v.ravel()[None, :]                 # (1, P)
    v2 = vf*vf
    theta = (np.arange(Nt)+0.5)*(2*np.pi/Nt)
    cost = np.cos(theta)
    acc = np.zeros(vf.shape[1], dtype=np.complex128)
    for s in range(0, Nt, chunk):
        ct = cost[s:s+chunk][:, None]       # (m,1)
        c = 1.0 + v2 - vf*ct                # (m,P)
        disc = np.sqrt(c*c - v2)
        val1 = 0.5*(c+disc); val2 = 0.5*(c-disc)
        val = np.where(np.abs(val1) >= np.abs(val2), val1, val2)
        acc += np.log(val).sum(axis=0)
    return (np.log(2.0) + acc*(2*np.pi/Nt)/(4*np.pi)).reshape(shp)

Kc = 0.5*np.arcsinh(1.0)  # 0.44069 ; vc = sinh(2Kc) = 1

if __name__ == "__main__":
    # checks
    print("F(v=0)=", neg_beta_f_v(np.array([0.0+0j]))[0], " expect ln2=", np.log(2))
    # w on circle -> 2 cos theta ; pinch v=1 -> w=2
    for vv in [1.0, -1.0, 1j, 0.5, 2.0]:
        w=(1+vv**2)/vv
        print(f"v={vv}: w={w}")
