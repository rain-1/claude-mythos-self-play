"""
tropical.py — shared engine for the amoeba / coamoeba / Ronkin triptych.

A plane curve V(P) = { (z,w) in (C*)^2 : P(z,w) = 0 }, with
    P(z,w) = sum_{(i,j)} c[i,j] z^i w^j   (a Laurent polynomial).

Amoeba(P)  = { (log|z|, log|w|) : (z,w) in V(P) }        -- the log-modulus shadow
Coamoeba(P)= { (arg z,  arg w ) : (z,w) in V(P) } (mod 2pi) -- the phase image
Ronkin  N(x,y) = (1/(2pi)^2) ∮∮ log|P(e^{x+i s}, e^{y+i t})| ds dt

Core sampler: fix z = exp(x + i*theta); then P(z, .) is an ordinary polynomial in w
whose deg_w roots we solve for.  Sweeping theta over [0,2pi) and x over a range fills
the amoeba (as a density) and the coamoeba (from the arguments) simultaneously.
Batched over theta via stacked companion-matrix eigenvalues (np.linalg.eigvals on a
(K, n, n) array), so a whole x-row is one vectorised call.
"""
import numpy as np


def poly_w_coeffs(C, z):
    """Given coeff matrix C[i,j] (i = power of z, j = power of w) and an array z of
    complex values, return A[k, j] = coefficient of w^j at z[k]:  A = sum_i C[i,j] z^i.
    Shape: C is (Iz, Jw); z is (K,); returns (K, Jw)."""
    Iz, Jw = C.shape
    # Vandermonde in z: powers[k, i] = z[k]^i
    powers = np.vander(z, Iz, increasing=True)      # (K, Iz)
    return powers @ C                                # (K, Jw)


def roots_batch(A):
    """A[k, j] = coeff of w^j (j=0..n).  Return roots R[k, m], m=0..n-1 via stacked
    companion matrices.  Leading coeff assumed ~nonzero (generic curve)."""
    K, np1 = A.shape
    n = np1 - 1
    if n <= 0:
        return np.zeros((K, 0), complex)
    lead = A[:, -1]
    # normalise so w^n coeff = 1
    An = A / lead[:, None]
    # companion matrix (numpy convention): for monic p = w^n + c_{n-1} w^{n-1}+...+c0
    comp = np.zeros((K, n, n), complex)
    if n > 1:
        idx = np.arange(n - 1)
        comp[:, idx + 1, idx] = 1.0                 # sub-diagonal ones
    comp[:, :, -1] = -An[:, :n]                      # last column = -c0..-c_{n-1}
    return np.linalg.eigvals(comp)                   # (K, n)


def sample_curve(C, xrange, Nx, Ntheta, w_is_var=True):
    """Sweep z over a grid of (x=log|z|, theta=arg z); solve for w roots.
    Returns arrays (all flattened over the grid x roots):
        X  = log|z|   (repeated per root)
        Y  = log|w|
        TH = arg z    (in [0,2pi))
        PH = arg w    (in [0,2pi))
    """
    xs = np.linspace(xrange[0], xrange[1], Nx)
    thetas = np.linspace(0, 2 * np.pi, Ntheta, endpoint=False)
    n = C.shape[1] - 1
    Xo = np.empty((Nx, Ntheta, n)); Yo = np.empty_like(Xo)
    THo = np.empty_like(Xo);        PHo = np.empty_like(Xo)
    for a, x in enumerate(xs):
        z = np.exp(x + 1j * thetas)                  # (Ntheta,)
        A = poly_w_coeffs(C, z)                       # (Ntheta, n+1)
        R = roots_batch(A)                            # (Ntheta, n)
        Xo[a] = x
        THo[a] = thetas[:, None]
        Yo[a] = np.log(np.abs(R) + 1e-300)
        PHo[a] = np.mod(np.angle(R), 2 * np.pi)
    return Xo.ravel(), Yo.ravel(), THo.ravel(), PHo.ravel()


def ronkin_and_order(C, xr, yr, Nx, Ny, Kphase):
    """Ronkin function N(x,y) and order map (grad N) over a grid.
    N(x,y) = mean over torus of log|P(e^{x+is}, e^{y+it})|.
    Returns N (Ny,Nx), and the integer-ish order gradient components gx, gy."""
    xs = np.linspace(xr[0], xr[1], Nx)
    ys = np.linspace(yr[0], yr[1], Ny)
    s = np.linspace(0, 2 * np.pi, Kphase, endpoint=False)
    t = np.linspace(0, 2 * np.pi, Kphase, endpoint=False)
    S, T = np.meshgrid(s, t, indexing='ij')          # (Kp,Kp)
    eis = np.exp(1j * S).ravel()                      # phase of z
    eit = np.exp(1j * T).ravel()                      # phase of w
    Iz, Jw = C.shape
    # Precompute phase powers: eis^i, eit^j  (Kp^2, Iz) and (Kp^2, Jw)
    ei_pow = np.vander(eis, Iz, increasing=True)      # (M, Iz)
    et_pow = np.vander(eit, Jw, increasing=True)      # (M, Jw)
    M = eis.size
    N = np.empty((Ny, Nx))
    for b, y in enumerate(ys):
        ew = np.exp(y) ** np.arange(Jw)               # |w|^j via e^{y*j}
        # value factor per (i,j): C[i,j] * e^{x i} * e^{y j} * eis^i * eit^j
        for a, x in enumerate(xs):
            ez = np.exp(x) ** np.arange(Iz)
            coef = C * ez[:, None] * ew[None, :]       # (Iz,Jw)
            # P over torus = sum_ij coef[i,j] ei_pow[:,i] et_pow[:,j]
            Pz = (ei_pow @ coef)                       # (M, Jw)
            Pval = np.einsum('mj,mj->m', Pz, et_pow)   # (M,)
            N[b, a] = np.mean(np.log(np.abs(Pval) + 1e-300))
    gy, gx = np.gradient(N, ys, xs)
    return N, gx, gy
