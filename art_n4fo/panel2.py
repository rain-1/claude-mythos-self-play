"""PANEL 2 — 'The Tighter Cage': Brauer's ovals of Cassini.

The same eigenvalues, a strictly tighter cage. Gershgorin: |z-a_ii| <= R_i (a disc).
Brauer: |z-a_ii||z-a_jj| <= R_i R_j for SOME pair i!=j (a Cassini oval / lemniscate).
The Brauer set is contained in the Gershgorin set and hugs the spectrum tighter.
We draw the loose disc cage as faint ghost rings and the tight Cassini ovals as the
bright lemniscate cage, with the eigenvalue-truth blazing inside.
"""
import numpy as np
from kit import Canvas, ring_field, tonemap, bloom
from PIL import Image

def build_matrix(seed=2):
    """A compact matrix (small n) so the pairwise ovals stay legible; some diagonal
    entries close together so their Cassini ovals fuse into peanuts/lemniscates."""
    rng=np.random.default_rng(seed)
    # centres: two close clusters + a couple of loners -> mix of fused peanuts and eyes
    centers=np.array([
        -2.4+1.9j, -1.7+1.1j,        # close pair -> peanut
         2.2+1.6j,  2.9+0.7j,        # close pair -> peanut
        -0.2-2.2j,  0.7-2.6j,        # close pair low
         0.1+0.2j,                    # centre loner
        -3.3-1.0j,  3.2-1.6j,        # far loners
    ],complex)
    n=len(centers)
    A=np.zeros((n,n),complex)
    A[np.diag_indices(n)]=centers
    radii=np.array([1.05,1.15,1.0,1.1,1.2,1.0,1.35,0.75,0.8])
    for i in range(n):
        js=[j for j in range(n) if j!=i]
        w=rng.random(len(js)); w/=w.sum()
        ph=np.exp(1j*2*np.pi*rng.random(len(js)))
        for jj,j in enumerate(js):
            A[i,j]=radii[i]*w[jj]*ph[jj]
    return A, centers, radii

def render(S, out, seed=2, half=6.0, k_tone=1.25, gamma=0.85):
    A,centers,radii=build_matrix(seed)
    lam=np.linalg.eigvals(A)
    n=len(centers)
    # verify Brauer containment
    def in_brauer(l):
        for i in range(n):
            for j in range(i+1,n):
                if abs(l-centers[i])*abs(l-centers[j])<=radii[i]*radii[j]+1e-7: return True
        return False
    ok=all(in_brauer(l) for l in lam)
    ok_g=all(np.any(np.abs(l-centers)<=radii+1e-9) for l in lam)
    print(f"[panel2] n={n}  gershgorin={ok_g}  brauer={ok}")

    C=Canvas(S, zc=0+0j, half=half); Z=C.grid_Z()

    # Brauer field g(z)=min_{i<j} |z-c_i||z-c_j|/(R_i R_j); Brauer set = {g<=1}
    g=np.full((S,S), np.inf)
    for i in range(n):
        di=np.abs(Z-centers[i])
        for j in range(i+1,n):
            dj=np.abs(Z-centers[j])
            g=np.minimum(g, di*dj/(radii[i]*radii[j]))

    # loose Gershgorin discs = faint steel-blue ghost cage (the looser bound = uncertainty)
    wr=2*half/S*1.1
    ghost=np.zeros((S,S))
    for c,r in zip(centers,radii):
        ghost+=ring_field(Z,c,r,wr*1.4)
    C.add_field(ghost*0.30, np.array([0.34,0.48,0.70]))

    # tight Cassini cage WARMS toward gold as it closes on the truth (= certainty)
    inside=np.clip(1.0-g,0,1)                 # 1 deep inside, 0 at boundary
    C.add_field(np.tanh(inside*2.2)*0.19, np.array([0.82,0.60,0.28]))
    # boundary: |g-1| small, width in g-units scaled so it's ~constant screen width
    gg=np.abs(g-1.0)
    edge=np.exp(-(gg/0.038)**2)
    C.add_field(edge*0.95, np.array([1.0,0.83,0.50]))

    # eigenvalue stars — the caged truth
    sig=0.058
    for l in lam:
        blob=np.exp(-(np.abs(Z-l)/sig)**2)
        C.add_field(blob*3.2, np.array([1.0,0.95,0.85]))

    buf=bloom(C.buf,[(S/760*1.4,0.85),(S/760*4.5,0.5),(S/760*13,0.3)])
    img=tonemap(buf,k=k_tone,gamma=gamma)
    Image.fromarray(img).save(out)
    print(f"[panel2] wrote {out} {S}x{S}")

if __name__=="__main__":
    import sys
    S=int(sys.argv[1]) if len(sys.argv)>1 else 760
    out=sys.argv[2] if len(sys.argv)>2 else "variants/panel2_proto.png"
    render(S,out)
