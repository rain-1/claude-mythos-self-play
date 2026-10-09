"""Candy springs: helices as glossy tubes.  White stripes = parallel-transported (Bishop) frame,
coral stripe = Frenet frame (outer side, -N).  Per coil the stripes slip by 2*pi*sin(alpha) = 2*pi - solid angle."""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from paint import SORBET, caption
OUT = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
SS = int(sys.argv[2]) if len(sys.argv) > 2 else 2
name = sys.argv[3] if len(sys.argv) > 3 else f'springs_{OUT}.png'
WO, HO = OUT, int(OUT*0.9)
W, H = WO*SS, HO*SS
# camera
eye = np.array([0.0, -34.0, 10.0]); look = np.array([0.0, 0.0, 5.0]); fov = 0.60
fw = look - eye; fw /= np.linalg.norm(fw)
rt = np.cross(fw, [0, 0, 1.0]); rt /= np.linalg.norm(rt); up = np.cross(rt, fw)
foc = (W/2)/np.tan(fov/2)
def project(P):
    q = P - eye
    z = q @ fw
    return W/2 + foc*(q @ rt)/z, H/2 - foc*(q @ up)/z, z
Ld = np.array([-0.45, -0.35, 0.82]); Ld /= np.linalg.norm(Ld)       # light toward
a, Lw, rt_tube = 0.62, 13.0, 0.16
ALPH = [5, 13, 24, 37, 52, 70]                                          # pitch angle (deg) of each spring
HUE = ['lilac', 'periwinkle', 'sky', 'mint', 'butter', 'peach']
xs = np.linspace(-6.6, 6.6, len(ALPH))
def spring(al, x0):
    alr = np.radians(al)
    c = a*np.tan(alr)                       # z per radian
    n = 9000
    t = np.linspace(0, Lw/np.hypot(a, c), n)
    C = np.stack([x0 + a*np.cos(t), a*np.sin(t), 0.35 + c*t], -1)
    T = np.stack([-a*np.sin(t), a*np.cos(t), c*np.ones_like(t)], -1)/np.hypot(a, c)
    N = np.stack([-np.cos(t), -np.sin(t), 0*t], -1)
    B = np.cross(T, N)
    tau = c/(a*a + c*c); s = t*np.hypot(a, c)
    # Bishop frame: rotate (N,B) by -tau*s  (U' = 0 along T)
    th = -tau*s
    U = np.cos(th)[:, None]*N - np.sin(th)[:, None]*B
    V = np.sin(th)[:, None]*N + np.cos(th)[:, None]*B
    return C, U, V, -th   # frenet angle of N in (U,V) frame = tau*s
def spring_points(al, x0, hn, scale):
    """yield (P, colour, normal) chunks for one spring; density adapts to the projected size."""
    C, U, V, psiN = spring(al, x0)
    base = SORBET[hn]
    u0, v0, _ = project(C)
    plen = np.sum(np.hypot(np.diff(u0), np.diff(v0)))
    pr = foc*rt_tube/np.linalg.norm(C.mean(0) - eye)
    na, m = int(plen*2.2*scale) + 10, int(2*np.pi*pr*2.6*scale) + 16
    ti = np.linspace(0, len(C) - 1, na)
    def lerpa(A): return np.stack([np.interp(ti, np.arange(len(C)), A[:, i]) for i in range(A.shape[1])], -1)
    C2, U2, V2 = lerpa(C), lerpa(U), lerpa(V); ps2 = np.interp(ti, np.arange(len(C)), psiN)
    th = np.linspace(0, 2*np.pi, m, endpoint=False)
    step = max(1, int(1.0e7/m))
    for i0 in range(0, na, step):
        sl = slice(i0, i0 + step)
        nn = np.cos(th)[None, :, None]*U2[sl, None, :] + np.sin(th)[None, :, None]*V2[sl, None, :]
        P = C2[sl, None, :] + rt_tube*nn
        wstr = np.broadcast_to(np.abs(((th[None, :]*5/(2*np.pi)) % 1.0) - 0.5) < 0.13, P.shape[:2])
        fr = np.angle(np.exp(1j*(th[None, :] - (ps2[sl, None] + np.pi))))
        cstr = np.abs(fr) < 0.17
        col = np.broadcast_to(base, P.shape).astype(np.float32).copy()
        col[wstr] = [1.0, 0.995, 0.985]
        col[cstr] = SORBET['coral']*0.92
        yield P.reshape(-1, 3), col.reshape(-1, 3), nn.reshape(-1, 3)
    for e in (C[0], C[-1]):
        ph = np.random.default_rng(0).normal(size=(int(4e5*scale*scale), 3)); ph /= np.linalg.norm(ph, axis=1, keepdims=True)
        yield e + ph*rt_tube*1.45, np.broadcast_to(SORBET['butter'], ph.shape), ph
