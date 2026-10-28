"""The tile wall: certified ground states of 2x2 plaquette energies (MO 516372).
    python3 compose.py SIZE out.png
"""
import sys, json, colorsys, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "..")
from caption import caption, font, INK, CORAL
from wall import render_wall, noise_fields

SIZE = int(sys.argv[1]); out = sys.argv[2]
d = json.load(open("../math_ground/ground_states.json"))
ex = d["examples"]

CELL, PAN = 15, 13           # cell pitch in tiles, panel side
GX, GY = 4, 4
TX, TY = GX * CELL + 1, GY * CELL + 1
grid = np.full((TY, TX), -1, int)    # -1 = plain white field tile, 0/1 = state
gcol = np.zeros((TY, TX, 3)); coral = np.zeros((TY, TX), bool)

WHITE = np.array([0.975, 0.972, 0.955])
def sorbet(h, s=0.42, v=0.96):
    return np.array(colorsys.hsv_to_rgb(h % 1, s, v))

def state_patch(e, h, w, r0=0, c0=0):
    P = np.array(e["patch64"])
    return P[r0:r0 + h, c0:c0 + w]

# centre panel: the Gaussian period-21 staircase (rank 2), spans 2x2 cells
centre = ex[1]
cx0, cy0 = 1 * CELL + 1, 1 * CELL + 1
side = 2 * CELL - 1
P = np.array(centre["patch64"])[:side, :side]
grid[cy0:cy0 + side, cx0:cx0 + side] = P
# hue = phase of the site in the 21-cycle, r - 13 c (mod 21): the staircase shows as bands
pp, sh = centre["period"]["vertical_period_p"], centre["period"]["shear_s"]
gcol[cy0:cy0 + side, cx0:cx0 + side] = sorbet(0.66, 0.40, 0.97)
# the period lattice {a(21,0) + b(13,1)}: one site in 21 gets a coral dot
dots = np.zeros((TY, TX), bool)
for r in range(side):
    for c in range(side):
        if (r - sh * c - 3) % pp == 0: dots[cy0 + r, cx0 + c] = True
# coral frame ring one tile outside the centre panel
for i in range(cy0 - 1, cy0 + side + 1):
    for j in range(cx0 - 1, cx0 + side + 1):
        if i in (cy0 - 1, cy0 + side) or j in (cx0 - 1, cx0 + side):
            coral[i, j] = True

# other panels: skip the centre example, take the rest in order of interest; diverse areas
pick = [0, 2, 4, 5, 7, 11, 12, 14, 18, 20, 23, 25]
others = [ex[k] for k in pick]
cells = [(gx, gy) for gy in range(GY) for gx in range(GX) if not (1 <= gx <= 2 and 1 <= gy <= 2)]
# hue walks around the wall
for (gx, gy), e in zip(cells, others):
    x0, y0 = gx * CELL + 1, gy * CELL + 1
    P = state_patch(e, PAN, PAN)
    # make 1 the minority colour so the pattern reads as ink on white
    if P.mean() > 0.5: P = 1 - P
    grid[y0:y0 + PAN, x0:x0 + PAN] = P
    ang = np.arctan2(gy - 1.5, gx - 1.5) / (2 * np.pi)
    gcol[y0:y0 + PAN, x0:x0 + PAN] = sorbet(ang + 0.02, 0.40, 0.97)

colours = np.where((grid == 1)[..., None], gcol, WHITE)
# white tiles take a faint tint of their panel so panels read as panels
tint = np.where((grid == 0)[..., None], 1 - (1 - gcol) * 0.10, colours)
colours = np.where((grid == 0)[..., None], tint, colours)
colours[grid == -1] = np.nan
colours[coral] = np.array([0.98, 0.56, 0.48])

W = SIZE; band = int(W * 0.14)
H = W
Hw = H - band
T = Hw / (TY + 1.6)
oy = (Hw - TY * T) / 2; ox = (W - TX * T) / 2
win = {"rect": (-0.95, 0.05, -0.30, 1.05), "nx": 2, "ny": 3, "I": 0.9, "room": 0.09, "par": 1.4, "col": (1.0, 0.98, 0.95)}
noise = noise_fields(Hw, W)
img = np.zeros((Hw, W, 3), np.float32)
step = 512
for y0 in range(0, Hw, step):
    a, b = max(0, y0 - 4), min(Hw, y0 + step + 4)
    part = render_wall(Hw, W, TY, TX, colours, None, seed=11, tile_px=T, win=win, y0=a, y1=b, noise=noise,
                       ox=ox, oy=oy, dots=dots, grout=(0.93, 0.92, 0.915), plaster_col=(0.975, 0.965, 0.955))
    img[y0:min(Hw, y0 + step)] = part[y0 - a:y0 - a + min(step, Hw - y0)]
# daylight falloff from the window side (upper left)
yy, xx = np.mgrid[0:Hw, 0:W].astype(np.float32)
fall = 1.0 + 0.10 * (1 - xx / W) + 0.05 * (1 - yy / Hw)
img = img * fall[..., None]
img = img / (1 + img / 3.5) * 1.22
canvas = np.ones((H, W, 3), np.float32) * np.array([0.975, 0.975, 0.985])
canvas[:Hw] = np.clip(img, 0, 1)
im = Image.fromarray((canvas * 255 + 0.5).astype(np.uint8))
s = W / 4096
y = caption(im, int(ox + 20 * s), Hw + int(0.10 * band), int(2600 * s),
            "Twenty-One Rows Before It Repeats",
            "Every panel is a cheapest way to tile the plane when each 2×2 block has a price;\nthe framed one repeats only after 21 rows, sheared by 13: two Fibonacci numbers.",
            "tile = one site, coloured = 1 · coral dots = the period lattice (21,0), (13,1) · prices J random (centre: all 16 blocks, Gaussian)\neach panel certified a ground state: exact periodic optimum = 4×4-window LP lower bound · MathOverflow 516372",
            scale=s * 1.0, series="SOMETHING WE PROJECT ONTO IT  ·  IV")
# price list of the centre: the 16 2x2 tiles, ordered by their price J
dr = ImageDraw.Draw(im)
J = np.array(centre["J"]); order = np.argsort(J)
freq = np.array(centre["tile_frequencies"])
px0 = int(W - 1330 * s); py0 = Hw + int(0.30 * band); u = int(30 * s)
for k, t in enumerate(order):
    a_, b_, c_, d_ = t & 1, (t >> 1) & 1, (t >> 2) & 1, (t >> 3) & 1
    x = px0 + k * int(78 * s)
    used = freq[t] > 1e-9
    for (rr, cc), bit in zip([(0, 0), (0, 1), (1, 0), (1, 1)], [a_, b_, c_, d_]):
        col = tuple(int(255 * v) for v in (sorbet(0.66, 0.40) if bit else WHITE))
        dr.rounded_rectangle([x + cc * u, py0 + rr * u, x + cc * u + u - 3 * s, py0 + rr * u + u - 3 * s], radius=int(5 * s), fill=col,
                             outline=CORAL if used else (190, 180, 195), width=max(1, int((3 if used else 1.5) * s)))
    dr.text((x + 2 * s, py0 + 2 * u + 8 * s), f"{J[t]:+.2f}", font=font("reg", 22 * s), fill=INK)
dr.text((px0, py0 - 46 * s), "the centre's price list, cheapest first (coral = used by the ground state)", font=font("ital", 28 * s), fill=(128, 110, 136))
im.save(out)
print("saved", out, im.size)
