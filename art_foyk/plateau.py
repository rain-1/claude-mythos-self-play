"""THE RHOMBUS PLATEAU - MO 137177.  2560^2.
Left: the flat valley - the one-parameter rhombus family, every member worth exactly B=8.
Right: the stiffened worlds n>=5 - optimal polygons with softest-mode ghosts, and the
stiffness ladder with 1/phi at n=5, triple degeneracies at n=8 (4sqrt2) and n=10 (10phi),
softest mode ~ n^3/(8 pi^2)."""
import numpy as np, sys
import artlib as A

PREVIEW = len(sys.argv)>1 and sys.argv[1]=='preview'
FINAL = 1024 if PREVIEW else 2560
SS = 1 if PREVIEW else 2
S = FINAL*SS
rs = S/5120.0

buf = A.canvas(S)
GOLD  = np.array([1.00, 0.80, 0.38])
CYAN  = np.array([0.45, 0.78, 1.00])
VIOLET= np.array([0.66, 0.50, 1.00])
ICE   = np.array([0.72, 0.88, 1.00])
EMBER = np.array([1.00, 0.47, 0.30])

def reg_verts(n, cx, cy, side):
    R = side/(2*np.sin(np.pi/n))
    th = np.linspace(0, 2*np.pi, n, endpoint=False) - np.pi/2 + np.pi/n
    return np.stack([cx + R*np.cos(th), cy + R*np.sin(th)], 1)

# ---------- left: the corridor of rhombi (flat valley) ----------------------
# rhombi with angle alpha from 90 deg down to 14 deg, drawn in a receding corridor
ncor = 26
x0c, y0c = 0.255*S, 0.180*S     # far end
x1c, y1c = 0.255*S, 0.870*S     # near end
side0, side1 = 0.055*S, 0.155*S
for i in range(ncor):
    t = i/(ncor-1)
    alpha = np.deg2rad(90 - 76*t)
    cx = x0c + (x1c-x0c)*t**1.15
    cy = y0c + (y1c-y0c)*t**1.15
    side = side0 + (side1-side0)*t**1.3
    d1 = side*np.cos(alpha/2); d2 = side*np.sin(alpha/2)   # half-diagonals
    Pv = np.array([[cx-d1, cy],[cx, cy-d2],[cx+d1, cy],[cx, cy+d2]])
    # every rhombus same brightness: the plateau
    col = GOLD*0.55 + ICE*0.45
    A.polyline(buf, Pv, col, amp=0.75*rs, closed=True)
    # diagonals faint
    A.polyline(buf, Pv[[0,2]], CYAN*0.6, amp=0.16*rs)
    A.polyline(buf, Pv[[1,3]], CYAN*0.6, amp=0.16*rs)
    for v in Pv: A.star(buf, v[0], v[1], col, amp=0.8, rad=1.8*rs*2)
# valley floor line
A.polyline(buf, np.array([[x0c, y0c+0.02*S],[x1c, y1c+0.055*S]]), GOLD*0.5, amp=0.22*rs)

