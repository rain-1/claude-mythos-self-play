"""Figure 3 — the (2,3,7) triangle group (hyperbolic reflection lens).
Per-pixel fold of the Poincare disk into the fundamental (pi/2,pi/3,pi/7)
triangle, 2-coloured by reflection parity. This kaleidoscope is the universal
symmetry behind both the {3,7} tiling and the Klein quartic."""
import numpy as np, sys, math
sys.path.insert(0,'psl168'); sys.path.insert(0,'octonions')
import figkit
from PIL import Image

def fundamental():
    A=math.pi/7; B=math.pi/2; C=math.pi/3   # angles at O, P, Q
    cOP=(math.cos(C)+math.cos(A)*math.cos(B))/(math.sin(A)*math.sin(B))
    cOQ=(math.cos(B)+math.cos(A)*math.cos(C))/(math.sin(A)*math.sin(C))
    rP=math.tanh(math.acosh(cOP)/2); rQ=math.tanh(math.acosh(cOQ)/2)
    P=complex(rP,0.0); Q=complex(rQ*math.cos(A), rQ*math.sin(A))
    # geodesic circle through P,Q orthogonal to unit circle
    a=np.array([[P.real,P.imag],[Q.real,Q.imag]])
    rhs=np.array([(abs(P)**2+1)/2,(abs(Q)**2+1)/2])
    c=np.linalg.solve(a,rhs); cc=complex(c[0],c[1]); rho=abs(P-cc)
    return A,cc,rho

def render(W=1500):
    A,cc,rho=fundamental()
    ys,xs=np.mgrid[0:W,0:W]
    z=( (xs-W/2)/(W*0.49) ) + 1j*( -(ys-W/2)/(W*0.49) )
    inside=np.abs(z)<0.999
    cnt=np.zeros(z.shape,np.int32)
    beta=A
    ux,uy=math.cos(beta),math.sin(beta)
    z=z.copy()
    for _ in range(120):
        changed=np.zeros(z.shape,bool)
        # m1: real axis, inside Im>=0
        m=inside&(z.imag<0); z=np.where(m, np.conj(z), z); cnt+=m; changed|=m
        # m2: ray at angle beta, inside cross<0  (cross = ux*Im - uy*Re)
        cross=ux*z.imag - uy*z.real
        m=inside&(cross>1e-12); z=np.where(m, np.exp(2j*beta)*np.conj(z), z); cnt+=m; changed|=m
        # m3: circle (cc,rho), inside = outside circle (|z-cc|>rho)
        d=np.abs(z-cc); m=inside&(d<rho-1e-12)
        zr=cc+ (rho*rho)/np.conj(z-cc)
        z=np.where(m, zr, z); cnt+=m; changed|=m
        if not changed.any(): break
    par=(cnt%2)
    # palette: two triangle colours + depth shade by total count
    shade=np.clip(cnt/22.0,0,1)
    base_dark=np.array([0.06,0.05,0.13]); base_light=np.array([0.95,0.78,0.42])
    col=np.where(par[...,None]==0, base_dark, base_light)
    # deepen toward boundary using shade (cool tint in dark, warm in light)
    cool=np.array([0.15,0.35,0.7]);
    img=col*(0.45+0.55*(1-shade[...,None])) + par[...,None]*0  # base
    img=np.where(par[...,None]==0, base_dark*(0.5)+cool*(0.5*shade[...,None]), base_light*(0.6+0.4*(1-shade[...,None])))
    img[~inside]=np.array([0.012,0.013,0.025])
    # boundary ring
    rr=np.abs(z* (W*0.49))  # not used
    out=(np.clip(img,0,1)*255).astype('uint8')
    return Image.fromarray(out)

if __name__=="__main__":
    viz=render(1500)
    body=("Take a single hyperbolic triangle with angles 90°, 60° and 180°/7 (that is π/2, π/3, "
          "π/7) and reflect it in its own three edges, again and again. Because the angles divide "
          "π, the copies fit together perfectly and tile the entire hyperbolic plane — shown here "
          "in the Poincaré disk, two-coloured by whether a tile is reached after an even or odd "
          "number of reflections. This is the (2,3,7) TRIANGLE GROUP, the most efficient "
          "symmetry-engine the hyperbolic plane allows. Group together each cluster of 14 "
          "triangles and you get a heptagon ({7,3}); the orientation-preserving part of this group "
          "is what acts on the Klein quartic, and the smallest closed surface on which the tiling "
          "closes up is that genus-3 surface — with exactly 336 = 2·168 triangles.")
    fig=figkit.caption(viz,"FIGURE 3 · HYPERBOLIC SYMMETRY","The (2,3,7) triangle group",
                       body,accent=(255,190,90),W=1500)
    figkit.save(fig,"psl168/03_237_triangle_group.png")
    print("done",fig.size)
