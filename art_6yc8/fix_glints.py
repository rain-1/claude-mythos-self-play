"""fix_glints.py raw.png out.png — undo the contact-glint blend and redo it with an occlusion test
(the renderer drew every contact; contacts behind the opaque ball must not show)."""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from render_cyl import burr, contacts, normalize
P, U, r = burr()
im = np.asarray(Image.open(sys.argv[1]).convert('RGB'), np.float32) / 255
S = im.shape[0]
lin = np.where(im <= 0.04045, im / 12.92, ((im + 0.055) / 1.055) ** 2.4)
cam = np.array([0.35, 0.25, 1.0]); f = normalize(cam); eye = f * 9.0; fwd = -f
up = np.array([0, 0, 1.0]); right = normalize(np.cross(fwd, up)); upv = np.cross(right, fwd); fov = 0.55
C = contacts(P, U, r)
def glow_of(vis_only):
    g = np.zeros((S, S), np.float32); n = 0
    for c in C:
        v = c - eye; z = v @ fwd; px = (v @ right) / (z * fov); py = (v @ upv) / (z * fov)
        X, Y = (px + 1) / 2 * S, (1 - py) / 2 * S
        if not (0 <= X < S and 0 <= Y < S): continue
        if vis_only:
            d = v / np.linalg.norm(v); b = eye @ d; cc = eye @ eye - 1; disc = b * b - cc
            if disc > 0 and (-b - np.sqrt(disc)) < np.linalg.norm(v) - 1e-3: continue   # ball in front
        g[int(Y), int(X)] += 1; n += 1
    sg = S / 700
    return np.clip(gaussian_filter(g, sg) * 2 * np.pi * sg * sg, 0, 1), n
coral = np.array([1.0, 0.42, 0.36], np.float32)
g_all, na = glow_of(False)
base = (lin - coral * 0.8 * g_all[..., None]) / (1 - 0.8 * g_all[..., None])
g_vis, nv = glow_of(True)
sg = S / 520   # slightly larger, clearer glints
g_vis2 = g_vis
out = base * (1 - 0.8 * g_vis2[..., None]) + coral * 0.8 * g_vis2[..., None]
out = np.clip(out, 0, 1)
s = np.where(out <= 0.0031308, 12.92 * out, 1.055 * out ** (1 / 2.4) - 0.055)
Image.fromarray((s * 255 + 0.5).clip(0, 255).astype(np.uint8)).save(sys.argv[2])
print('contacts drawn before', na, 'visible now', nv)