# ---------- right upper: stiffened worlds -----------------------------------
# n=5..8 optimal (regular) polygons, softest-mode ghost displacement
import numpy.linalg as la
def hess_modes(n):
    # projected Hessian at regular n-gon (finite differences), returns eigvals, eigvecs in tangent basis, and vertex displacement fields
    def BC(theta):
        phi = np.cumsum(theta) - theta[0]
        e = np.stack([np.cos(phi), np.sin(phi)], 1)
        P = np.vstack([[0,0], np.cumsum(e,0)])[:-1]
        c = P.mean(0)
        Bv = n*((P-c)**2).sum()
        cons = np.array([theta.sum()-2*np.pi, e[:,0].sum(), e[:,1].sum()])
        return Bv, cons, P
    x = np.full(n, 2*np.pi/n)
    h = 1e-5
    def ng(f):
        g = np.zeros(n)
        for i in range(n):
            xp=x.copy(); xp[i]+=h; xm=x.copy(); xm[i]-=h
            g[i] = (f(xp)-f(xm))/(2*h)
        return g
    fB = lambda t: BC(t)[0]
    fC = [lambda t,i=i: BC(t)[1][i] for i in range(3)]
    gB = ng(fB); J = np.stack([ng(c) for c in fC])
    lam, *_ = la.lstsq(J.T, gB, rcond=None)
    fL = lambda t: fB(t) - lam @ BC(t)[1]
    H = np.zeros((n,n)); h2=1e-4
    for i in range(n):
        for j in range(i,n):
            xpp=x.copy(); xpp[i]+=h2; xpp[j]+=h2
            xpm=x.copy(); xpm[i]+=h2; xpm[j]-=h2
            xmp=x.copy(); xmp[i]-=h2; xmp[j]+=h2
            xmm=x.copy(); xmm[i]-=h2; xmm[j]-=h2
            H[i,j]=H[j,i]=(fL(xpp)-fL(xpm)-fL(xmp)+fL(xmm))/(4*h2*h2)
    _,_,Vt = la.svd(J); T = Vt[3:].T
    Hp = T.T @ H @ T
    ev, evec = la.eigh(-Hp)
    return ev, (T @ evec), x, BC

worlds = [5, 6, 7, 8]
wx = [0.545, 0.780, 0.545, 0.780]
wy = [0.195, 0.195, 0.430, 0.430]
for wi, n in enumerate(worlds):
    cx, cy = wx[wi]*S, wy[wi]*S
    side = 0.112*S/ (n/5.2)
    ev, modes, x0, BC = hess_modes(n)
    Pv = reg_verts(n, cx, cy, side)
    A.polyline(buf, Pv, GOLD, amp=1.15*rs, closed=True)
    for v in Pv: A.star(buf, v[0], v[1], GOLD, amp=1.5, rad=2.2*rs*2)
    # softest mode ghosts: theta perturbation along softest eigenvector
    mode = modes[:,0]
    for eps, aa in [(-0.34,0.30),(-0.17,0.5),(0.17,0.5),(0.34,0.30)]:
        th = x0 + eps*mode/np.max(np.abs(mode))*0.5
        th = th*2*np.pi/th.sum()
        _,_,P = BC(th)
        P = P - P.mean(0)
        # scale to same side length ~ side: edges of P are unit
        P = P*side
        # rotate to align first edge orientation with regular's
        A.polyline(buf, P + np.array([cx,cy]), ICE, amp=0.28*rs*aa*2.2, closed=True)

# ---------- bottom right: stiffness ladder ---------------------------------
lx0, lx1 = 0.475*S, 0.955*S
ly0, ly1 = 0.615*S, 0.905*S
ns = list(range(4, 25))
data = {}
for n in ns:
    ev, _, _, _ = hess_modes(n)
    data[n] = ev
lam_max = max(v[-1] for v in data.values())
def lgy(v):  # log scale, with a pit for zero
    if v < 1e-9: return ly1 + 0.030*S
    return ly1 - (np.log10(v) - np.log10(0.4))/(np.log10(lam_max)-np.log10(0.4))*(ly1-ly0)
def lgx(n): return lx0 + (n-4)/(24-4)*(lx1-lx0)
# asymptote thread n^3/(8pi^2)
th_ns = np.linspace(4.6, 24, 120)
th_pts = np.stack([ [lgx(n), lgy(n**3/(8*np.pi**2))] for n in th_ns ])
A.polyline(buf, th_pts, EMBER*0.85, amp=0.30*rs)
for n in ns:
    for v in data[n]:
        y = lgy(v)
        col = ICE
        A.polyline(buf, np.array([[lgx(n)-5*rs*2, y],[lgx(n)+5*rs*2, y]]), col, amp=0.5*rs)
