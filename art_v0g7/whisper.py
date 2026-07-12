# The Whispering Gallery — one exact eigenmode of the disk, u = J_m(k r) cos(m th),
# k = j_{m,n}/R_disk (Dirichlet zero: u = 0 on the rim), at semiclassical m.
# The turning-point circle r_c = m/k is a real caustic: outside it the mode
# rings (2m petals, n radial shells), inside it the wave cannot go — the
# evanescent void. Overlaid: the CLASSICAL ray star — chords reflecting
# specularly off the rim, all tangent to the same circle r_c (Keller–Rubinow
# correspondence). The rays' envelope and the wave's caustic agree.
# Verifications (whisper_stats.txt):
#   - k r_c = m exactly by construction; observed intensity peak sits at
#     r_c + 0.809/ (k^2 r_c)^{1/3} * (first Airy max), checked numerically
#   - residual of the Helmholtz equation on a test annulus (finite check)
#   - ray chords tangent to r_c to machine precision; rotation number vs m/j
#   - front-page inequality J_m^2 <= J_{m-1/2}^2 + J_{m+1/2}^2 spot-tested
#     along the mode's own radius line
import numpy as np, sys, time
from scipy.special import jv, jn_zeros, ai_zeros
from scipy.ndimage import gaussian_filter
from PIL import Image

PROTO = '--proto' in sys.argv
R  = 1280 if PROTO else 2560
SS = 2
G  = R*SS
M   = 120         # angular order (2M petals)
# choose n so the classical rotation number ~ 2/7: alpha = arccos(m/j) ~ 2pi/7
t0=time.time()
target = np.cos(2*np.pi/7)
zs = jn_zeros(M, 45)
NR = int(np.argmin(np.abs(M/zs - target)))+1
k  = zs[NR-1]
Rdisk = 0.455                   # in frame units (frame = [0,1]^2)
rc = M/k                        # caustic radius (units of R_disk)
print('m=%d n=%d  j_{m,n}=%.6f  r_c/R=%.4f (target %.4f)'%(M,NR,k,rc,target))

yy,xx = np.mgrid[0:G,0:G].astype(np.float64)
cx=cy=(G-1)/2
r  = np.hypot(xx-cx,yy-cy)/ (Rdisk*G)
th = np.arctan2(yy-cy,xx-cx)
inside = r<=1.0
u = np.zeros_like(r)
u[inside] = jv(M, k*r[inside])*np.cos(M*th[inside])
I = u*u
print('mode field %ds'%(time.time()-t0))

# ---------- verifications ----------
rr = np.linspace(1e-4, 1.0, 20000)
prof = jv(M, k*rr)**2
r_peak = rr[np.argmax(prof)]
a1 = ai_zeros(1)[1][0]          # first max of Ai at t = -1.0188
r_airy = rc*(1 + (-a1)*(2)**(-1/3)*M**(-2/3))   # first antinode prediction
# Helmholtz residual on a moderate polar grid (5-pt FD in r,th)
rg=np.linspace(0.3,0.98,400); tg=np.linspace(0,2*np.pi,1200,endpoint=False)
RG,TG=np.meshgrid(rg,tg,indexing='ij')
U=jv(M,k*RG)*np.cos(M*TG)
dr=rg[1]-rg[0]; dt=tg[1]-tg[0]
Urr=(np.roll(U,-1,0)-2*U+np.roll(U,1,0))/dr**2
Ur =(np.roll(U,-1,0)-np.roll(U,1,0))/(2*dr)
Utt=(np.roll(U,-1,1)-2*U+np.roll(U,1,1))/dt**2
lap=Urr+Ur/RG+Utt/RG**2
res=np.abs(lap[2:-2]+k*k*U[2:-2]).max()/ (k*k*np.abs(U).max())
# ray star: specular chords, tangent to rc
alpha = np.arccos(rc)           # half-chord angle at the rim
NCH = 480
ths = 2*np.pi*np.arange(NCH)/NCH + 0.5*np.pi/M
tangency_err=0.0
for i in range(0,NCH,37):
    p=np.array([np.cos(ths[i]),np.sin(ths[i])]); q=np.array([np.cos(ths[i]+2*alpha),np.sin(ths[i]+2*alpha)])
    d=np.abs(np.cross(q-p, -p))/np.linalg.norm(q-p)
    tangency_err=max(tangency_err,abs(d-rc))
