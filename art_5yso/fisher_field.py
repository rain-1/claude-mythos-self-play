import numpy as np, time, sys
from fisher_core import neg_beta_f_v_batched

def compute_field(cx, cy, half, N, Nt=2000, aspect=1.0, out="field.npz"):
    """Complex free energy G(v)=-beta f on an N x N grid centered (cx,cy), half-width `half`.
    aspect: width/height of the value window (keeps square pixels if N square)."""
    xs = np.linspace(cx-half*aspect, cx+half*aspect, N)
    ys = np.linspace(cy-half, cy+half, N)
    G = np.empty((N, N), dtype=np.complex128)
    t0=time.time()
    for j in range(N):
        row = xs + 1j*ys[j]
        G[j] = neg_beta_f_v_batched(row, Nt=Nt, chunk=128)
        if j % max(1,N//20)==0:
            el=time.time()-t0
            print(f"  row {j}/{N}  {el:.1f}s  eta {el/(j+1)*(N-j-1):.1f}s", flush=True)
    np.savez_compressed(out, G=G, cx=cx, cy=cy, half=half, N=N, aspect=aspect)
    print("saved", out, "total", round(time.time()-t0,1),"s")
    return G, xs, ys

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv)>1 else "test"
    if mode=="test":
        import time
        row = np.linspace(-2.2,2.2,4096)+0.3j
        t=time.time(); neg_beta_f_v_batched(row,Nt=2000,chunk=128); dt=time.time()-t
        print(f"one 4096-row Nt=2000: {dt:.3f}s -> full 4096^2 ~ {dt*4096/60:.1f} min")
