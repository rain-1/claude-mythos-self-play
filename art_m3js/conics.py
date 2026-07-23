"""SIX MOMENTS OF PERFECT ATTENTION (x2) -- osculating conics of a convex oval.
At each point, the unique conic with 5th-order contact.  Where the oval bends
boldly the conic is an ELLIPSE (attention that returns, closed rings); at the
flat arcs affine curvature crosses zero and the conic ESCAPES through a
parabola into hyperbolae (whiskers that never come back).  At the 12
sextactic points (Mukhopadhyaya >= 6) contact deepens to 6th order: gold.
Everything from one SVD null-space per point; sextactic = det of the 6x6."""
import sys, numpy as np
from conics_engine import make_curve, osculating_conics, t, K
from kit import splat, draw_polyline, wide_bloom, tonemap, save, ramp, typ

PROTO  = "final" not in sys.argv
S      = 1600 if PROTO else 5120
FINAL  = 800 if PROTO else 2560
rs     = S / 1600.0

CURVE = {2: (0.09, 0.7), 3: (0.055, 0.0), 5: (0.012, 1.9)}
dx, dy = make_curve(CURVE)
xp, yp, xpp, ypp = dx[1], dy[1], dx[2], dy[2]
assert ((xp*ypp - yp*xpp)/(xp**2+yp**2)**1.5).min() > 0, "not convex"

