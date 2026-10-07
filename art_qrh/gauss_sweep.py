"""gamma_2(pi) for every primary prime with norm <= D (split: both pi, conj pi; inert: -q with q^2 <= D)."""
import numpy as np, sys, math
from eis import eisenstein_primes, omega_image, gamma2_split, pow_fq2
D=int(sys.argv[1]); P=eisenstein_primes(D)
rows=[]
for (a,b,N,kind) in P:
    if kind=='s':
        w=omega_image(a,b,N); g=gamma2_split(a,b,N,w)
    else:
        # inert: O/q = F_q[w]; chi(x)^2 = x^{(q^2-1)/3}; e(x/(-q)) = exp(-4 pi i Im(x)/(q sqrt3)) ; x=c+dw, Im x = d sqrt3/2
        q=-a; tot=0j
        # cubic character values: r = x^{(q^2-1)/3} in {1,w,w^2}
        for c in range(q):
            for d in range(q):
                if c==0 and d==0: continue
                ra,rb=pow_fq2(c,d,(q*q-1)//3,q)
                j=0 if (ra,rb)==(1,0) else (1 if (ra,rb)==(0,1) else 2)
                tot+=np.exp(2j*np.pi*j/3)*np.exp(-2j*np.pi*d/q)
        g=tot/q
    rows.append((a,b,N,0 if kind=='s' else 1,g.real,g.imag))
A=np.array(rows); np.save('gauss_%d.npy'%D,A); print(len(A),'primes; |g| range',np.abs(A[:,4]+1j*A[:,5]).min(),np.abs(A[:,4]+1j*A[:,5]).max())
