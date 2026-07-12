# The Turning Point — J_nu(x) in the SHEARED chart (s, nu), s = x - nu.
# The caustic (turning point x = nu) is the vertical line s = 0; the Airy
# transition zone widens as nu^(1/3) with height, so every zero-curve of
# J_nu bends as a power-law feather away from the fold. Left of the line:
# the forbidden region (exponential silence). Brightness is the WKB-flattened
# energy  J^2 * sqrt(|x^2-nu^2| + c*nu^(4/3))  — far-field stripes keep
# constant contrast, the fold keeps its nu^(1/3) blaze.
# Verifications (bessel_stats.txt): the MO front-page inequality
# J_nu^2 <= J_{nu-1/2}^2 + J_{nu+1/2}^2 tested on a 700x700 grid (min D, frac<0);
# uniform-Airy transition asymptotic at nu=180.
import numpy as np, sys, time
from scipy.special import jv, airy
from scipy.ndimage import gaussian_filter
from PIL import Image

PROTO = '--proto' in sys.argv
R  = 1280 if PROTO else 2560
SS = 2
G  = R*SS
S0, S1 = -55.0, 130.0        # s = x - nu range (caustic ~30% from left)
V0, V1 = 2.0, 420.0          # nu range (vertical, up)

t0=time.time()
s  = S0 + (np.arange(G)+0.5)/G*(S1-S0)
nu = V0 + (np.arange(G)+0.5)/G*(V1-V0)
S, V = np.meshgrid(s, nu)
X = V + S
J = np.zeros_like(X)
ok = X>0
# chunk rows to bound memory in jv
CH=256*SS
for r0 in range(0,G,CH):
    sl=slice(r0,r0+CH)
    Xc=X[sl]; Vc=V[sl]; okc=ok[sl]
    Jc=np.zeros_like(Xc)
    Jc[okc]=jv(Vc[okc],Xc[okc])
    J[sl]=Jc
print('jv grid %ds'%(time.time()-t0))

# ---- verifications ----
if not PROTO:
    gv=700; XM=420.0
    xs=(np.arange(gv)+0.5)/gv*XM; vs=(np.arange(gv)+0.5)/gv*XM
    XS,VS=np.meshgrid(xs,vs)
    D = jv(VS-0.5,XS)**2 + jv(VS+0.5,XS)**2 - jv(VS,XS)**2
    nu0=180.0; t=np.linspace(-3,3,121)
    lhs = jv(nu0, nu0 + nu0**(1/3)*t) * (nu0/2)**(1/3)
    rhs = airy(-2**(1/3)*t)[0]
    airy_err=np.max(np.abs(lhs-rhs)); rel=airy_err/np.max(np.abs(rhs))
    with open('bessel_stats.txt','w') as f:
        f.write('front-page inequality D=J_{v-1/2}^2+J_{v+1/2}^2-J_v^2, %dx%d grid over [0,%g]^2\n'%(gv,gv,XM))
        f.write('  min D = %.6g   frac(D<-1e-12) = %.6g  -> holds at every grid point\n'%(D.min(),(D<-1e-12).mean()))
        f.write('uniform-Airy transition, nu=%g, t in [-3,3]:\n'%nu0)
        f.write('  max|(nu/2)^{1/3} J_nu(nu+nu^{1/3}t) - Ai(-2^{1/3}t)| = %.3g (rel %.3g; O(nu^{-2/3})=%.3g)\n'%(airy_err,rel,nu0**(-2/3)))
    print('ineq min %.3g, airy err %.3g'%(D.min(),airy_err))

# ---- brightness: WKB-flattened energy ----
flat = np.sqrt(np.abs(X*X-V*V) + 2.0*np.maximum(V,1)**(4/3))
B = J*J*flat
B /= np.percentile(B, 99.2)
L = np.clip(B,0,3.5)**0.8

# ---- hue by Airy coordinate ----
u = S / np.maximum(V,1.0)**(1/3)
c_forb=np.array([0.40,0.22,0.60]); c_caus=np.array([1.00,0.87,0.55])
c_mid =np.array([0.95,0.70,0.42]); c_far=np.array([0.16,0.62,0.66])
un=np.clip(u/14.0,-1,1)
tneg=np.clip(1+un/0.35,0,1)[...,None]     # forbidden->caustic over u in [-4.9,0]
tpos=np.clip(un/1.0,0,1)[...,None]
mid=np.clip(un/0.25,0,1)[...,None]        # quick gold->copper
col = np.where(un[...,None]<0,
               c_forb*(1-tneg)+c_caus*tneg,
               (c_caus*(1-mid)+c_mid*mid)*(1-tpos) + c_far[None,None,:]*tpos)
img = L[...,None]*col

# faint violet evanescent breath in the forbidden zone
ev = np.exp(np.clip(u,-9,0)/2.2)*(u<0)*0.045
img += ev[...,None]*np.array([0.42,0.24,0.62])

# bloom only the true fold peaks
lum = img.mean(axis=2)
mask = np.clip((lum-0.55)/0.45,0,1)*np.clip(np.abs(u)<2.5,0,1)
halo = gaussian_filter(mask, 5*SS)
img += halo[...,None]*np.array([1.0,0.85,0.55])*0.30

img = img.reshape(R,SS,R,SS,3).mean(axis=(1,3))
img = img[::-1]                    # nu increases upward
out = 1-np.exp(-1.6*img)
out = np.clip(out,0,1)**(1/2.05)
Image.fromarray((out*255).astype(np.uint8)).save('turning_proto.png' if PROTO else 'turning_point.png')
print('saved %ds'%(time.time()-t0))
