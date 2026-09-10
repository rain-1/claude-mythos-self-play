"""snowio.py — read snow.c outputs and map the axial hex array to Cartesian rasters."""
import numpy as np
from scipy.ndimage import affine_transform

SQ3 = np.sqrt(3.0)


def load(prefix, N):
    t = np.fromfile(prefix + '.t', dtype=np.int32).reshape(N, N)
    c = np.fromfile(prefix + '.c', dtype=np.float32).reshape(N, N)
    b = np.fromfile(prefix + '.b', dtype=np.float32).reshape(N, N)
    d = np.fromfile(prefix + '.d', dtype=np.float32).reshape(N, N)
    return t, c, b, d


def axial_to_cart(arr, px_per_cell, out_size, order=0, cval=0.0, centre=None):
    """arr indexed [i, j] (axial); cell (i,j) sits at x = (i + j/2), y = j*sqrt(3)/2 (cell units).
    Returns an out_size x out_size raster centred on the array centre (or `centre` axial coords)."""
    N = arr.shape[0]
    if centre is None:
        centre = ((N - 1) / 2.0, (N - 1) / 2.0)
    # output pixel (Y, X) -> cell coords: x = (X - W/2)/p + xc, y = (Y - H/2)/p + yc  (cartesian, cell units)
    # cartesian (x, y) -> axial: j = y / (sqrt3/2), i = x - j/2
    p = px_per_cell
    W = H = out_size
    xc = centre[0] + centre[1] / 2.0
    yc = centre[1] * SQ3 / 2.0
    # i = x - j/2 = (X - W/2)/p + xc - ((Y - H/2)/p + yc)/sqrt3*... let's write as matrix on (Y, X)
    # j = ((Y - H/2)/p + yc) * 2/sqrt3
    # i = ((X - W/2)/p + xc) - j/2
    a_jY = 2.0 / (SQ3 * p); a_jX = 0.0; o_j = yc * 2.0 / SQ3 - a_jY * H / 2.0
    a_iY = -a_jY / 2.0; a_iX = 1.0 / p; o_i = xc - a_iX * W / 2.0 - o_j / 2.0
    M = np.array([[a_iY, a_iX], [a_jY, a_jX]])
    off = np.array([o_i, o_j])
    return affine_transform(arr.astype(np.float32), M, offset=off, output_shape=(H, W), order=order, cval=cval, mode='constant')