NC   = 1400 if PROTO else 1400
idx  = (np.arange(NC) * (K // NC)).astype(int)
Q, _, _ = osculating_conics(dx, dy, idx)
Qf, sex_full, _ = osculating_conics(dx, dy, np.arange(K))
sgn = np.sign(sex_full)
flip = np.nonzero(sgn != np.roll(sgn, 1))[0]
print("sextactic count:", len(flip))
X0, Y0 = dx[0][idx], dy[0][idx]

a,b,c,d,e,f = (Q[:,i] for i in range(6))
disc = b*b - 4*a*c
det2 = 4*a*c - b*b
ucen = (-2*c*d + b*e) / np.where(np.abs(det2)<1e-14, np.nan, det2)
vcen = (-2*a*e + b*d) / np.where(np.abs(det2)<1e-14, np.nan, det2)
# value at center, axes
fc = a*ucen**2 + b*ucen*vcen + c*vcen**2 + d*ucen + e*vcen + f
tr = a + c; rt = np.sqrt(((a-c)/2)**2 + (b/2)**2)
l1, l2 = tr/2 + rt, tr/2 - rt                     # eigenvalues of [[a,b/2],[b/2,c]]
r1 = np.sqrt(np.abs(-fc/np.where(np.abs(l1)<1e-14, np.nan, l1)))
r2 = np.sqrt(np.abs(-fc/np.where(np.abs(l2)<1e-14, np.nan, l2)))
is_ell = (disc < 0) & np.isfinite(r1) & np.isfinite(r2) & (np.maximum(r1,r2) < 3.0)
print("rings:", is_ell.sum(), "whiskers:", (~is_ell).sum())

# near-parabolic silver measure: normalized |disc|
pnorm = np.abs(disc) / (a*a + b*b + c*c)
silver = np.exp(-(pnorm / np.nanquantile(pnorm, 0.06))**2)

sext_t = t[flip]
prox = np.abs(((t[idx][:,None] - sext_t[None,:]) + np.pi) % (2*np.pi) - np.pi).min(1)
hot  = np.exp(-(prox/0.10)**2)

cx = cy = S/2
SC = S * 0.225
def w2s(x, y): return cx + x*SC, cy - y*SC

rings = np.zeros((S, S, 3), np.float32)
whisk = np.zeros((S, S, 3), np.float32)
goldL = np.zeros((S, S, 3), np.float32)
silvL = np.zeros((S, S), np.float32)
oval  = np.zeros((S, S), np.float32)

def cyc(u):
    return ramp([(0.00,(0.13,0.44,0.62)),(0.25,(0.16,0.66,0.70)),
                 (0.50,(0.42,0.80,0.72)),(0.75,(0.12,0.52,0.74)),
                 (1.00,(0.13,0.44,0.62))], u)
colA = cyc((t[idx]/(2*np.pi)) % 1.0)
GOLD = np.array([1.0, 0.74, 0.30])

# ---- closed rings (ellipses), exact parametric --------------------------
ei = np.nonzero(is_ell)[0]
NP_E = 420 if PROTO else 760
th = np.linspace(0, 2*np.pi, NP_E)[None, :]
ang = 0.5*np.arctan2(b[ei], (a-c)[ei])
ca, sa = np.cos(ang)[:,None], np.sin(ang)[:,None]
# principal radii along rotated axes (l1 axis at angle ang)
R1 = r1[ei][:,None]; R2 = r2[ei][:,None]
pu = R1*np.cos(th)*ca - R2*np.sin(th)*sa + ucen[ei][:,None]
pv = R1*np.cos(th)*sa + R2*np.sin(th)*ca + vcen[ei][:,None]
Xw, Yw = w2s(X0[ei][:,None] + pu, Y0[ei][:,None] + pv)
# param angle of contact point on each ellipse (for gold arc-gating)
u0 = -ucen[ei]; v0 = -vcen[ei]                     # contact rel. center
pu0 =  u0*ca[:,0] + v0*sa[:,0]; pv0 = -u0*sa[:,0] + v0*ca[:,0]
th0 = np.arctan2(pv0/np.maximum(R2[:,0],1e-12), pu0/np.maximum(R1[:,0],1e-12))
dth = np.abs(((th - th0[:,None]) + np.pi) % (2*np.pi) - np.pi)
arcgate = np.exp(-(dth/0.75)**2)
radW = np.exp(-((( (X0[ei][:,None]+pu)**2 + (Y0[ei][:,None]+pv)**2 ) / 2.4**2)**2))
MASS_E = 26.0 * rs * rs
wgt = np.full((len(ei), 1), MASS_E/NP_E) * (1 - hot[ei][:,None]) * (0.35 + 0.65*radW)
for ch in range(3):
    tmp = np.zeros((S, S), np.float32)
    splat(tmp, Xw.ravel(), Yw.ravel(), (wgt*colA[ei][:,ch:ch+1]*np.ones_like(pu)).ravel())
    rings[..., ch] += tmp
# silver near-parabolic + gold sextactic ellipse overlays
wgt_s = np.full((len(ei),1), MASS_E/NP_E) * silver[ei][:,None]
tmp = np.zeros((S, S), np.float32)
splat(tmp, Xw.ravel(), Yw.ravel(), (wgt_s*np.ones_like(pu)).ravel())
silvL += tmp
wgt_g = np.full((len(ei),1), MASS_E/NP_E) * hot[ei][:,None] * 5.5 * arcgate
for ch in range(3):
    tmp = np.zeros((S, S), np.float32)
    splat(tmp, Xw.ravel(), Yw.ravel(), (wgt_g*GOLD[ch]*np.ones_like(pu)).ravel())
    goldL[..., ch] += tmp

# ---- whiskers (hyperbolae & giants), marched ----------------------------
def march(Qs, x0s, y0s, nstep, ds):
    n = len(Qs)
    aa,bb,cc,dd,ee,ff = (Qs[:,i] for i in range(6))
    out = []
    for direction in (+1.0, -1.0):
        u = np.zeros(n); v = np.zeros(n)
        pts = np.empty((nstep, 2, n))
        for s in range(nstep):
            gu = 2*aa*u + bb*v + dd; gv = bb*u + 2*cc*v + ee
            nn = np.hypot(gu, gv) + 1e-30
            um, vm = u + 0.5*ds*direction*gv/nn, v - 0.5*ds*direction*gu/nn
            gu = 2*aa*um + bb*vm + dd; gv = bb*um + 2*cc*vm + ee
            nn = np.hypot(gu, gv) + 1e-30
            u = u + ds*direction*gv/nn; v = v - ds*direction*gu/nn
            val = aa*u*u + bb*u*v + cc*v*v + dd*u + ee*v + ff
            gu = 2*aa*u + bb*v + dd; gv = bb*u + 2*cc*v + ee
            g2 = gu*gu + gv*gv + 1e-30
            u -= val*gu/g2; v -= val*gv/g2
            pts[s,0] = u; pts[s,1] = v
        out.append(pts)
    return out

hi = np.nonzero(~is_ell)[0]
NST = 320 if PROTO else 700
DS  = 2.0 / NST
whL, whR = march(Q[hi], X0[hi], Y0[hi], NST, DS)
fade = np.exp(-np.linspace(0, 1, NST)*1.3)[None, :]
MASS_W = 20.0 * rs * rs
for W in (whL, whR):
    U = W[:,0,:].T; V = W[:,1,:].T
    rad2 = (X0[hi][:,None]+U)**2 + (Y0[hi][:,None]+V)**2
    Xw, Yw = w2s(X0[hi][:,None]+U, Y0[hi][:,None]+V)
    base = (MASS_W/NST) * fade * np.exp(-(rad2/1.9**2)**2)
    for ch in range(3):
        tmp = np.zeros((S, S), np.float32)
        splat(tmp, Xw.ravel(), Yw.ravel(),
              (base*(1-hot[hi][:,None])*0.8*colA[hi][:,ch:ch+1]).ravel())
        whisk[..., ch] += tmp
    tmp = np.zeros((S, S), np.float32)
    splat(tmp, Xw.ravel(), Yw.ravel(), (base*silver[hi][:,None]).ravel())
    silvL += tmp
    for ch in range(3):
        tmp = np.zeros((S, S), np.float32)
        splat(tmp, Xw.ravel(), Yw.ravel(), (base*hot[hi][:,None]*2.5*GOLD[ch]).ravel())
        goldL[..., ch] += tmp

# ---- the twelve sextactic conics, crisp gold ----------------------------
Qs12, _, _ = osculating_conics(dx, dy, flip)
Xs12, Ys12 = dx[0][flip], dy[0][flip]
a12,b12,c12,d12,e12,f12 = (Qs12[:,i] for i in range(6))
disc12 = b12*b12 - 4*a12*c12
det12 = 4*a12*c12 - b12*b12
uc12 = (-2*c12*d12 + b12*e12)/np.where(np.abs(det12)<1e-14,np.nan,det12)
vc12 = (-2*a12*e12 + b12*d12)/np.where(np.abs(det12)<1e-14,np.nan,det12)
fc12 = a12*uc12**2 + b12*uc12*vc12 + c12*vc12**2 + d12*uc12 + e12*vc12 + f12
tr12 = a12 + c12; rt12 = np.sqrt(((a12-c12)/2)**2 + (b12/2)**2)
l1_, l2_ = tr12/2 + rt12, tr12/2 - rt12
r1_ = np.sqrt(np.abs(-fc12/l1_)); r2_ = np.sqrt(np.abs(-fc12/l2_))
gold12 = np.zeros((S, S), np.float32)
for i in range(len(flip)):
    if disc12[i] < 0 and np.isfinite(r1_[i]) and np.isfinite(r2_[i]) and max(r1_[i],r2_[i]) < 2.6:
        thq = np.linspace(0, 2*np.pi, 2000)
        angq = 0.5*np.arctan2(b12[i], a12[i]-c12[i])
        caq, saq = np.cos(angq), np.sin(angq)
        puq = r1_[i]*np.cos(thq)*caq - r2_[i]*np.sin(thq)*saq + uc12[i]
        pvq = r1_[i]*np.cos(thq)*saq + r2_[i]*np.sin(thq)*caq + vc12[i]
        Xq, Yq = w2s(Xs12[i] + puq, Ys12[i] + pvq)
        draw_polyline(gold12, Xq, Yq, 5200*rs*rs)
    else:
        WL, WR = march(Qs12[i:i+1], None, None, NST, DS*0.6)
        for W in (WL, WR):
            Uq = W[:,0,0]; Vq = W[:,1,0]
            dist2 = Uq**2 + Vq**2            # distance from the contact point
            keep = dist2 < 0.55**2
            if keep.sum() < 4: continue
            Xq, Yq = w2s(Xs12[i]+Uq[keep], Ys12[i]+Vq[keep])
            draw_polyline(gold12, Xq, Yq, 2600*rs*rs)
gold12 = gold12 + wide_bloom(gold12, 3.5*rs)*0.9

# oval + beads
Xc, Yc = w2s(dx[0], dy[0])
draw_polyline(oval, np.append(Xc, Xc[0]), np.append(Yc, Yc[0]), 26000*rs*rs)
bead = np.zeros((S, S), np.float32)
Xb, Yb = w2s(dx[0][flip], dy[0][flip])
splat(bead, Xb, Yb, 1.0)
bead = wide_bloom(bead, 3.0*rs) * 2600 * rs * rs

img = np.zeros((S, S, 3), np.float32)
r_t = typ(rings.sum(-1)); rings /= r_t
img += rings * 1.18
w_t = typ(whisk.sum(-1)); whisk /= max(w_t,1e-9)
img += whisk * 0.55
halo = np.stack([wide_bloom((rings+whisk)[...,ch], 5*rs) for ch in range(3)], -1)
img += halo * (0.55/max(typ(halo.sum(-1)),1e-9))
img += (silvL/max(typ(silvL),1e-9))[...,None]*np.array([0.82,0.90,0.95])*0.5
g_t = typ(goldL.sum(-1)); goldL /= max(g_t,1e-9)
img += goldL * 1.2
img += (gold12/typ(gold12))[...,None]*np.array([1.0,0.72,0.26])*1.15
img += (oval/typ(oval))[...,None]*np.array([0.58,0.78,0.76])*0.52
img += bead[...,None]*np.array([1.0,0.72,0.28])*1.05
out = tonemap(img, k=1.05, gamma=0.85)
save(out, "proto_conics.png" if PROTO else "conics_attention.png", FINAL)
