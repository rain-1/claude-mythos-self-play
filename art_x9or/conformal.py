"""Riemann map of a smooth star-shaped domain onto the disc, the way MO 515949 asks for it:
three boundary 'doors' z1,z2,z3, and every point is sent to the disc point with the same three
Brownian exit probabilities.  Numerically: double-layer Nyström for Re F = log|t-a|, Plemelj for the
boundary values of F, f = (z-a) e^{-F}, then a disc Möbius sending f(z_k) -> 1, w, w^2."""
import numpy as np, subprocess, os
HERE = os.path.dirname(os.path.abspath(__file__))

def curve_from_r(rfun, N):
    s = 2*np.pi*np.arange(N)/N
    r = rfun(s)
    t = r*np.exp(1j*s)
    k = np.fft.fftfreq(N, 1.0/N)
    tp = np.fft.ifft(1j*k*np.fft.fft(t)); tpp = np.fft.ifft(-(k**2)*np.fft.fft(t))
    return s, t, tp, tpp

def solve_map(rfun, N=2048, a=0j):
    s, t, tp, tpp = curve_from_r(rfun, N)
    h = 2*np.pi/N
    phi = np.log(np.abs(t - a))
    D = t[None, :] - t[:, None]
    np.fill_diagonal(D, 1.0)
    K = np.imag(tp[None, :]/D)*h/(2*np.pi)
    np.fill_diagonal(K, np.imag(tpp/(2*tp))*h/(2*np.pi))
    A = 0.5*np.eye(N) + K
    mu = np.linalg.solve(A, phi)
    # Plemelj interior boundary values: F = mu0 + (1/2πi) Σ h (mu_j - mu0) t'_j/(t_j - t0), diag = mu'(s0)
    k = np.fft.fftfreq(N, 1.0/N)
    mup = np.real(np.fft.ifft(1j*k*np.fft.fft(mu)))
    Mq = (mu[None, :] - mu[:, None])*tp[None, :]/D
    np.fill_diagonal(Mq, mup)
    Fb = mu + Mq.sum(1)*h/(2j*np.pi)
    chk = np.max(np.abs(Fb.real - phi))
    fb = (t - a)*np.exp(-Fb)
    return dict(s=s, t=t, w=tp*h, F=Fb, f=fb, a=a, chk=chk, modchk=np.max(np.abs(np.abs(fb)-1)))

def disc_mobius(p):
    """Möbius of the disc sending three positively ordered unit points p -> 1, ω, ω²."""
    q = np.exp(2j*np.pi*np.arange(3)/3)
    def cross(z, z1, z2, z3):  # map to 0,1,inf in upper half-plane style: (z-z1)(z2-z3)/((z-z3)(z2-z1))
        return (z - z1)*(z2 - z3)/((z - z3)*(z2 - z1))
    def cross_inv(u, z1, z2, z3):
        k = (z2 - z3)/(z2 - z1)
        return (u*z3 - k*z1)/(u - k)
    return lambda z: cross_inv(cross(z, *p), *q)

def eval_F(sol, Z, tag=None):
    tag = tag or f'{os.getpid()}'
    N = len(sol['t'])
    bf = os.path.join(HERE, f'_bnd_{tag}.bin'); pf = os.path.join(HERE, f'_pts_{tag}.bin'); of = os.path.join(HERE, f'_out_{tag}.bin')
    with open(bf, 'wb') as fh:
        np.array([N], np.int64).tofile(fh)
        sol['t'].astype(np.complex128).tofile(fh); sol['w'].astype(np.complex128).tofile(fh); sol['F'].astype(np.complex128).tofile(fh)
    Z.astype(np.complex128).tofile(pf)
    subprocess.run([os.path.join(HERE, 'doors'), 'map', bf, pf, of], check=True)
    out = np.fromfile(of, np.complex128)
    for x in (bf, pf, of): os.remove(x)
    return out

def tiles(W, tag=None, maxit=400):
    tag = tag or f'{os.getpid()}'
    pf = os.path.join(HERE, f'_tp_{tag}.bin'); of = os.path.join(HERE, f'_to_{tag}.bin')
    W.astype(np.complex128).tofile(pf)
    subprocess.run([os.path.join(HERE, 'doors'), 'tile', pf, of, str(maxit)], check=True)
    out = np.fromfile(of, np.float64).reshape(-1, 8)
    os.remove(pf); os.remove(of)
    return out

def exit_probs(w):
    """Harmonic measure of the three arcs [1,ω],[ω,ω²],[ω²,1] seen from w in the disc."""
    q = np.exp(2j*np.pi*np.arange(4)/3)
    P = []
    for k in range(3):
        a, b = q[k], q[k+1]
        ang = np.angle((b - w)/(a - w)) % (2*np.pi)   # directed angle subtended (0, 2π)
        P.append(ang/np.pi - 1.0/3.0)
    return np.stack(P, -1)

if __name__ == '__main__':
    rf = lambda s: 1 + 0.22*np.cos(5*s)
    for N in (512, 1024, 2048):
        sol = solve_map(rf, N)
        print(N, sol['chk'], sol['modchk'])
    z = np.array([0.3+0.2j, 0.9+0.05j, -0.5j])
    for N in (1024, 2048):
        sol = solve_map(rf, N); print(N, eval_F(sol, z))
    print(exit_probs(np.array([0j, 0.5])))