scale = W/2400
# --- ground: paper with coloured shadow pools
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dirs = (xx[..., None] - W/2)/foc*rt.astype(np.float32) + (H/2 - yy[..., None])/foc*up.astype(np.float32) + fw.astype(np.float32)
del xx, yy
tg = -eye[2]/dirs[..., 2]
Gx = eye[0] + tg*dirs[..., 0]; Gy = eye[1] + tg*dirs[..., 1]
del dirs
sh_res = 0.01; gx0, gy0 = -10.0, -6.0
ii = ((Gx - gx0)/sh_res).astype(np.int32); jj = ((Gy - gy0)/sh_res).astype(np.int32)
del Gx, Gy
paper = np.array([0.993, 0.988, 0.98], np.float32)
img = np.ones((H, W, 3), np.float32)*paper
zbuf = np.full((H, W), np.inf, np.float32)
lav = np.array([0.78, 0.80, 0.93])
for al, x0, hn in zip(ALPH, xs, HUE):
    SM = np.zeros((int(16/sh_res), int(22/sh_res)), np.float32)
    for P, Cc, Nn in spring_points(al, x0, hn, scale):
        Pg = P - (P[:, 2:3]/Ld[2])*Ld
        gi = ((Pg[:, 0] - gx0)/sh_res).astype(int); gj = ((Pg[:, 1] - gy0)/sh_res).astype(int)
        ok = (gi >= 0) & (gi < SM.shape[1]) & (gj >= 0) & (gj < SM.shape[0])
        SM[gj[ok], gi[ok]] = 1
    SM = gaussian_filter(SM, 4.0); SM = np.clip(SM*2.2, 0, 1); SM = gaussian_filter(SM, 3.0)
    okg = (tg > 0) & (ii >= 0) & (ii < SM.shape[1]) & (jj >= 0) & (jj < SM.shape[0])
    sh = np.zeros((H, W), np.float32); sh[okg] = SM[jj[okg], ii[okg]]
    tint = (0.55*lav + 0.45*SORBET[hn]).astype(np.float32)
    img *= (1 - 0.72*sh[..., None]*(1 - tint))
    del sh, SM, okg
for al, x0, hn in zip(ALPH, xs, HUE):
    for P, Cc, Nn in spring_points(al, x0, hn, scale):
        view = P - eye; view /= np.linalg.norm(view, axis=1, keepdims=True)
        facing = -(Nn*view).sum(1) > -0.05
        P, Cc, Nn, view = P[facing], Cc[facing], Nn[facing], view[facing]
        dif = np.clip(Nn @ Ld, 0, 1)
        hv = Ld - view; hv /= np.linalg.norm(hv, axis=1, keepdims=True)
        spec = np.clip((Nn*hv).sum(1), 0, 1)**60
        fres = (1 - np.clip(-(Nn*view).sum(1), 0, 1))**3
        shade = 0.58 + 0.30*dif + 0.12*(0.5 + 0.5*Nn[:, 2])
        col = np.clip(Cc*shade[:, None] + 0.75*spec[:, None] + 0.22*fres[:, None]*np.array([0.9, 0.93, 1.0]), 0, 1).astype(np.float32)
        u_, v_, z_ = project(P)
        iu = np.round(u_).astype(np.int32); iv = np.round(v_).astype(np.int32)
        ok = (iu >= 0) & (iu < W) & (iv >= 0) & (iv < H)
        iu, iv, z_, col = iu[ok], iv[ok], z_[ok].astype(np.float32), col[ok]
        order = np.argsort(-z_)
        lin = iv[order]*W + iu[order]
        tz = {}
        # nearest per pixel within the chunk: last write wins after the far->near sort
        uniq_lin = lin
        tmpz = np.full(H*W, np.inf, np.float32); tmpz[uniq_lin] = z_[order]
        tmpc = np.zeros((H*W, 3), np.float32); tmpc[uniq_lin] = col[order]
        sel = np.unique(uniq_lin)
        better = tmpz[sel] < zbuf.ravel()[sel]
        sel = sel[better]
        zbuf.ravel()[sel] = tmpz[sel]
        img.reshape(-1, 3)[sel] = tmpc[sel]
        del tmpz, tmpc
im = Image.fromarray((np.clip(img, 0, 1)*255).astype(np.uint8))
if SS > 1: im = im.resize((WO, HO), Image.LANCZOS)
u = WO/1200
for al, x0 in zip(ALPH, xs):
    px, py, _ = project(np.array([x0, 0, 0]))
    caption(im, px/SS, py/SS + 34*u, [(f'\u03b1 = {al}\u00b0', 'i', 17), (f'slips {np.sin(np.radians(al)):.2f} turn per coil', 'i', 13)], scale=u, align='center')
caption(im, 60*u, HO - 150*u, [('The Stripe That Remembers the Turning', 'b', 30),
  ('one candy wire, six stretches.  White stripes are carried without twisting (parallel transport); the coral stripe keeps facing out (the Frenet frame).', 'i', 14.5),
  ('Per coil the two slip by 2\u03c0 sin \u03b1 = 2\u03c0 \u2212 the solid angle the tangent sweeps: torsion \u03c4 = sin \u03b1 cos \u03b1 / a, largest at 45\u00b0.', 'i', 14.5)], scale=u)
im.save(name); print('saved', name)
