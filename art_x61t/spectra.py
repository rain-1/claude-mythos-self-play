"""Spectrum -> sRGB helpers: CIE 1931 CMF (Wyman et al. multi-Gaussian fits),
blackbody sun weighting, XYZ->linear sRGB, filmic tone map."""
import numpy as np

def _pg(lam, mu, s1, s2):
    s = np.where(lam < mu, s1, s2)
    return np.exp(-0.5*((lam-mu)/s)**2)

def cmf(lam_nm):
    x = (1.056*_pg(lam_nm, 599.8, 37.9, 31.0)
         + 0.362*_pg(lam_nm, 442.0, 16.0, 26.7)
         - 0.065*_pg(lam_nm, 501.1, 20.4, 26.2))
    y = (0.821*_pg(lam_nm, 568.8, 46.9, 40.5)
         + 0.286*_pg(lam_nm, 530.9, 16.3, 31.1))
    z = (1.217*_pg(lam_nm, 437.0, 11.8, 36.0)
         + 0.681*_pg(lam_nm, 459.0, 26.0, 13.8))
    return np.stack([x, y, z])

def planck(lam_nm, T=5778.0):
    lam = lam_nm*1e-9
    h, c, kB = 6.626e-34, 2.998e8, 1.381e-23
    B = 1.0/(lam**5*(np.exp(h*c/(lam*kB*T)) - 1))
    return B/B.max()

XYZ2RGB = np.array([[ 3.2406, -1.5372, -0.4986],
                    [-0.9689,  1.8758,  0.0415],
                    [ 0.0557, -0.2040,  1.0570]])

def spectra_to_rgb(I, lam_nm, T=5778.0):
    """I: [..., nlam] arbitrary-unit spectral intensity -> linear sRGB [...,3]"""
    W = cmf(lam_nm)*planck(lam_nm, T)            # [3, nlam]
    XYZ = I @ W.T                                # [...,3]
    rgb = XYZ @ XYZ2RGB.T
    # gamut: add white to kill negatives (per pixel)
    mn = np.minimum(rgb.min(axis=-1), 0.0)
    rgb = rgb - mn[..., None]
    return rgb

def tonemap(rgb, k=1.0, gamma=2.2, sat=1.0):
    x = 1.0 - np.exp(-k*np.maximum(rgb, 0))
    if sat != 1.0:
        lum = (0.2126*x[...,0] + 0.7152*x[...,1] + 0.0722*x[...,2])[...,None]
        x = np.clip(lum + sat*(x-lum), 0, 1)
    return (255*np.clip(x, 0, 1)**(1/gamma)).astype(np.uint8)
