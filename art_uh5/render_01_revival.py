"""01 — The Wave That Remembers (Talbot / quantum carpet).  4096x4096 centerpiece.

A Gaussian wave-packet in an infinite square well, given a kick (momentum k0),
bounces forever.  psi(x,t) = sum_n c_n sqrt2 sin(n pi x) exp(-i n^2 t).
Because the energies E_n = n^2 are PERFECT SQUARES, the quadratic phases
re-cohere: at t = 2pi the packet reassembles exactly (a full quantum revival),
and at every rational fraction p/q of that time it splits into q little copies
of itself (fractional revivals).  Horizontal = position in the well; vertical =
one full revival period of time.  The dark 'canals' and the bright ridges are
a genuinely fractal interference lattice -- structure at every scale, which is
why it earns 4096^2.
"""
import numpy as np
from PIL import Image
import time

def carpet(Nx, Nt, M, x0=0.5, sig=0.02, k0=60.0, tmax=2*np.pi, tchunk=32):
    x = np.linspace(0,1,Nx,endpoint=False) + 0.5/Nx
    n = np.arange(1,M+1)
    Phi = (np.sqrt(2.0)*np.sin(np.outer(n, np.pi*x))).astype(np.complex64)   # [M,Nx]
    psi0 = np.exp(-(x-x0)**2/(2*sig**2)) * np.exp(1j*k0*x)
    c = ((np.sqrt(2.0)*np.sin(np.outer(n,np.pi*x))) @ psi0)/Nx               # [M]
    c = c.astype(np.complex64)
    t = np.linspace(0,tmax,Nt)
    n2 = (n*n).astype(np.float64)
    PhiT = Phi.T.copy()                                                      # [Nx,M]
    out = np.empty((Nt,Nx), np.float32)
    for i in range(0,Nt,tchunk):
        tt = t[i:i+tchunk]
        ph = np.exp(-1j*np.outer(n2, tt)).astype(np.complex64)               # [M,c]
        amp = c[:,None]*ph
        psi = PhiT @ amp                                                     # [Nx,c]
        out[i:i+tchunk] = (psi.real**2 + psi.imag**2).T
    return out

def colormap(f, stops):
    pos=np.array([s[0] for s in stops]); cols=np.array([s[1] for s in stops])
    return np.stack([np.interp(f,pos,cols[:,c]) for c in range(3)],-1)

PAL=[(0,[0.015,0.01,0.05]),(0.16,[0.03,0.10,0.20]),(0.40,[0.05,0.45,0.56]),
     (0.68,[0.28,0.85,0.86]),(0.88,[0.80,0.98,0.93]),(1.0,[1.0,1.0,0.96])]

def main(S=4096, M=360):
    t0=time.time()
    F = carpet(S,S,M)
    print('field', time.time()-t0, F.shape, F.max())
    f = np.clip(F/(np.percentile(F,99.7)+1e-9),0,1)**0.55
    img = colormap(f, PAL)
    Image.fromarray((np.clip(img,0,1)*255).astype('uint8')).save('art_uh5/01_the_wave_that_remembers.png')
    print('saved', time.time()-t0)

if __name__=="__main__":
    main()
