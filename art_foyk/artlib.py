"""Shared render kit: float32 additive canvas, AA segment splatting, bloom, filmic tone, text."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

def canvas(S):
    return np.zeros((S, S, 3), np.float32)

def _splat_points(buf, xs, ys, amp, color, rad):
    """Gaussian-ish dot splats via bilinear + later blur; here: direct bilinear deposit."""
    S = buf.shape[0]
    xs = np.asarray(xs, np.float64); ys = np.asarray(ys, np.float64)
    ok = (xs > -4) & (xs < S+3) & (ys > -4) & (ys < S+3)
    xs, ys = xs[ok], ys[ok]
    if np.isscalar(amp) or np.ndim(amp)==0: amp = np.full(len(xs), float(amp))
    else: amp = np.asarray(amp, np.float64)[ok]
    x0 = np.floor(xs).astype(np.int64); y0 = np.floor(ys).astype(np.int64)
    fx = xs - x0; fy = ys - y0
    col = np.asarray(color, np.float64)
    for dy in (0,1):
        for dx in (0,1):
            w = (fx if dx else 1-fx)*(fy if dy else 1-fy)*amp
            xi = np.clip(x0+dx, 0, S-1); yi = np.clip(y0+dy, 0, S-1)
            idx = yi*S + xi
            for c in range(3):
                np.add.at(buf[...,c].reshape(-1), idx, w*col[c])

def polyline(buf, pts, color, amp=1.0, step=0.7, closed=False, amps=None):
    """AA polyline via dense point sampling; pts (n,2) in pixel coords."""
    pts = np.asarray(pts, np.float64)
    if closed: pts = np.vstack([pts, pts[:1]])
    seg = np.diff(pts, axis=0)
    L = np.hypot(seg[:,0], seg[:,1])
    xs_all, ys_all, aa = [], [], []
    for i in range(len(seg)):
        n = max(2, int(L[i]/step))
        t = np.linspace(0, 1, n, endpoint=False)
        xs_all.append(pts[i,0] + t*seg[i,0]); ys_all.append(pts[i,1] + t*seg[i,1])
        if amps is not None:
            a0 = amps[i]; a1 = amps[(i+1) % len(amps)]
            aa.append((a0 + t*(a1-a0)))
        else:
            aa.append(np.full(n, 1.0))
    xs = np.concatenate(xs_all); ys = np.concatenate(ys_all); aa = np.concatenate(aa)
    _splat_points(buf, xs, ys, amp*aa*step, color, 1.0)

def catmull(pts, closed=True, subdiv=24, alpha=0.5):
    """Centripetal Catmull-Rom spline through pts."""
    P = np.asarray(pts, np.float64)
    n = len(P)
    if n < 3: return P
    out = []
    idx = lambda i: i % n if closed else min(max(i,0), n-1)
    for i in range(n if closed else n-1):
        p0,p1,p2,p3 = P[idx(i-1)],P[idx(i)],P[idx(i+1)],P[idx(i+2)]
        def tj(ti, pa, pb):
            return ti + max(np.hypot(*(pb-pa)),1e-9)**alpha
        t0=0.; t1=tj(t0,p0,p1); t2=tj(t1,p1,p2); t3=tj(t2,p2,p3)
        t = np.linspace(t1,t2,subdiv,endpoint=False)
        A1=(t1-t)[:,None]/(t1-t0)*p0+(t-t0)[:,None]/(t1-t0)*p1
        A2=(t2-t)[:,None]/(t2-t1)*p1+(t-t1)[:,None]/(t2-t1)*p2
        A3=(t3-t)[:,None]/(t3-t2)*p2+(t-t2)[:,None]/(t3-t2)*p3
        B1=(t2-t)[:,None]/(t2-t0)*A1+(t-t0)[:,None]/(t2-t0)*A2
        B2=(t3-t)[:,None]/(t3-t1)*A2+(t-t1)[:,None]/(t3-t1)*A3
        C=(t2-t)[:,None]/(t2-t1)*B1+(t-t1)[:,None]/(t2-t1)*B2
        out.append(C)
    return np.vstack(out)

def star(buf, x, y, color, amp=1.0, rad=3.0):
    S = buf.shape[0]
    r = int(max(3, rad*4))
    xi, yi = int(round(x)), int(round(y))
    if xi < -r or xi > S+r or yi < -r or yi > S+r: return
    y0,y1 = max(0,yi-r), min(S,yi+r+1); x0,x1 = max(0,xi-r), min(S,xi+r+1)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d2 = (xx-x)**2 + (yy-y)**2
    g = np.exp(-d2/(2*rad*rad))*amp
    for c in range(3): buf[y0:y1, x0:x1, c] += g*color[c]

def bloom(buf, sigmas=(2, 8, 30), weights=(1.0, 0.35, 0.18), thresh=None):
    out = buf.copy()
    src = buf
    if thresh is not None:
        m = buf.max(-1)
        src = buf * np.clip((m - thresh)/max(thresh,1e-6), 0, 1)[...,None]
    for s, w in zip(sigmas, weights):
        if s <= 6:
            bl = np.stack([gaussian_filter(src[...,c], s) for c in range(3)], -1)
        else:
            ds = max(1, int(s/6))
            small = src[::ds, ::ds]
            bl = np.stack([gaussian_filter(small[...,c], s/ds) for c in range(3)], -1)
            bl = np.kron(bl, np.ones((ds,ds,1), np.float32))[:buf.shape[0], :buf.shape[1]]
        out += w*bl
    return out

def tonemap(buf, k=1.0, gamma=0.9, base=(0.012, 0.016, 0.026)):
    x = 1.0 - np.exp(-k*np.clip(buf,0,None))
    x = np.clip(x, 0, 1)**gamma
    x = x + np.asarray(base)*(1-x)
    return x

def save(buf, path, final=None, dither=True):
    img = np.clip(buf, 0, 1)
    if dither: img = np.clip(img + (np.random.rand(*img.shape)-0.5)/255.0, 0, 1)
    im = Image.fromarray((img*255).astype(np.uint8))
    if final and final != img.shape[0]:
        im = im.resize((final, final), Image.LANCZOS)
    im.save(path)
    return im

def get_font(size, bold=False):
    cands = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for c in cands:
        try: return ImageFont.truetype(c, size)
        except Exception: continue
    return ImageFont.load_default()

def bake_text(img_arr, texts, S):
    """texts: list of (x, y, s, size, color, bold, anchor). Draw on top AFTER tonemap. img_arr in [0,1]."""
    im = Image.fromarray((np.clip(img_arr,0,1)*255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for (x, y, s, size, color, bold, anchor) in texts:
        f = get_font(size, bold)
        col = tuple(int(255*c) for c in color)
        d.text((x, y), s, font=f, fill=col, anchor=anchor)
    return np.asarray(im).astype(np.float32)/255.0
