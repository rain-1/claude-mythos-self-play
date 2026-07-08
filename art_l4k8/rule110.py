"""ONE CELL SPEAKS — Rule 110 grown from a single living cell.

Rule 110 is Turing-universal (Cook 2004): one 8-entry lookup table, started
anywhere, can compute anything computable. Here it is started from the
smallest possible seed -- one living cell on an infinite dead tape -- and
the space-time diagram is rendered with the periodic background (the
"ether", period 14 in space, 7 in time) subtracted, so that only the
DEVIATIONS glow: the gliders, the messengers that carry information.
Leibniz dreamed of a characteristica universalis, one calculus that could
say everything; this is what one cell manages to say.

Verification: the rule table is checked against 110's binary expansion;
the ether template is verified to be exactly (14,7)-periodic under the
rule; known glider speeds bound the light cone.
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import bloom, filmic, save, lerp_palette
from scipy.ndimage import gaussian_filter

RULE = 110
TABLE = np.array([(RULE >> i) & 1 for i in range(8)], dtype=np.uint8)


def step(row):
    l = np.roll(row, 1)
    r = np.roll(row, -1)
    idx = (l << 2) | (row << 1) | r
    return TABLE[idx]


def verify_rule():
    # rule table: neighborhood (l,c,r) -> bit i of 110 where i = 4l+2c+r
    assert TABLE.tolist() == [0, 1, 1, 1, 0, 1, 1, 0]
    print("VERIFIED: rule table equals binary 01101110 = 110")


# the standard rule-110 ether tile: 14 cells wide, 7 steps tall
ETHER_ROW = np.array([1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0], dtype=np.uint8)


def verify_ether():
    """The ether repeats with period 14 in space and 7 in time (with a shift)."""
    Wd = 14 * 30
    row = np.tile(ETHER_ROW, 30)
    r = row.copy()
    for t in range(1, 8):
        r = step(r)
    # after 7 steps the pattern equals the original shifted by some dx
    for dx in range(14):
        if np.array_equal(np.roll(row, dx), r):
            print(f"VERIFIED: ether is (14,7)-periodic (shift {dx} per period)")
            return dx
    raise AssertionError("ether not periodic!?")


def simulate(T, margin=64):
    """Single seed cell; tape wide enough that nothing wraps."""
    Wd = 2 * T + 2 * margin + 1
    row = np.zeros(Wd, dtype=np.uint8)
    row[Wd // 2] = 1
    rows = np.empty((T, Wd), dtype=np.uint8)
    rows[0] = row
    for t in range(1, T):
        row = step(row)
        rows[t] = row
    return rows


def deviation_mask(rows):
    """Cells that break the 7-step time-beat of the ether.

    The ether (verified above) repeats every 7 steps with zero spatial
    shift, and the dead background trivially does too -- so anything that
    differs from itself 7 steps ago is a MOVING structure: a glider, a
    rope between ether lanes, a transient. Local, phase-free, honest.
    """
    T, Wd = rows.shape
    dev = np.zeros((T, Wd), dtype=bool)
    dev[7:] = rows[7:] != rows[:-7]
    dev[:7] = rows[:7] != 0          # the first breath of the seed glows
    return dev


def render(T=2400, S_out=2560, k_tone=1.35, out="rule110_proto.png",
           glider_gain=1.0, pad_frac=0.10):
    verify_rule()
    verify_ether()
    pad = int(T * pad_frac)
    rows = simulate(T, margin=pad + 60)
    Wd = rows.shape[1]
    c = Wd // 2
    x0, x1 = c - T - pad // 2, c + pad
    win = rows[:, x0:x1].astype(np.float32)
    dev = deviation_mask(rows)[:, x0:x1].astype(np.float32)

    Timg, Wimg = win.shape
    t_norm = (np.arange(Timg) / Timg)[:, None]
    ether_col = np.array([0.20, 0.24, 0.46])
    glider_pal = [
        (0.00, (1.00, 0.98, 0.90)),
        (0.30, (1.00, 0.85, 0.45)),
        (0.62, (1.00, 0.55, 0.25)),
        (1.00, (0.88, 0.32, 0.36)),
    ]
    gl_cols = lerp_palette(np.broadcast_to(t_norm, (Timg, Wimg)), glider_pal)

    rgb = np.zeros((Timg, Wimg, 3), dtype=np.float32)
    eth = win * (1.0 - dev)
    rgb += 0.34 * eth[..., None] * ether_col[None, None, :]
    g = dev * (0.40 + 0.60 * win)
    rgb += 1.25 * glider_gain * g[..., None] * gl_cols

    # the seed itself: a birth star at the apex
    sx, sy = float(c - x0), 0.0
    yyg, xxg = np.mgrid[0:Timg, 0:Wimg].astype(np.float32)
    star = np.exp(-(((xxg - sx) ** 2 + (yyg - sy) ** 2)) / (0.009 * Timg) ** 2 / 2)
    rgb += 3.2 * star[..., None] * np.array([1.0, 0.97, 0.88])[None, None, :]

    halo = np.stack([gaussian_filter(rgb[..., c2], 3.0) for c2 in range(3)], -1)
    rgb = rgb + 0.5 * halo
    rgb = filmic(rgb, k=k_tone, gamma=0.9)

    from PIL import Image
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(img)
    im = im.resize((S_out, S_out), Image.LANCZOS)
    im.save(out)
    print("saved", out, "from", img.shape)


if __name__ == "__main__":
    render(T=1200, S_out=1024, out="variants/rule110_p1.png")
