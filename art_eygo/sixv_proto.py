"""Six-vertex DWBC sampler prototype (ice point a=b=c=1).

Config = +-1 integer height function H on (N+1)x(N+1) faces:
  adjacent faces differ by exactly +-1  => 2-in-2-out (ice rule) automatic.
DWBC boundary (saddle pinning): H(x,0)=x, H(0,y)=y, H(N,y)=N-y, H(x,N)=N-x.
Uniform measure (a=b=c=1) sampled by checkerboard heat-bath extremum flips:
  flippable face = interior local max (all 4 nbrs = c-1) or local min (all = c+1);
  flip by -+2 with prob 1/2 (heat-bath, weight ratio 1 at ice point).
"""
import numpy as np
from PIL import Image
import sys

def init_H(N):
    x = np.arange(N+1)[:,None]
    y = np.arange(N+1)[None,:]
    return np.abs(x - y).astype(np.int32)   # valid +-1 function w/ correct boundary

def check_valid(H):
    dx = np.abs(np.diff(H, axis=0))
    dy = np.abs(np.diff(H, axis=1))
    return (dx==1).all() and (dy==1).all()

def sweep(H, rng, parity):
    M = H.shape[0]
    c = H[1:-1,1:-1]
    up    = H[1:-1, :-2]
    down  = H[1:-1, 2:]
    left  = H[:-2, 1:-1]
    right = H[2:, 1:-1]
    xx, yy = np.meshgrid(np.arange(1,M-1), np.arange(1,M-1), indexing='ij')
    pmask = ((xx+yy) % 2) == parity
    is_max = (left==c-1)&(right==c-1)&(up==c-1)&(down==c-1)
    is_min = (left==c+1)&(right==c+1)&(up==c+1)&(down==c+1)
    flip = (is_max | is_min) & pmask & (rng.random(c.shape) < 0.5)
    delta = np.where(is_min, 2, -2)
    c_new = c + np.where(flip, delta, 0)
    H[1:-1,1:-1] = c_new
    return int(flip.sum())

def flippable_density(H):
    c = H[1:-1,1:-1]
    up=H[1:-1,:-2]; down=H[1:-1,2:]; left=H[:-2,1:-1]; right=H[2:,1:-1]
    is_max=(left==c-1)&(right==c-1)&(up==c-1)&(down==c-1)
    is_min=(left==c+1)&(right==c+1)&(up==c+1)&(down==c+1)
    return float((is_max|is_min).mean())

def vertex_types(H):
    """Classify each of the NxN vertices. Faces around vertex (i,j):
       f00=H[i,j], f10=H[i+1,j], f11=H[i+1,j+1], f01=H[i,j+1] (cyclic order).
       steps around: two +1 two -1. Adjacent ups (++--) -> ferro (a/b), alternating (+-+-) -> c.
       Return: 0..3 ferro-orientation code, 4/5 for c-types."""
    f00=H[:-1,:-1]; f10=H[1:,:-1]; f11=H[1:,1:]; f01=H[:-1,1:]
    s0=f10-f00; s1=f11-f10; s2=f01-f11; s3=f00-f01   # cyclic steps, each +-1
    alt = (s0*s2 < 0) & (s1*s3 < 0)  # +-+- pattern => c vertex (saddle)
    # ferro orientation by (gradient) : use (f10-f00, f01-f00) sign combos
    gx = f10 - f00   # +-1
    gy = f01 - f00
    code = np.where(alt, 4 + ((s0>0).astype(int)),  # c1/c2
                    (gx>0).astype(int) + 2*(gy>0).astype(int))
    return code, alt

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv)>1 else 64
    sweeps = int(sys.argv[2]) if len(sys.argv)>2 else 20000
    rng = np.random.default_rng(1)
    H = init_H(N)
    assert check_valid(H), "init invalid"
    for s in range(sweeps):
        sweep(H, rng, 0); sweep(H, rng, 1)
        if s % (sweeps//10 or 1) == 0:
            assert check_valid(H), f"invalid at sweep {s}"
            print(f"sweep {s:6d}  flippable_density={flippable_density(H):.4f}", flush=True)
    print("final valid:", check_valid(H), " flippable:", flippable_density(H))
    # frozen corner purity check
    code, alt = vertex_types(H)
    n = code.shape[0]
    k = n//6
    print("corner c-vertex fractions (want ~0 = frozen):",
          f"BL={alt[:k,:k].mean():.3f} BR={alt[-k:,:k].mean():.3f} "
          f"TL={alt[:k,-k:].mean():.3f} TR={alt[-k:,-k:].mean():.3f} "
          f"center={alt[n//2-k:n//2+k, n//2-k:n//2+k].mean():.3f}")
    # quick color render of vertex types
    pal = np.array([[40,60,120],[90,140,220],[200,120,60],[230,200,90],
                    [255,255,255],[120,255,220]], np.uint8)
    img = pal[code]
    Image.fromarray(np.transpose(img,(1,0,2))[::-1]).resize((512,512),Image.NEAREST).save("art_eygo/sixv_proto.png")
    print("saved art_eygo/sixv_proto.png")
