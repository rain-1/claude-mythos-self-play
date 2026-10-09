"""Curves, Frenet and parallel-transport (Bishop) frames, torsion."""
import numpy as np
def trefoil(t):
    return np.stack([np.sin(t) + 2*np.sin(2*t), np.cos(t) - 2*np.cos(2*t), -np.sin(3*t)], -1)
def torus_knot(p, q, R=2.0, r=0.85):
    def f(t):
        return np.stack([(R + r*np.cos(q*t))*np.cos(p*t), (R + r*np.cos(q*t))*np.sin(p*t), r*np.sin(q*t)], -1)
    return f
def frames(f, n=40000, closed=True):
    t = np.linspace(0, 2*np.pi, n, endpoint=not closed)
    h = t[1] - t[0]
    c = f(t)
    d1 = (np.roll(c, -1, 0) - np.roll(c, 1, 0))/(2*h)
    d2 = (np.roll(c, -1, 0) - 2*c + np.roll(c, 1, 0))/h**2
    d3 = (np.roll(c, -2, 0) - 2*np.roll(c, -1, 0) + 2*np.roll(c, 1, 0) - np.roll(c, 2, 0))/(2*h**3)
    T = d1/np.linalg.norm(d1, axis=1, keepdims=True)
    cr = np.cross(d1, d2)
    kap = np.linalg.norm(cr, axis=1)/np.linalg.norm(d1, axis=1)**3
    tau = np.einsum('ij,ij->i', cr, d3)/np.maximum(np.einsum('ij,ij->i', cr, cr), 1e-12)
    B = cr/np.linalg.norm(cr, axis=1, keepdims=True)
    N = np.cross(B, T)
    # Bishop frame by double reflection (Wang et al. 2008)
    U = np.zeros_like(T); U[0] = N[0]
    for i in range(len(t) - 1):
        v1 = c[i+1] - c[i]; c1 = v1 @ v1
        rL = U[i] - (2/c1)*(v1 @ U[i])*v1
        tL = T[i] - (2/c1)*(v1 @ T[i])*v1
        v2 = T[i+1] - tL; c2 = v2 @ v2
        U[i+1] = rL - (2/c2)*(v2 @ rL)*v2 if c2 > 1e-20 else rL
    # closing holonomy: angle from transported U[-1]->U[0] around T[0]
    V = np.cross(T, U)
    # angle of Frenet N in the Bishop frame
    psi = np.unwrap(np.arctan2(np.einsum('ij,ij->i', N, V), np.einsum('ij,ij->i', N, U)))
    sl = np.linalg.norm(d1, axis=1)*h
    s = np.concatenate([[0], np.cumsum(sl)[:-1]])
    return dict(t=t, c=c, T=T, N=N, B=B, U=U, V=V, kap=kap, tau=tau, psi=psi, s=s, L=sl.sum())
if __name__ == '__main__':
    F = frames(trefoil, 20000)
    print('L', F['L'], 'tau range', F['tau'].min(), F['tau'].max(), 'kappa', F['kap'].min(), F['kap'].max())
    # check psi' = tau * ds  (Frenet normal turns at rate tau relative to a parallel frame)
    dpsi = np.gradient(F['psi'])
    print('psi total', F['psi'][-1] - F['psi'][0], ' int tau ds', np.sum(F['tau']*np.gradient(F['s'])))
