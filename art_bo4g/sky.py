"""sky.py — the cosmic microwave background as a pastel sky.

C_ell from CAMB (Planck-2018-like LambdaCDM), a Gaussian realisation on a HEALPix sphere (synfast),
projected to a Mollweide ellipse.  The temperature field is the certificate: the loudest note is the
first acoustic peak at ell ~ 220, about a degree on the sky.
"""
import sys, json, time
import numpy as np
import camb, healpy as hp


def spectrum(lmax=3000):
    pars = camb.set_params(H0=67.36, ombh2=0.02237, omch2=0.1200, mnu=0.06, omk=0, tau=0.0544,
                           As=2.1e-9, ns=0.9649, lmax=lmax, lens_potential_accuracy=1)
    res = camb.get_results(pars)
    pw = res.get_cmb_power_spectra(pars, CMB_unit='muK', raw_cl=True)
    cl = pw['total'][:, 0]  # TT, muK^2, raw C_ell
    return cl


def sky_map(cl, nside=2048, seed=5, lmax=3000):
    np.random.seed(seed)
    m = hp.synfast(cl, nside, lmax=lmax, pol=False, verbose=False)
    return m


def mollweide(m, W, H, rot_lon=0.0):
    """sample a HEALPix map onto a W x H Mollweide ellipse (NaN outside)"""
    nside = hp.get_nside(m)
    R = min(W / (4 * np.sqrt(2)), H / (2 * np.sqrt(2)))   # ellipse semi-axes 2*sqrt2*R, sqrt2*R
    ys, xs = np.mgrid[0:H, 0:W]
    x = (xs + 0.5 - W / 2) / R
    y = -(ys + 0.5 - H / 2) / R
    inside = (x / (2 * np.sqrt(2))) ** 2 + (y / np.sqrt(2)) ** 2 <= 1.0
    th = np.arcsin(np.clip(y / np.sqrt(2), -1, 1))
    lat = np.arcsin(np.clip((2 * th + np.sin(2 * th)) / np.pi, -1, 1))
    lon = np.pi * x / (2 * np.sqrt(2) * np.maximum(np.cos(th), 1e-9)) + rot_lon
    colat = np.pi / 2 - lat
    pix = hp.ang2pix(nside, colat[inside], np.mod(lon[inside], 2 * np.pi))
    out = np.full((H, W), np.nan, np.float32)
    out[inside] = m[pix]
    return out, inside


def gnomonic(m, W, H, fov_deg, lon0=0.0, lat0=0.0):
    """tangent-plane patch of fov_deg (full width) centred on (lon0, lat0)"""
    nside = hp.get_nside(m)
    half = np.tan(np.radians(fov_deg) / 2)
    ys, xs = np.mgrid[0:H, 0:W]
    x = (xs + 0.5 - W / 2) / (W / 2) * half
    y = -(ys + 0.5 - H / 2) / (H / 2) * half
    # tangent plane at (lon0, lat0): basis e (east), n (north), c (centre)
    c = np.array([np.cos(lat0) * np.cos(lon0), np.cos(lat0) * np.sin(lon0), np.sin(lat0)])
    e = np.array([-np.sin(lon0), np.cos(lon0), 0.0])
    n = np.cross(c, e)
    v = c[None, None, :] + x[..., None] * e[None, None, :] + y[..., None] * n[None, None, :]
    v /= np.linalg.norm(v, axis=-1, keepdims=True)
    pix = hp.vec2pix(nside, v[..., 0].ravel(), v[..., 1].ravel(), v[..., 2].ravel())
    return m[pix].reshape(H, W)


if __name__ == '__main__':
    t0 = time.time()
    cl = spectrum()
    ell = np.arange(len(cl))
    dl = ell * (ell + 1) * cl / (2 * np.pi)
    peak = int(np.argmax(dl[50:]) + 50)
    print('first peak at ell =', peak, ' D_ell = %.0f muK^2' % dl[peak], ' -> %.2f deg' % (180.0 / peak))
    np.save('cache/cl_tt.npy', cl)
    nside = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    m = sky_map(cl, nside=nside)
    print('map rms %.1f muK, min %.0f max %.0f' % (m.std(), m.min(), m.max()), 'elapsed %.0f s' % (time.time() - t0))
    hp.write_map('cache/sky_%d.fits' % nside, m, overwrite=True, dtype=np.float32)
    json.dump(dict(peak_ell=peak, peak_deg=180.0 / peak, rms=float(m.std()), nside=nside),
              open('cache/sky_cert.json', 'w'), indent=1)
