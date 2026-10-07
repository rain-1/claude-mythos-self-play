"""Duistermaat's complex Riemann function phi(t)=sum_{n>=1} e^{i pi n^2 t}/(i pi n^2), t in [0,2],
sampled exactly on t=2k/M by one FFT (n^2 mod M bins)."""
import numpy as np
def phi(M=1<<22, nmax=200000):
    n=np.arange(1,nmax+1,dtype=np.int64)
    a=np.zeros(M,complex)
    np.add.at(a,(n*n)%M,1/(1j*np.pi*n.astype(float)**2))
    # phi(2k/M)=sum a_j e^{2 pi i j k/M}
    return np.fft.ifft(a)*M
if __name__=="__main__":
    import sys
    z=phi(); np.save('proto/phi.npy',z.astype(np.complex64)); print(z[:3],abs(z).max(), z.real.min(),z.real.max(),z.imag.min(),z.imag.max())
