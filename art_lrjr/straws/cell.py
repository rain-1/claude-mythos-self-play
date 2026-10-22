import numpy as np, json
from tracer import render_cell

V0 = np.array(json.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__), 'octa.json'))))

def lin(h):
    h = h.lstrip('#'); return (np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0) ** 2.2

def camera(elev=38, azim=-55, dist=6.0):
    e, a = np.radians(elev), np.radians(azim)
    eye = dist * np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    fwd = -eye / np.linalg.norm(eye)
    right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return eye, fwd, right, up

def render(cyc, size, straw, stripe, bead, ground, V=V0, rot=None, spp=24, rc=0.075, rs=0.13,
           fov=0.29, cam=None, seed=1, pitch=0.11, nstripe=2.0, sun=(-0.45, -0.75, 0.9), zpad=0.55):
    P = V[list(cyc)]
    if rot is not None:
        P = P @ rot.T
    A = P.copy(); B = np.roll(P, -1, axis=0)
    zg = P[:, 2].min() - zpad
    eye, fwd, right, up = camera() if cam is None else cam
    sun = np.array(sun, float); sun /= np.linalg.norm(sun)
    img, al = render_cell(A, B, rc, P.copy(), rs, zg, size, size, eye, fwd, right, up, fov, sun, 0.08,
                          lin(straw), lin(stripe), lin(bead), lin(ground),
                          np.array([0.44, 0.44, 0.50]), np.array([0.66, 0.62, 0.56]), spp, pitch, nstripe, seed)
    return img, al
