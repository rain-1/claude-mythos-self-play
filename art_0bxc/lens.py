"""lens.py — 'Seen Through the Synapse': the cosmic web behind a Schwarzschild black hole, exactly.

Null geodesics of the Schwarzschild metric (G = c = 1, M = 1).  A photon with impact parameter b sweeps
the azimuth
    phi(b) = 2 * int_0^{u_max} du / sqrt(1/b^2 - u^2 + 2 u^3)  -  (the part inside the observer's radius),
u = 1/r, u_max the turning point (smallest positive root of 2u^3 - u^2 + 1/b^2).  For b < b_c = 3*sqrt(3)
there is no turning point: the photon falls in (the shadow).  Near b_c the sweep diverges logarithmically:
the whole sky is wrapped, again and again, in thinner and thinner rings around the shadow.
The observer stands at r_o; a pixel at angle theta from the hole sees the sky point that its geodesic
came from; surface brightness is conserved along rays (Liouville), so the picture is a pure lookup
of the sky's pigment density — nothing is brightened, nothing invented.  The shadow is left as paper.
"""
import numpy as np, sys, json, time, warnings
warnings.filterwarnings('ignore')
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.ndimage import map_coordinates, gaussian_filter
from PIL import Image
sys.path.insert(0, '.')
from pastel import Sheet, PIG, absorb, text_density, finish, text_width

BC = 3 * np.sqrt(3.0)


def u_turn(b):
    """smallest positive root of 2u^3 - u^2 + 1/b^2 = 0 (b > b_c)."""
    f = lambda u: 2 * u ** 3 - u ** 2 + 1 / b ** 2
    return brentq(f, 1e-12, 1.0 / 3.0 - 1e-15)


def sweep_inf(b):
    """int_0^{u_max} du / sqrt(1/b^2 - u^2 + 2u^3), with the square-root endpoint removed by u = um - v^2."""
    um = u_turn(b)

    def g(v):
        u = um - v * v
        val = 1 / b ** 2 - u * u + 2 * u ** 3
        return 2 * v / np.sqrt(max(val, 1e-300))
    r, _ = quad(g, 0.0, np.sqrt(um), limit=200)
    return r


def sweep_partial(b, u_o):
    """int_0^{u_o} du / sqrt(1/b^2 - u^2 + 2u^3)  (observer side, no singularity if u_o < u_max)."""
    r, _ = quad(lambda u: 1 / np.sqrt(1 / b ** 2 - u * u + 2 * u ** 3), 0.0, u_o, limit=200)
    return r


def deflection_table(r_o, nb=3000, b_max=None):
    """b -> total azimuth sweep Delta phi from the observer at r_o to infinity, for b in (b_c, b_max)."""
    b_max = b_max or 0.97 * r_o / np.sqrt(1 - 2.0 / r_o)
    eps = np.geomspace(1e-10, b_max - BC, nb)
    bs = BC + eps
    u_o = 1.0 / r_o
    dphi = np.empty(nb)
    for i, b in enumerate(bs):
        dphi[i] = 2 * sweep_inf(b) - sweep_partial(b, u_o)
    return bs, dphi


