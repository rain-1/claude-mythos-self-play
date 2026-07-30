"""THE THOUSAND DOORS  (hero, 4096x4096)

One column per odd shift s in [-999, 999]: the door  t + s,  t = 2^^inf.
Column height = ln ln (first prime key)  -- the climb the sieve made
before some prime divided t+s.  A gold star crowns each opened door;
fainter violet ghosts above it are the later keys that arrived after
the question was already closed.  Doors with NO key below 1e10 are cold
channels that burn straight through the top of the frame: the open
questions.  Door +1 is sealed by theorem (no prime can ever divide t+1):
white ice.  Door +3 is the MO 479419 question, open past 6e15: crimson.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_common import *
from PIL import Image, ImageDraw

PROTO = int(os.environ.get('PROTO', '0'))
FINAL = 1024 if PROTO else 4096
SS = 1 if PROTO else 2
S = FINAL * SS
rs = S / 2048.0

census = {int(k): v for k, v in json.load(open(SC + 'census.json')).items()}
DOORS = sorted(census.keys())            # -999 .. 999 odd
ND = len(DOORS)
B = 1e10

# ---- layout ----
MX = int(0.030 * S)                       # side margins
FOOT = int(0.070 * S)                     # footer band
TOPM = int(0.045 * S)
x_of = lambda i: MX + (i + 0.5) * (S - 2 * MX) / ND
LLmin, LLmax = np.log(np.log(3.0)) - 0.06, np.log(np.log(B))
y_base = S - FOOT - int(0.020 * S)
y_top = TOPM + int(0.055 * S)            # y of lnln(B) shoreline
def y_of(p):
    ll = np.log(np.log(float(p)))
    return y_base - (ll - LLmin) / (LLmax - LLmin) * (y_base - y_top)

# ---- palettes ----
EMBER = [(0.28, 0.045, 0.02), (0.75, 0.22, 0.045), (1.00, 0.55, 0.12), (1.00, 0.86, 0.42)]
GOLD = (1.00, 0.80, 0.34)
GHOST = (0.42, 0.30, 0.75)
COLD = (0.16, 0.38, 0.85)
CYAN = (0.35, 0.85, 1.00)
ICE = (0.80, 0.95, 1.00)
CRIM = (1.00, 0.16, 0.22)

buf = canvas(S, S)

# faint ladder rules at p = 10^2,10^4,10^6,10^8,10^10
for pe in [1e2, 1e4, 1e6, 1e8, 1e10]:
    yy = int(y_of(pe))
    buf[yy:yy + max(1, int(1 * rs)), MX:S - MX] += np.array([0.05, 0.055, 0.075], np.float32) * (0.7 if pe < 1e10 else 1.6)

colw = (S - 2 * MX) / ND
rng = np.random.default_rng(11)

shut = [s for s in DOORS if not census[s]]
for i, s in enumerate(DOORS):
    x = x_of(i)
    keys = census[s]
    if s == 1:
        # sealed by theorem: full ice column, brightest, hard crystal
        n = int(y_base - y_top)
        g = np.linspace(0, 1, n).astype(np.float32)
        amp = (0.55 + 0.9 * g ** 1.3) * 0.95
        vline(buf, x, y_base, y_top, ICE, amp, colw * 0.66)
        vline(buf, x, y_top, TOPM - int(0.02 * S), ICE, 1.6, colw * 0.66)
        splat_points(buf, [x], [y_top], ICE, [3.0], 2.4 * rs)
        continue
    if not keys:
        # unknown door: cold channel burning past the frame top
        n = int(y_base - y_top)
        g = np.linspace(0, 1, n).astype(np.float32)     # 0 at bottom
        amp = 0.055 + 0.9 * g ** 3.0
        col = (0.10, 0.30, 0.62) if s != 3 else lerp((0.10, 0.30, 0.62), CRIM, 0.62)
        vline(buf, x, y_base, y_top, col, amp * 0.62, colw * 0.55)
        # beyond the shoreline: it keeps going, brighter, out the top
        vline(buf, x, y_top, -int(0.01 * S), lerp(col, CYAN if s != 3 else CRIM, 0.35), 1.05, colw * 0.55)
        splat_points(buf, [x], [y_top], CYAN if s != 3 else CRIM, [2.4 if s != 3 else 3.2],
                     (2.2 if s != 3 else 2.6) * rs)
        if s == 3:
            splat_points(buf, [x], [int(0.55 * y_top)], CRIM, [1.1], 7.0 * rs)
        continue
    p1 = keys[0]
    yk = y_of(p1)
    h01 = (np.log(np.log(p1)) - LLmin) / (LLmax - LLmin)   # 0..1 climb height
    ccol = ramp(EMBER, 0.25 + 0.75 * h01)
    n = max(2, int(y_base - yk))
    g = np.linspace(0, 1, n).astype(np.float32)
    amp = (0.22 + 0.95 * g ** 1.7) * (0.40 + 0.85 * h01)
    vline(buf, x, y_base, yk, ccol, amp * 1.15, colw * 0.68)
    # crown star
    splat_points(buf, [x], [yk], GOLD, [0.8 + 3.4 * h01 ** 1.5], (1.3 + 1.6 * h01) * rs)
    # ghost keys above the crown (answers after the fact)
    for p2 in keys[1:26]:
        splat_points(buf, [x], [y_of(p2)], GHOST, [0.17], 0.9 * rs)

# shoreline label strip: subtle glow along y_top
buf[int(y_top):int(y_top + 1.8 * rs), MX:S - MX] += np.array([0.14, 0.17, 0.26], np.float32)
# void haze above the shoreline (beyond the census)
nvh = int(y_top)
vh = (np.linspace(1.0, 0.0, nvh) ** 2.0 * 0.045)[:, None, None]
buf[:nvh, MX:S - MX] += vh * np.array([0.25, 0.38, 0.70], np.float32)

buf = bloom(buf, 10 * rs, 0.55, thresh=0.50)
buf = bloom(buf, 42 * rs, 0.30, thresh=0.62)
img = tonemap(buf, k=1.35, gamma=0.84)

# ---- footer text ----
im = Image.fromarray((img * 255).astype(np.uint8))
dr = ImageDraw.Draw(im)
f1 = font(int(0.0135 * S), bold=True)
f2 = font(int(0.0088 * S))
f3 = font(int(0.0072 * S))
ty = S - FOOT + int(0.008 * S)
dr.text((MX, ty), "THE THOUSAND DOORS", font=f1, fill=(235, 225, 205))
sub = ("t = 2↑↑2↑↑2↑↑⋯  frozen in the profinite integers — one column per door t+s, odd |s| ≤ 999 · "
       "column height = ln ln (smallest prime key), census of all 455,052,511 primes ≤ 10¹⁰")
dr.text((MX, ty + int(0.0195 * S)), sub, font=f2, fill=(150, 148, 158))
sub2 = ("%d doors opened · %d still shut (cold channels) · door +1 sealed forever by the 2-adic theorem (ice) · "
        "door +3 is MO 479419: no key below 6×10¹⁵ (crimson)" % (ND - len(shut), len(shut) - 1))
dr.text((MX, ty + int(0.0335 * S)), sub2, font=f3, fill=(120, 118, 130))
# axis ticks
for pe, lab in [(1e2, "10²"), (1e4, "10⁴"), (1e6, "10⁶"), (1e8, "10⁸"), (1e10, "10¹⁰")]:
    dr.text((int(0.004 * S), int(y_of(pe)) - int(0.006 * S)), lab, font=f3, fill=(105, 108, 125))
# door +3 tick at bottom
i3 = DOORS.index(3)
dr.text((x_of(i3) - int(0.004 * S), y_base + int(0.002 * S)), "+3", font=f3, fill=(220, 80, 90))
for sN, tag in [(51, "+51"), (235, "+235"), (-333, "−333")]:
    iN = DOORS.index(sN)
    pN = census[sN][0]
    dr.text((x_of(iN) - int(0.007 * S), y_of(pN) - int(0.016 * S)), tag, font=f3, fill=(230, 190, 120))

im = im.resize((FINAL, FINAL), Image.LANCZOS) if im.size != (FINAL, FINAL) else im
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'thousand_doors_proto.png' if PROTO else 'thousand_doors.png')
im.save(out, optimize=True)
print("saved", out, im.size)