# specials
A.star(buf, lgx(4), lgy(0), GOLD, amp=3.2, rad=4.0*rs*2)         # the zero mode
A.star(buf, lgx(5), lgy(0.6180339887), GOLD, amp=2.6, rad=3.4*rs*2)  # 1/phi
A.star(buf, lgx(8), lgy(4*np.sqrt(2)), VIOLET, amp=2.6, rad=3.4*rs*2)
A.star(buf, lgx(10), lgy(10*1.6180339887), VIOLET, amp=2.6, rad=3.4*rs*2)
A.polyline(buf, np.array([[lx0, ly1],[lx1, ly1]]), CYAN*0.5, amp=0.2*rs)

img = A.bloom(buf, sigmas=(2.0*rs*2, 8*rs*2, 26*rs*2), weights=(1.0, 0.38, 0.20))
img = A.tonemap(img, k=1.5, gamma=0.88)

tx = []
W = S
def T(x,y,s,size,col=(0.88,0.84,0.76),bold=False,anchor='la'): tx.append((x*W,y*W,s,int(size*rs*2),col,bold,anchor))
T(0.045, 0.028, "THE RHOMBUS PLATEAU", 40, (1.0,0.87,0.55), True)
T(0.045, 0.056, "unit-sided polygons maximizing the sum of squared distances  (MO 137177)", 18, (0.75,0.72,0.66))
T(0.255, 0.108, "n = 4: the flat valley", 20, (0.9,0.86,0.75), anchor='ma')
T(0.255, 0.128, "every rhombus scores exactly B = 8  (Euler: |AC|^2+|BD|^2 = 4 - 4|MN|^2)", 14, (0.65,0.63,0.58), anchor='ma')
T(0.255, 0.915, "the optimizer wanders the corridor and loses nothing", 14, (0.65,0.63,0.58), anchor='ma')
T(0.655, 0.095, "n >= 5: the valley closes", 20, (0.9,0.86,0.75), anchor='ma')
T(0.655, 0.115, "regular wins alone; ghosts = softest escape, now uphill", 14, (0.65,0.63,0.58), anchor='ma')
for wi, n in enumerate(worlds):
    T(wx[wi], wy[wi]+0.078, f"n={n}", 15, (0.8,0.76,0.66), anchor='ma')
T(0.715, 0.585, "the stiffness ladder: eigenvalues of the shape Hessian at the optimum", 15, (0.85,0.80,0.68), anchor='ma')
T(lgx(4)/W+0.010, (lgy(0)-14*rs*2)/W, "n=4: a rung at zero", 13, (1.0,0.87,0.55))
T(lgx(5)/W+0.011, lgy(0.6180339887)/W-0.008, "1/phi", 14, (1.0,0.87,0.55))
T(lgx(8)/W+0.011, lgy(4*np.sqrt(2))/W-0.008, "4sqrt2 (x3)", 13, (0.78,0.65,1.0))
T(lgx(10)/W+0.011, lgy(16.180339887)/W-0.008, "10phi (x3)", 13, (0.78,0.65,1.0))
T(lgx(21)/W, lgy(21**3/(8*np.pi**2))/W+0.014, "n^3 / 8pi^2", 14, (1.0,0.60,0.42), anchor='ma')
for nt in (5,10,15,20):
    T(lgx(nt)/W, 0.912, str(nt), 12, (0.55,0.53,0.50), anchor='ma')
T(0.045, 0.955, "B_reg(n) = n^2 / 4 sin^2(pi/n);  n=4 alone keeps a zero mode - the one flat direction in the whole family", 14, (0.60,0.58,0.54))
T(0.715, 0.940, "multistart search n<=16: regular optimal every time; spectrum verified to n=50", 13, (0.62,0.60,0.56), anchor='ma')
img = A.bake_text(img, tx, S)
A.save(img, 'plateau_preview.png' if PREVIEW else 'plateau_2560.png', final=FINAL)
print("saved")
