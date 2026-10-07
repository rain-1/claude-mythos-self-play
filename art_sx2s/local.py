import numpy as np, numba
@numba.njit(parallel=True,fastmath=True)
def phi_at(t,N):
    out=np.empty(len(t),np.complex128)
    for k in numba.prange(len(t)):
        s=0j; tk=t[k]
        for n in range(1,N+1):
            a=np.pi*((n*n*tk)%2.0)
            s+=complex(np.cos(a),np.sin(a))/(n*n)
        out[k]=s/(1j*np.pi)
    return out
