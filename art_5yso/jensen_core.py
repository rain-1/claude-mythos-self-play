import numpy as np
import mpmath as mp
from math import comb

mp.mp.dps = 50

def Phi(u):
    """Riemann's Phi(u): even, positive, super-exponentially decaying.
       Xi(t)=xi(1/2+it)=2 int_0^inf Phi(u) cos(ut) du."""
    u = mp.mpf(u)
    s = mp.mpf(0)
    e2u = mp.e**(2*u)
    n = 1
    while True:
        term = (2*mp.pi**2*n**4*mp.e**(mp.mpf(9)*u/2) - 3*mp.pi*n**2*mp.e**(mp.mpf(5)*u/2))*mp.e**(-mp.pi*n**2*e2u)
        s += term
        if abs(term) < mp.mpf(10)**(-mp.mp.dps-5) and n>2:
            break
        n += 1
        if n>200: break
    return s

def gamma_moment(n, U=None):
    """gamma(n) = int_0^inf Phi(u) u^{2n} du  (the positive Polya moment sequence)."""
    return mp.quad(lambda u: Phi(u)*u**(2*n), [0, mp.mpf('0.5'), 1, 2, 4])

def gamma_seq(K):
    return [gamma_moment(n) for n in range(K+1)]

def polya_seq(K):
    """The Jensen/Polya sequence a(n) = moment(n)/(2n)!  (Taylor coeffs of Xi in z).
       Hyperbolicity of the Jensen polynomials of a(n)  <=>  RH."""
    M = gamma_seq(K)
    return [M[n]/mp.factorial(2*n) for n in range(K+1)]

def jensen_roots(a, d, n):
    coeff = [mp.mpf(comb(d,j))*a[n+j] for j in range(d+1)]  # low->high, all >0
    cf = np.array([float(c) for c in coeff], dtype=np.float64)
    logs = np.log(np.abs(cf)+1e-300); cf = cf*np.exp(-logs.mean())
    return np.roots(cf[::-1])

def hermite_zeros(d):
    from numpy.polynomial.hermite import hermgauss
    x,_ = hermgauss(d); return np.sort(x)

if __name__=="__main__":
    import time
    # sanity: Xi(0)=2*gamma_moment(0) should equal xi(1/2)=0.497120778...
    g0 = gamma_moment(0)
    print("2*gamma(0) =", mp.nstr(2*g0,10), " expect xi(1/2)=0.4971207782")
    K=62
    t=time.time(); g=gamma_seq(K); print(f"gamma[0..{K}] in {time.time()-t:.1f}s")
    print("all gamma>0:", all(x>0 for x in g))
    print("gamma[0..5]:", [mp.nstr(x,5) for x in g[:6]])
    np.save("gamma_seq.npy", np.array([float(x) for x in g]))
    # also save high-precision as strings
    with open("gamma_seq.txt","w") as f:
        for x in g: f.write(mp.nstr(x,40)+"\n")
    # hyperbolicity + Hermite convergence (should IMPROVE with n)
    for d in [6,12,20]:
        for n in [2,15,40]:
            if n+d>K: continue
            r=jensen_roots(g,d,n)
            him=np.abs(r.imag).max()/(np.abs(r.real).max()+1e-12)
            rr=np.sort(r.real); rz=(rr-rr.mean())/rr.std()
            hz=hermite_zeros(d); hz=(hz-hz.mean())/hz.std()
            print(f"d={d:2d} n={n:2d}: |Im|/|Re|={him:.1e}  Hermite-err={np.abs(rz-hz).max():.4f}")
