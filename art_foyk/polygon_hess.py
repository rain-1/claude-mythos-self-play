"""Stiffness spectrum: projected Hessian of the Lagrangian at the regular n-gon."""
import numpy as np

def B_and_cons(theta):
    n = len(theta)
    phi = np.cumsum(theta) - theta[0]
    e = np.stack([np.cos(phi), np.sin(phi)], 1)
    P = np.vstack([[0,0], np.cumsum(e,0)])[:-1]
    c = P.mean(0)
    Bv = n*((P-c)**2).sum()
    cons = np.array([theta.sum()-2*np.pi, e[:,0].sum(), e[:,1].sum()])
    return Bv, cons

def num_grad(f, x, h=1e-6):
    g = np.zeros_like(x)
    for i in range(len(x)):
        xp = x.copy(); xp[i]+=h; xm = x.copy(); xm[i]-=h
        g[i] = (f(xp)-f(xm))/(2*h)
    return g

def num_hess(f, x, h=1e-4):
    n=len(x); H=np.zeros((n,n))
    f0=f(x)
    for i in range(n):
        for j in range(i,n):
            xpp=x.copy(); xpp[i]+=h; xpp[j]+=h
            xpm=x.copy(); xpm[i]+=h; xpm[j]-=h
            xmp=x.copy(); xmp[i]-=h; xmp[j]+=h
            xmm=x.copy(); xmm[i]-=h; xmm[j]-=h
            H[i,j]=H[j,i]=(f(xpp)-f(xpm)-f(xmp)+f(xmm))/(4*h*h)
    return H

print("n  eigenvalues of -projected Hessian (ascending, first 6) [positive = stable max]")
soft = {}
for n in list(range(4,25))+[30,40,50]:
    x = np.full(n, 2*np.pi/n)
    fB = lambda t: B_and_cons(t)[0]
    fC = [lambda t,i=i: B_and_cons(t)[1][i] for i in range(3)]
    gB = num_grad(fB, x)
    J = np.stack([num_grad(c, x) for c in fC])
    lam, *_ = np.linalg.lstsq(J.T, gB, rcond=None)
    fL = lambda t: fB(t) - lam @ B_and_cons(t)[1]
    H = num_hess(fL, x)
    # tangent basis
    _,_,Vt = np.linalg.svd(J)
    T = Vt[3:].T
    Hp = T.T @ H @ T
    ev = np.sort(np.linalg.eigvalsh(-Hp))   # -H: positive eigenvalues = local max directions
    soft[n]=ev
    print(f"{n:3d} ", " ".join(f"{e:9.4f}" for e in ev[:6]))
np.save('hess_spectra.npy', np.array(list(soft.items()), dtype=object), allow_pickle=True)
