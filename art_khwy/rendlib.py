"""Shared render kit: float32 additive canvas, AA segment/point splats,
downsample-blur-upsample bloom, filmic tone map. Dark-field aesthetic."""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom as ndzoom

class Canvas:
    def __init__(self, W, H, bg=(0.0, 0.0, 0.0)):
        self.W, self.H = W, H
        self.buf = np.zeros((H, W, 3), np.float32)
        self.buf += np.asarray(bg, np.float32)

    def _stamp(self, xs, ys, amps, color, sigma):
        """Additive gaussian stamps at float coords (vectorized, local
        kernels). xs, ys in pixel coords; amps scalar or array."""
        R = max(int(np.ceil(3 * sigma)), 1)
        k = np.arange(-R, R + 1)
        ky, kx = np.meshgrid(k, k, indexing="ij")
        xs = np.asarray(xs, np.float64); ys = np.asarray(ys, np.float64)
        amps = np.broadcast_to(np.asarray(amps, np.float32), xs.shape)
        ix = np.floor(xs).astype(np.int64); iy = np.floor(ys).astype(np.int64)
        fx = (xs - ix).astype(np.float32); fy = (ys - iy).astype(np.float32)
        # kernel per point: gaussian centered at fractional offset
        # (chunk to bound memory)
        H, W = self.H, self.W
        col = np.asarray(color, np.float32)
        flat = np.zeros((H * W,), np.float32)
        CH = max(1, int(2e7 / ((2*R+1)**2)))
        for s in range(0, len(xs), CH):
            e = min(s + CH, len(xs))
            gx = kx[None, :, :] - fx[s:e, None, None]
            gy = ky[None, :, :] - fy[s:e, None, None]
            g = np.exp(-(gx*gx + gy*gy) / (2*sigma*sigma)).astype(np.float32)
            g *= amps[s:e, None, None] / (2*np.pi*sigma*sigma)
            px = (ix[s:e, None, None] + kx[None]).ravel()
            py = (iy[s:e, None, None] + ky[None]).ravel()
            ok = (px >= 0) & (px < W) & (py >= 0) & (py < H)
            np.add.at(flat, (py[ok]*W + px[ok]), g.ravel()[ok])
        lay = flat.reshape(H, W)
        for c in range(3):
            self.buf[:, :, c] += lay * col[c]
        return lay

    def segments(self, A, B, color, width=1.2, amp=1.0, step=0.4,
                 amp_per=None, color_per=None):
        """Draw AA segments A[i]->B[i]. amp_per/color_per: per-segment."""
        A = np.asarray(A, np.float64); B = np.asarray(B, np.float64)
        L = np.linalg.norm(B - A, axis=1)
        nseg = len(A)
        xs_all, ys_all, am_all, col_all = [], [], [], []
        for i in range(nseg):
            npts = max(int(L[i] / step), 2)
            t = (np.arange(npts) + 0.5) / npts
            P = A[i][None, :] + t[:, None] * (B[i] - A[i])[None, :]
            a = (amp if amp_per is None else amp_per[i]) * L[i] / npts
            xs_all.append(P[:, 0]); ys_all.append(P[:, 1])
            am_all.append(np.full(npts, a, np.float32))
            c = color if color_per is None else color_per[i]
            col_all.append(np.broadcast_to(np.asarray(c, np.float32), (npts, 3)))
        xs = np.concatenate(xs_all); ys = np.concatenate(ys_all)
        am = np.concatenate(am_all); cols = np.concatenate(col_all)
        # group by color? simple: per unique color splat; here just loop 3 chans
        R = max(int(np.ceil(3 * width)), 1)
        k = np.arange(-R, R + 1)
        ky, kx = np.meshgrid(k, k, indexing="ij")
        ix = np.floor(xs).astype(np.int64); iy = np.floor(ys).astype(np.int64)
        fx = (xs - ix).astype(np.float32); fy = (ys - iy).astype(np.float32)
        H, W = self.H, self.W
        flat = np.zeros((H * W, 3), np.float32)
        CH = max(1, int(1.2e7 / ((2*R+1)**2)))
        for s in range(0, len(xs), CH):
            e = min(s + CH, len(xs))
            gx = kx[None] - fx[s:e, None, None]
            gy = ky[None] - fy[s:e, None, None]
            g = np.exp(-(gx*gx + gy*gy) / (2*width*width)).astype(np.float32)
            g *= am[s:e, None, None] / (2*np.pi*width*width)
            px = (ix[s:e, None, None] + kx[None]).ravel()
            py = (iy[s:e, None, None] + ky[None]).ravel()
            ok = (px >= 0) & (px < W) & (py >= 0) & (py < H)
            gv = g.reshape(e - s, -1)
            cc = cols[s:e]
            for c in range(3):
                v = (gv * cc[:, c:c+1]).ravel()[ok]
                np.add.at(flat[:, c], (py[ok]*W + px[ok]), v)
        self.buf += flat.reshape(H, W, 3)

    def stars(self, xs, ys, color, sigma=2.0, amp=1.0):
        self._stamp(xs, ys, amp, color, sigma)

    def bloom(self, sigmas=(6, 20, 60), gains=(0.35, 0.22, 0.14), thresh=0.55):
        src = self.buf
        lum = src.max(axis=2)
        m = np.clip((lum - thresh) / max(lum.max() - thresh, 1e-6), 0, 1)[..., None]
        base = src * m
        out = src.copy()
        for sg, gn in zip(sigmas, gains):
            ds = max(int(sg / 6), 1)
            small = base[::ds, ::ds]
            bl = gaussian_filter(small, (sg/ds, sg/ds, 0))
            if ds > 1:
                bl = ndzoom(bl, (ds, ds, 1), order=1)[:self.H, :self.W]
                # pad if zoom undershoots
                if bl.shape[0] < self.H or bl.shape[1] < self.W:
                    pad = np.zeros_like(out)
                    pad[:bl.shape[0], :bl.shape[1]] = bl
                    bl = pad
            out += gn * bl
        self.buf = out

    def tonemap(self, k=1.0, gamma=2.2, dither=True):
        x = 1.0 - np.exp(-k * np.clip(self.buf, 0, None))
        x = np.power(np.clip(x, 0, 1), 1.0/gamma)
        if dither:
            x += (np.random.default_rng(1).random(x.shape).astype(np.float32) - 0.5)/255.0
        return (np.clip(x, 0, 1) * 255).astype(np.uint8)

def save(img_u8, path):
    from PIL import Image
    Image.fromarray(img_u8).save(path)