ineq = (jv(M-0.5,k*rr)**2+jv(M+0.5,k*rr)**2-jv(M,k*rr)**2)
with open('whisper_stats.txt','w') as f:
    f.write('mode (m,n)=(%d,%d), j_mn=%.9f, caustic r_c/R=%.6f\n'%(M,NR,k,rc))
    f.write('first antinode: observed r=%.5f, Airy prediction r=%.5f (rel err %.2e)\n'%(r_peak,r_airy,abs(r_peak-r_airy)/r_airy))
    f.write('Helmholtz residual (rel, FD polar 400x1200): %.2e\n'%res)
    f.write('ray chords tangent to r_c: max |dist - r_c| = %.2e\n'%tangency_err)
    f.write('rotation number 2*alpha/2pi = %.6f  vs 2/7 = %.6f (detuning %.2e -> star precesses %.3f deg/return)\n'%(alpha/np.pi, 2/7, alpha/np.pi-2/7, np.degrees(7*(2*alpha-4*np.pi/7))))
    f.write('front-page inequality along mode radius: min D = %.3g (>=0: %s)\n'%(ineq.min(), bool(ineq.min()>=-1e-15)))
print('verifications done: peak %.5f vs %.5f, res %.1e, tang %.1e'%(r_peak,r_airy,res,tangency_err))

# ---------- render ----------
# brightness: I, per-shell flattening ~ (r^2... keep honest: just tone-map I)
In = I/np.percentile(I[I>0],99.5)
L  = 0.72*np.clip(In,0,3.2)**0.62

# palette: inner void violet-black; petals ice-blue; caustic shell gold
w_in  = np.clip((rc - r)/ (2.2*rc*M**(-2/3)), 0, 1)          # inside-caustic depth
w_c   = np.exp(-((r-rc)/(1.4*rc*M**(-2/3)))**2)              # caustic shell weight
c_pos = np.array([0.55,0.80,1.00])
c_neg = np.array([0.52,0.88,0.86])
c_gold= np.array([1.00,0.84,0.45])
c_ev  = np.array([0.40,0.24,0.60])
sgn = (u>0).astype(np.float64)[...,None]
c_pet = c_pos[None,None,:]*sgn + c_neg[None,None,:]*(1-sgn)
col = c_pet*(1-w_c[...,None]) + c_gold[None,None,:]*w_c[...,None]
img = L[...,None]*col
# evanescent violet breath just inside the caustic
ev = np.exp(-np.clip((rc-r)/(2.1*rc*M**(-2/3)),0,40))*(r<rc)*0.21
img += ev[...,None]*c_ev
# rim: cool thin ring at r=1
rim = np.exp(-((r-1.0)*Rdisk*G/(1.6*SS))**2)*0.35
img += rim[...,None]*np.array([0.45,0.62,0.85])

# ---------- ray star (classical chords) ----------
ray = np.zeros((G,G),np.float32)
def draw_seg(g,x0,y0,x1,y1,w):
    dx,dy=x1-x0,y1-y0
    n=int(max(abs(dx),abs(dy)))+1
    t=(np.arange(n)+0.5)/n
    xs=x0+t*dx; ys=y0+t*dy
    ix=np.floor(xs).astype(np.int64); iy=np.floor(ys).astype(np.int64)
    ok=(ix>=0)&(iy>=0)&(ix<G-1)&(iy<G-1)
    ix,iy,fx,fy=ix[ok],iy[ok],(xs-np.floor(xs))[ok],(ys-np.floor(ys))[ok]
    ws=w/n
    np.add.at(g,(iy,ix),ws*(1-fx)*(1-fy)); np.add.at(g,(iy,ix+1),ws*fx*(1-fy))
    np.add.at(g,(iy+1,ix),ws*(1-fx)*fy);   np.add.at(g,(iy+1,ix+1),ws*fx*fy)
# one long billiard trajectory: theta_{i+1} = theta_i + 2 alpha (irrational rotation)
th0 = 0.5*np.pi/M
NRAY = 57                       # 8 heptagram returns; precession ~1.8 deg/return
pts=[th0 + 2*alpha*i for i in range(NRAY)]
for i in range(NRAY-1):
    x0=(cx + np.cos(pts[i])*Rdisk*G); y0=(cy + np.sin(pts[i])*Rdisk*G)
    x1=(cx + np.cos(pts[i+1])*Rdisk*G); y1=(cy + np.sin(pts[i+1])*Rdisk*G)
    age=(i+1)/(NRAY-1)              # ghost -> blaze
    draw_seg(ray,x0,y0,x1,y1, 40.0*(0.25+0.75*age**2.2))
rayb = gaussian_filter(ray,0.7*SS)*1.3 + gaussian_filter(ray,3.0*SS)*0.5
rayb/=np.percentile(rayb[rayb>0],99.5)
img += np.clip(rayb,0,2.5)[...,None]*np.array([1.00,0.74,0.34])*1.05

img = img.reshape(R,SS,R,SS,3).mean(axis=(1,3))
out = 1-np.exp(-1.55*img)
out = np.clip(out,0,1)**(1/2.1)
Image.fromarray((out*255).astype(np.uint8)).save('whisper_proto.png' if PROTO else 'whispering_gallery.png')
print('saved %ds'%(time.time()-t0))
