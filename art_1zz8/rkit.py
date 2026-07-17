"""Minimal additive render kit: bilinear splats, AA line splats, bloom, tonemap."""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom as ndzoom

def lines_scalar(W, cx, cy, half, z0, z1, mass_per_px, step=0.7, buf=None,
                 chunk_px=60_000_000):
    """Fast scalar-mass line splatter: nearest-pixel bincount accumulation.
    Returns/updates a (W,W) float32 buffer. For fog/mist layers."""
    if buf is None:
        buf = np.zeros((W, W), np.float32)
    z0 = np.asarray(z0, complex).ravel(); z1 = np.asarray(z1, complex).ravel()
    def to_px(z):
        x = (np.real(z)-cx)/half*0.5+0.5
        y = 0.5-(np.imag(z)-cy)/half*0.5
        return x*W, y*W
    X0, Y0 = to_px(z0); X1, Y1 = to_px(z1)
    L = np.hypot(X1-X0, Y1-Y0)
    nseg = np.maximum(2, (L/step).astype(np.int64))
    m = np.broadcast_to(np.asarray(mass_per_px, np.float32), X0.shape)
    # process in groups whose total sample count stays below chunk_px
    order = np.arange(len(z0))
    csum = np.cumsum(nseg)
    ngroups = max(1, int(csum[-1]//chunk_px)+1)
    bounds = np.searchsorted(csum, np.linspace(0, csum[-1], ngroups+1))
    for gi in range(ngroups):
        sl = order[bounds[gi]:bounds[gi+1]]
        if len(sl) == 0: continue
        reps = nseg[sl]
        t = np.concatenate([np.linspace(0,1,r) for r in reps]).astype(np.float32)
        src = np.repeat(sl, reps)
        Z = z0[src]*(1-t) + z1[src]*t
        Xs, Ys = to_px(Z)
        xi = np.round(Xs).astype(np.int64); yi = np.round(Ys).astype(np.int64)
        okm = (xi>=0)&(xi<W)&(yi>=0)&(yi<W)
        w = np.repeat(m[sl]*L[sl]/reps, reps)[okm]
        idx = yi[okm]*W + xi[okm]
        acc = np.bincount(idx, weights=w, minlength=W*W)
        buf += acc.reshape(W, W).astype(np.float32)
    return buf

class Canvas:
    def __init__(self, S, SS=2, cx=0.0, cy=0.0, half=1.0):
        self.S, self.SS = S, SS
        self.W = S * SS
        self.img = np.zeros((self.W, self.W, 3), np.float32)
        self.cx, self.cy, self.half = cx, cy, half

    def to_px(self, z):
        x = (np.real(z) - self.cx) / self.half * 0.5 + 0.5
        y = 0.5 - (np.imag(z) - self.cy) / self.half * 0.5
        return x * self.W, y * self.W

    def splat(self, z, color, mass):
        """Bilinear additive splat of complex points. mass: scalar or per-point.
        color: (3,) or (N,3)."""
        X, Y = self.to_px(z)
        m = np.broadcast_to(np.asarray(mass, np.float32), X.shape).copy()
        col = np.asarray(color, np.float32)
        if col.ndim == 1:
            col = np.broadcast_to(col, (len(X), 3))
        x0 = np.floor(X).astype(np.int64); y0 = np.floor(Y).astype(np.int64)
        fx = (X - x0).astype(np.float32); fy = (Y - y0).astype(np.float32)
        for dx, dy, w in ((0,0,(1-fx)*(1-fy)), (1,0,fx*(1-fy)),
                          (0,1,(1-fx)*fy), (1,1,fx*fy)):
            xi, yi = x0+dx, y0+dy
            okm = (xi>=0)&(xi<self.W)&(yi>=0)&(yi<self.W)
            np.add.at(self.img, (yi[okm], xi[okm]),
                      col[okm]*(w[okm]*m[okm])[:,None])

    def lines(self, z0, z1, color, mass_per_px=1.0, step=0.6):
        """AA line segments z0[i]->z1[i], constant brightness per pixel of length."""
        X0, Y0 = self.to_px(z0); X1, Y1 = self.to_px(z1)
        L = np.hypot(X1-X0, Y1-Y0)
        nseg = np.maximum(2, (L/step).astype(np.int64))
        col = np.asarray(color, np.float32)
        percol = col.ndim == 2
        # chunk by segments
        idx = np.arange(len(X0))
        for chunk in np.array_split(idx, max(1, len(idx)//2000)):
            if len(chunk) == 0: continue
            reps = nseg[chunk]
            t = np.concatenate([np.linspace(0,1,r) for r in reps]).astype(np.float32)
            src = np.repeat(chunk, reps)
            Z = (np.asarray(z0)[src]*(1-t) + np.asarray(z1)[src]*t)
            m = np.repeat(np.broadcast_to(np.asarray(mass_per_px,np.float32),
                                          (len(X0),))[chunk]*L[chunk]/reps, reps)
            c = col[src] if percol else col
            self.splat(Z, c, m)

    def wide_lines(self, z0, z1, color, mass_per_px=1.0, width_px=4.0, noff=7):
        """Soft wide strokes: noff parallel offsets, gaussian weights."""
        z0 = np.asarray(z0, complex); z1 = np.asarray(z1, complex)
        d = z1 - z0
        n = 1j * d / np.maximum(np.abs(d), 1e-12)      # unit normal (world units)
        w_world = width_px * (2*self.half) / self.W
        offs = np.linspace(-1, 1, noff)
        wts = np.exp(-2.2*offs**2); wts /= wts.sum()
        for o, wt in zip(offs, wts):
            sh = n * (o * w_world / 2)
            self.lines(z0 + sh, z1 + sh, color, mass_per_px * wt)

    def fill_tri(self, z1, z2, z3, color, mass_per_px2=0.01, rng=None):
        """Translucent filled triangle via uniform barycentric splatting."""
        rng = rng or np.random.RandomState(5)
        # area in px^2
        px = self.W/(2*self.half)
        area = 0.5*abs(((z2-z1).conjugate()*(z3-z1)).imag)*px*px
        K = max(200, int(area*2.2))
        r1, r2 = rng.rand(K), rng.rand(K)
        sw = r1 + r2 > 1
        r1[sw], r2[sw] = 1-r1[sw], 1-r2[sw]
        pts = z1 + r1*(z2-z1) + r2*(z3-z1)
        self.splat(pts, color, mass_per_px2*area/K)

    def glow_points(self, z, color, amp=1.0, sigma=6.0):
        """Gaussian star at points (drawn via dedicated buffer for exact shape)."""
        buf = np.zeros((self.W, self.W), np.float32)
        X, Y = self.to_px(np.asarray(z))
        x0 = np.round(X).astype(int); y0 = np.round(Y).astype(int)
        okm = (x0>=0)&(x0<self.W)&(y0>=0)&(y0<self.W)
        buf[y0[okm], x0[okm]] += 1.0
        buf = gaussian_filter(buf, sigma)
        buf *= amp / max(buf.max(), 1e-12)
        self.img += buf[:,:,None]*np.asarray(color,np.float32)[None,None,:]

    def widebloom(self, frac=0.12, sigma_px=None, thresh=0.65):
        """Downsample->blur->upsample wide bloom of bright regions."""
        lum = self.img @ np.array([0.30,0.55,0.15], np.float32)
        p = np.percentile(lum, 99.5)
        mask = np.clip((lum/(p+1e-9) - thresh)/(1-thresh), 0, 1)[:,:,None]*self.img
        sig = sigma_px or self.W*0.02
        ds = max(1, int(sig/6))
        small = mask[::ds, ::ds]
        small = gaussian_filter(small, (sig/ds, sig/ds, 0))
        big = ndzoom(small, (ds, ds, 1), order=1)[:self.W, :self.W]
        self.img += frac*big

    def tightbloom(self, frac=0.35, sigma=2.5):
        self.img += frac*gaussian_filter(self.img, (sigma, sigma, 0))

    def out(self, k=1.0, gamma=1.9, downscale=True):
        from PIL import Image
        t = 1 - np.exp(-k*self.img)
        t = np.clip(t, 0, 1)**(1/gamma)
        im = Image.fromarray((t*255).astype(np.uint8))
        if downscale and self.SS > 1:
            im = im.resize((self.S, self.S), Image.LANCZOS)
        return im
