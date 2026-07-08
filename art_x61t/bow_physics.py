"""Semiclassical rainbow: exact scattering intensity I(gamma, lambda) for a water sphere.

Physics:
  ray with impact parameter b (units of drop radius R): sin i = b, sin i = n sin r.
  Deviation after p internal reflections: D_p(b) = 2(i - r) + p*(pi - 2 r).
  Semiclassical amplitude  f(theta) ~ (1/sqrt(sin theta)) * Int db sqrt(b) a(b)
                                       exp( i k R [ S(b) - b theta ] ),
  with S(b) = int_0^b D_p(b') db'  (deflection = dS/db), a(b) = Fresnel amplitude chain.
  Stationary phase reproduces geometric optics; near the rainbow (D_p'(b)=0) the
  integral IS Airy's 1838 rainbow integral, so supernumerary fringes come out exact.

The integral over a uniform b-grid against a uniform theta-grid is a plain DFT
=> evaluate with one zero-padded FFT per (lambda, polarization, order).

Outputs data/bow_profile.npz: gamma grid (angle from antisolar, rad),
lams (m), I1, I2 (primary/secondary intensity, shape [nlam, ntheta]).
"""
import numpy as np, time, os

t0 = time.time()
os.makedirs("art_x61t/data", exist_ok=True)

# ---------------- water refractive index: Cauchy fit to tabulated values --------------
tab_lam = np.array([404.7, 435.8, 486.1, 546.1, 589.3, 656.3, 706.5])   # nm
tab_n   = np.array([1.3428, 1.3403, 1.3372, 1.3345, 1.3330, 1.3312, 1.3300])
A_ = np.vstack([np.ones_like(tab_lam), 1/tab_lam**2, 1/tab_lam**4]).T
cauchy = np.linalg.lstsq(A_, tab_n, rcond=None)[0]
def n_water(lam_nm):
    return cauchy[0] + cauchy[1]/lam_nm**2 + cauchy[2]/lam_nm**4

# ---------------- geometry + Fresnel ----------------
def deviation(b, n, p):
    i = np.arcsin(np.clip(b, 0, 1))
    r = np.arcsin(np.clip(b / n, 0, 1))
    return 2*(i - r) + p*(np.pi - 2*r)

def fresnel_amp(b, n, p):
    """amplitude weights (s,p pol) for transmit -> p reflections -> transmit"""
    i = np.arcsin(np.clip(b, 0, 1)); r = np.arcsin(np.clip(b / n, 0, 1))
    ci, cr = np.cos(i), np.cos(r)
    rs = (ci - n*cr) / (ci + n*cr)          # external reflection coeff, s
    rp = (n*ci - cr) / (n*ci + cr)          # p
    Ts, Tp = 1 - rs**2, 1 - rp**2           # energy transmittance (in == out)
    Rs, Rp = rs**2, rp**2                   # internal reflectance (same magnitude)
    amp_s = Ts * Rs**(p/2.0)
    amp_p = Tp * Rp**(p/2.0)
    return amp_s, amp_p

# ---------------- semiclassical FFT evaluation ----------------
def order_profile(lam_m, R, p, nb=60000, dth_target=np.pi/16384, thmax=2*np.pi):
    """returns theta grid (deviation angle) and intensity I(theta) for order p."""
    n = n_water(lam_m*1e9)
    k = 2*np.pi/lam_m
    b = (np.arange(nb) + 0.5) / nb
    db = 1.0/nb
    D = deviation(b, n, p)
    S = np.cumsum(D)*db                      # S(b) = int D db
    amp_s, amp_p = fresnel_amp(b, n, p)
    base = np.sqrt(b) * np.exp(1j*(k*R)*S)
    c_target = k*R*db*dth_target
    N = int(np.ceil(2*np.pi/c_target))
    dth = 2*np.pi/(N*k*R*db)                 # actual theta step
    nth = min(int(thmax/dth), N)
    out = np.zeros(nth)
    for a in (amp_s, amp_p):
        u = np.zeros(N, dtype=np.complex128)
        u[:nb] = base*a
        F = np.fft.fft(u)[:nth]
        out += np.abs(F)**2
    th = np.arange(nth)*dth
    return th, out*db*db                      # scale ~ arbitrary but lambda-consistent

def gamma_profile(lam_m, R, gamma, p):
    """intensity vs observer angle gamma (from antisolar) for order p in [1,2]."""
    th, I = order_profile(lam_m, R, p)
    # map deviation D -> gamma = |pi - (D mod 2pi)| ; primary D in (2.4, pi],
    # secondary D in [4.02, 2pi) -> gamma = D - pi
    if p == 1:
        # gamma = pi - D  -> D = pi - gamma
        Dq = np.pi - gamma
    else:
        Dq = np.pi + gamma
    ok = (Dq >= th[0]) & (Dq <= th[-1])
    out = np.zeros_like(gamma)
    out[ok] = np.interp(Dq[ok], th, I)
    # geometric 1/sin(theta_scatter) flux factor; theta_scatter == gamma here
    s = np.sin(np.maximum(gamma, 1e-3))
    return out / s

if __name__ == "__main__":
    import sys
    R = float(sys.argv[1]) if len(sys.argv) > 1 else 0.30e-3    # drop radius (m)
    nlam = int(sys.argv[2]) if len(sys.argv) > 2 else 96
    tag = sys.argv[3] if len(sys.argv) > 3 else ""
    lams = np.linspace(385e-9, 715e-9, nlam)
    gamma = np.linspace(0.0, np.deg2rad(75), 9000)
    I1 = np.zeros((nlam, len(gamma)))
    I2 = np.zeros((nlam, len(gamma)))
    for i, lam in enumerate(lams):
        I1[i] = gamma_profile(lam, R, gamma, 1)
        I2[i] = gamma_profile(lam, R, gamma, 2)
        if i % 16 == 0:
            print(f"lam {lam*1e9:.0f}nm  {time.time()-t0:.1f}s", flush=True)
    np.savez_compressed(f"art_x61t/data/bow_profile{tag}.npz",
                        gamma=gamma, lams=lams, I1=I1, I2=I2, R=R)
    print(f"saved. {time.time()-t0:.1f}s")
