import numpy as np, time
from pearcey_fft import pearcey_fft
# supersample 2x -> 8192 compute, will downscale for AA of fine fringes
S=8192
xs=np.linspace(-20,20,S); ys=np.linspace(-14,6,S)
t0=time.time()
Pe=pearcey_fft(xs,ys,Nt=1<<16,T=8.5,taper=0.10)
print("compute",time.time()-t0,"shape",Pe.shape,"ampmax",np.abs(Pe).max())
np.save('hero_field_8192.npy', Pe.astype(np.complex64))
print("saved", time.time()-t0)
