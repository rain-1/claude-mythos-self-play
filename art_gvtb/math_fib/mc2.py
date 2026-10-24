# MC cross-check using numpy PCG64 random bits (pre-generated per batch) instead of xorshift.
import os; os.environ["NUMBA_NUM_THREADS"]="1"
import numpy as np, numba, sys, time
@numba.njit(cache=True)
def batch(al, bits, y):
    lo=1-al; hi=1+al; acc=0.0; prod=1.0
    n = bits.size
    for i in range(n):
        r = bits[i]
        u = hi if r & 1 else lo
        v = hi if r & 2 else lo
        y = u + v/y
        prod *= y
        if (i & 15) == 15:
            acc += np.log(prod); prod = 1.0
    acc += np.log(prod)
    return acc/n, y
if __name__=="__main__":
    from eta_koopman import eta
    rng = np.random.default_rng(12345)
    for al in map(float, sys.argv[1:]):
        t=time.time(); y=1.0; r=[]
        for b in range(1000):
            bits = rng.integers(0, 4, size=10**6, dtype=np.uint8)
            m, y = batch(al, bits, y); r.append(m)
        r=np.array(r)
        print(f"alpha={al}: MC(PCG64, 1e9 steps) {r.mean():.10f} +- {r.std()/np.sqrt(len(r)):.1e}  operator {eta(al,200)[0]:.10f}  diff/sigma {(r.mean()-eta(al,200)[0])/(r.std()/np.sqrt(len(r))):+.2f} ({time.time()-t:.0f}s)", flush=True)
