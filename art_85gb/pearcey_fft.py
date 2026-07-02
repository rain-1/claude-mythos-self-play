import numpy as np

def pearcey_fft(xs, ys, T=7.0, Nt=1<<14, taper=0.12):
    """Pe(x,y)=int exp(i(t^4+y t^2+x t))dt via FFT over t (it's a Fourier transf in x).
    Returns complex field on meshgrid(xs,ys). xs must be a uniform grid."""
    dt = 2*T/Nt
    t = (np.arange(Nt)-Nt//2)*dt
    # smooth endpoint taper (Tukey) to kill truncation ringing
    w = np.ones(Nt)
    nt = int(taper*Nt)
    ramp = 0.5*(1-np.cos(np.linspace(0,np.pi,nt)))
    w[:nt]=ramp; w[-nt:]=ramp[::-1]
    # FFT gives x on grid dx=2pi/(Nt*dt); we then interpolate onto requested xs
    dx = 2*np.pi/(Nt*dt)
    m = np.fft.fftfreq(Nt, d=1.0/Nt)          # integer indices -Nt/2..Nt/2-1 (as freqs)
    xg = m*dx                                  # x grid (unsorted, fft order)
    order = np.argsort(xg); xg_s = xg[order]
    t2 = t*t; t4 = t2*t2
    out = np.empty((len(ys), len(xs)), np.complex128)
    phase_t = np.exp(1j*t4)*w*dt
    for j,y in enumerate(ys):
        g = phase_t*np.exp(1j*y*t2)
        # S(x_m)=dt*sum_k g_k exp(i x_m t_k); with x_m=m*dx, t_k=(k-Nt/2)dt
        # = dt*exp(-i pi m??)... implement via fft with index bookkeeping:
        # sum_k g_k exp(i 2pi m (k-Nt/2)/Nt) = exp(-i pi m) * sum_k g_k exp(i2pi mk/Nt)
        #                                     = (-1)^m * Nt*ifft(g)[m]
        S = np.fft.ifft(g)*Nt
        S = S*((-1.0)**np.arange(Nt))
        Sx = S[order]                          # on xg_s
        out[j] = np.interp(xs, xg_s, Sx.real) + 1j*np.interp(xs, xg_s, Sx.imag)
    return out

if __name__=="__main__":
    import time
    # cross-check vs rotated-contour ground truth at a few points
    def pearcey_ref(x,y,R=3.4,Nr=4000):
        r=np.linspace(-R,R,Nr); dr=r[1]-r[0]
        a=y*np.exp(1j*3*np.pi/4); b=x*np.exp(1j*5*np.pi/8)
        return np.exp(1j*np.pi/8)*np.sum(np.exp(-r**4+a*r*r+b*r))*dr
    xs=np.linspace(-14,14,320); ys=np.linspace(-10,8,320)
    t0=time.time(); Pe=pearcey_fft(xs,ys); print("fft time",time.time()-t0)
    for (xi,yi) in [(0.0,0.0),(0.0,-6.0),(5.0,3.0),(-8.0,4.0),(2.0,-3.0)]:
        i=np.argmin(np.abs(ys-yi)); k=np.argmin(np.abs(xs-xi))
        ref=pearcey_ref(xs[k],ys[i])
        print(f"x={xs[k]:.2f} y={ys[i]:.2f}  fft={Pe[i,k]:.4f}  ref={ref:.4f}  |d|={abs(Pe[i,k]-ref):.2e}")
