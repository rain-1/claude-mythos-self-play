# Independent rigorous-style bracket: for each word w of length k, y -> log f_w(y) is monotone,
# so E log Y_k(y0=a) and E log Y_k(y0=b) bracket eta = E_mu log Y_k (mu supported on [a,b]).
import numpy as np, sys
from eta_koopman import support, eta
for al in map(float, sys.argv[1:]):
    a,b = support(al); res=[]
    for y0 in (a,b):
        y = np.array([y0])
        for k in range(12):
            y = np.concatenate([u + v/y for u in (1-al,1+al) for v in (1-al,1+al)])
        res.append(np.log(y).mean())
    print(al, min(res), max(res), "width %.1e"%abs(res[0]-res[1]), "operator", eta(al,200)[0])
