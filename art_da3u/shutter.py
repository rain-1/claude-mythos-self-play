"""Rolling-shutter pinwheels.  Row y is read at time tau=y/H, so a blade at angle a
appears where  phi - 2*pi*k*tau(y) = a  (mod 2pi/N).  For a thin radial blade
through a centre at height y0 this is Kepler's equation  phi - e sin(phi) = M
with e = 2*pi*k*r/H  (r in pixels): the blade breaks apart where e > 1."""
import numpy as np

def blade_field(X, Y, cx, cy, R, N, k, H, phase=0.0, r0=0.13, width=0.42, tip=0.55, curl=0.0):
    """Return (s, j, u, rr): s = signed physical distance inside a blade (px, >0 inside),
    j = blade index, u = across-blade coordinate in [-1,1], rr = r/R."""
    dx, dy = X - cx, Y - cy
    r = np.hypot(dx, dy)
    phi = np.arctan2(dy, dx)
    theta = 2*np.pi*k*(Y / H) + phase          # rotation at the time row Y is read
    rr = r / R
    psi = phi - theta - curl*rr                 # angle in the blade frame
    sec = 2*np.pi / N
    j = np.floor((psi + sec/2) / sec)
    dpsi = psi - j*sec - 0.0
    dpsi = (dpsi + sec/2) % sec - sec/2
    # physical half-width profile b(rr): grows from hub, rounded tip
    t = np.clip((rr - r0) / (1 - r0), 0, 1)
    b = width*R*np.sin(np.pi*np.clip(t, 0, 1)**0.85*0.5 + 0.0)**0.7 * np.sqrt(np.clip(1 - t**8, 0, 1))
    b = b * (0.55 + 0.45*t)
    across = r*np.sin(dpsi)                     # signed physical distance from centreline
    s = b - np.abs(across)
    s = np.minimum(s, (1.0 - rr)*R*3)
    s = np.minimum(s, (rr - r0*0.6)*R*3)
    u = across / np.maximum(b, 1e-6)
    return s, (j.astype(int) % N), u, rr