def render(FINAL=1024, SS=2, tag='proto_lens', sky='web_sky_2048.png', r_o=30.0, fov=0.62, tiles_lon=6.0,
           caption=True, title='Seen Through the Synapse', ring_d=1.3, ring_w=1.0, shadow='paper',
           sub='the web behind a black hole: every ray a Schwarzschild geodesic, the whole sky wrapped in rings around a disc of paper',
           gran=0.0, sky_gain=1.0, hole_centre=(0.5, 0.5), gamma_sky=1.0):
    t0 = time.time()
    W = H = FINAL * SS
    rs = FINAL / 1024.0 * SS
    # ---- sky: pigment absorbance of the seamless web (recovered from its print)
    im = Image.open(sky).convert('RGB')
    srgb = np.asarray(im, np.float32) / 255.0
    lin = np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)
    paper = np.percentile(lin.reshape(-1, 3), 92, axis=0)
    A_sky = -np.log(np.clip(lin / paper[None, None, :], 1e-3, 1.0)) * sky_gain
    A_sky = A_sky ** gamma_sky if gamma_sky != 1.0 else A_sky
    Hs, Ws = A_sky.shape[:2]
    # ---- geodesics: table of the azimuth sweep against impact parameter
    bs, dphi = deflection_table(r_o, b_max=min(0.97 * r_o / np.sqrt(1 - 2.0 / r_o), r_o * np.sin(min(fov * 1.6, 1.4)) / np.sqrt(1 - 2.0 / r_o)))
    cert = dict(r_o=r_o, b_c=float(BC), fov_rad=fov, tiles_lon=tiles_lon,
                check_weak_field=[[float(b), float(dphi[i] - (np.pi - np.arcsin(min(1.0, b * np.sqrt(1 - 2 / r_o) / r_o)))), float(4 / b)] for i, b in enumerate(bs) if b > 0.5 * bs[-1]][::400],
                check_divergence=[[float(bs[i] - BC), float(dphi[i])] for i in (0, 300, 600)])
    # ---- observer's sky: pixel -> angle theta from the hole (gnomonic), azimuth psi
    cx, cy = hole_centre[0] * W, hole_centre[1] * H
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    fl = (W / 2) / np.tan(fov)
    px, py = xx - cx, -(yy - cy)
    rho = np.hypot(px, py)
    theta = np.arctan(rho / fl)
    psi = np.arctan2(py, px)
    # impact parameter for a static observer at r_o
    b = r_o * np.sin(theta) / np.sqrt(1 - 2.0 / r_o)
    shadow_mask = b < BC
    # sweep by interpolation in log(b - b_c)
    lb = np.log(np.clip(b - BC, 1e-10, None))
    sw = np.interp(lb, np.log(bs - BC), dphi)
    sw = np.where(b > bs[-1], np.pi - theta + 4 / np.clip(b, 1e-9, None), sw)   # beyond the table (outside the view)
    # outgoing direction: -cos(sw) f + sin(sw) e_b   (f forward, e_b unit impact direction)
    ebx, eby = np.cos(psi), np.sin(psi)
    dz = -np.cos(sw)
    dx = np.sin(sw) * ebx
    dy = np.sin(sw) * eby
    # sky map: equirectangular around the vertical axis; forward at the centre; web box tiled tiles_lon per turn
    lon = np.arctan2(dx, dz)
    lat = np.arcsin(np.clip(dy, -1, 1))
    tu = (lon / (2 * np.pi)) * tiles_lon
    tv = (lat / np.pi) * (tiles_lon / 2.0)
    coords = [np.mod(0.5 - tv, 1.0) * Hs, np.mod(tu + 0.25, 1.0) * Ws]
    A = np.stack([map_coordinates(A_sky[..., c], coords, order=1, mode='grid-wrap') for c in range(3)], -1).astype(np.float32)
    A[shadow_mask] = 0.0
    sheet = Sheet(W, H, seed=17)
    sheet.A += A
    # photon ring: the theorem, b = 3 sqrt 3 M, drawn as one thin coral circle at the shadow's rim
    theta_c = np.arcsin(BC * np.sqrt(1 - 2.0 / r_o) / r_o)
    rho_c = fl * np.tan(theta_c)
    ring = np.exp(-((rho - rho_c) / (ring_w * rs)) ** 2).astype(np.float32)
    sheet.wash(ring * ring_d, 'coral')
    cert['shadow_radius_px'] = float(rho_c / SS)
    cert['shadow_fraction_of_width'] = float(2 * rho_c / W)
    if caption:
        ts_ = int(0.030 * H); ss = int(0.0135 * H)
        sheet.caption_strip(0.905, 0.985, f=0.62)
        items = [(title, int(0.045 * W), int(0.925 * H), ts_, 'serif_bold', 'ls')]
        if text_width(sub, ss, 'italic') > 0.9 * W:
            print('CAPTION OVERRUN', text_width(sub, ss, 'italic') / W)
        items.append((sub, int(0.045 * W), int(0.966 * H), ss, 'italic', 'ls'))
        sheet.wash(text_density(W, H, items) * 1.2, 'ink')
    img = sheet.develop()
    finish(img, (FINAL, FINAL), f'{tag}_{FINAL}.png')
    cert['secs'] = time.time() - t0
    json.dump(cert, open(f'{tag}_{FINAL}_cert.json', 'w'), indent=1)
    print(json.dumps(cert, indent=1))


if __name__ == '__main__':
    kw = {}
    for a in sys.argv[1:]:
        k, v = a.split('=', 1)
        try:
            v = json.loads(v)
        except Exception:
            pass
        kw[k] = v
    render(**kw)
