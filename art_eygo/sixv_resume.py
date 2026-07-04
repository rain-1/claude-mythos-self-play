"""Resume the six-vertex hero sample from a cached H_<tag>.npy and run more sweeps."""
import numpy as np, sys, time
sys.path.insert(0,'art_eygo')
from sixv import make_parity, sweep, valid, flip_density

tag=sys.argv[1]; more=int(sys.argv[2]); done0=int(sys.argv[3]) if len(sys.argv)>3 else 0
H=np.load(f"art_eygo/H_{tag}.npy"); N=H.shape[0]-1
assert valid(H), "loaded H invalid!"
pe,po=make_parity(N+1); rng=np.random.default_rng(99)
t0=time.time(); chk=max(1,more//15)
print(f"RESUME tag={tag} N={N} loaded valid fd={flip_density(H):.4f} running {more} more sweeps", flush=True)
for s in range(more+1):
    if s%chk==0:
        tot=done0+s
        print(f"  +{s:7d} (total {tot}, {tot/(N*N):.2f}N^2) t={time.time()-t0:6.1f}s fd={flip_density(H):.4f}", flush=True)
        np.save(f"art_eygo/H_{tag}.npy", H)
    if s<more: sweep(H,rng,pe); sweep(H,rng,po)
assert valid(H)
np.save(f"art_eygo/H_{tag}.npy", H)
print(f"DONE total_sweeps={done0+more} ({(done0+more)/(N*N):.2f}N^2) valid={valid(H)} fd={flip_density(H):.4f}")
