"""ATLAS 51 — THE WEATHER, IN DAYLIGHT (2560², first pastel register of the
residue-country series).

A musical-staff ledger of the window [3.0, 3.1]e12: one lane per channel
(g = 23, 24, 25).  Within each lane, FOUR faint guide lines = the gate
classes {94, 103, 110, 119} mod 144: every l>=4 run-start bead MUST sit on a
guide line (the gate is a theorem) — the empty paper between the lines is the
proof.  Fences (l>=5) are rose kites with stems; sextets (if any) deep ink
diamonds.  Verdict strip at the bottom, graded against the precommit.
"""
import numpy as np, json, sys
from PIL import Image, ImageDraw, ImageFont
from pastel import Watercolor, stroke_polyline
from scipy.ndimage import gaussian_filter

SS = 2
FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 2560
W = H = FINAL * SS
X0, X1 = 3.0e12, 3.1e12

res = json.load(open('atlas51_results.json'))
verdict = open('atlas51_verdict.txt').read().strip().splitlines()

# parse all OCC beads from alarms
AL = 'hunt_alarms_3000000000000_3100000000000.txt'
beads = {23: [], 24: [], 25: []}   # (start, l, cls)
for line in open(AL):
    p = line.split()
    if p and p[0] in ('OCC', 'L6+!'):
        l = int(p[1].split('=')[1]); g = int(p[2].split('=')[1])
        s = int(p[3].split('=')[1])
        if g in beads:
            beads[g].append((s, l, s % 144))

wc = Watercolor(H, W, seed=51)
GATE = [94, 103, 110, 119]
LANES = [(25, 'periwinkle', 0.16), (24, 'butter', 0.42), (23, 'seafoam', 0.68)]
lane_h = 0.20
mx0, mx1 = 0.06 * W, 0.97 * W

def xmap(s): return mx0 + (s - X0) / (X1 - X0) * (mx1 - mx0)

yy, xx = np.mgrid[0:H, 0:W]
for g, pig, ytop in LANES:
    y0, y1 = ytop * H, (ytop + lane_h) * H
    band = ((yy > y0) & (yy < y1)).astype(np.float32)
    fade = np.clip(1 - np.abs((yy - (y0 + y1) / 2) / ((y1 - y0) / 2)) ** 2.2, 0, 1)
    wc.wash(0.16 * band * fade, pig, granulate=0.22)
    # gate guide lines
    ink = np.zeros((H, W), np.float32)
    for gi, cls in enumerate(GATE):
        gy = y0 + (gi + 1) / (len(GATE) + 1) * (y1 - y0)
        stroke_polyline(ink, [(mx0, gy), (mx1, gy)], 0.7 * SS, amp=0.10)
    wc.wash(ink, 'graphite')
    # beads
    bead_f = np.zeros((H, W), np.float32)
    fence_f = np.zeros((H, W), np.float32)
    stem_f = np.zeros((H, W), np.float32)
    for s, l, cls in beads[g]:
        if cls not in GATE:      # gate violation -> draw OFF the lines, loud
            gy = y0 + 0.5 * (y1 - y0)
            r0 = 6 * SS
            d2 = (xx - xmap(s)) ** 2 + (yy - gy) ** 2
            fence_f += 6.0 * np.exp(-d2 / (2 * r0 ** 2))
            continue
        gi = GATE.index(cls)
        gy = y0 + (gi + 1) / (len(GATE) + 1) * (y1 - y0)
        px = xmap(s)
        if l == 4:
            r0 = 1.7 * SS
            x0i, x1i = int(px - 6 * r0), int(px + 6 * r0 + 1)
            y0i, y1i = int(gy - 6 * r0), int(gy + 6 * r0 + 1)
            if 0 <= x0i and x1i < W:
                d2 = (xx[y0i:y1i, x0i:x1i] - px) ** 2 + (yy[y0i:y1i, x0i:x1i] - gy) ** 2
                bead_f[y0i:y1i, x0i:x1i] += 1.5 * np.exp(-d2 / (2 * r0 ** 2))
        else:
            # fence: kite + stem to lane floor
            r0 = 3.4 * SS
            d2 = (xx - px) ** 2 + (yy - gy) ** 2
            fence_f += 3.2 * np.exp(-d2 / (2 * r0 ** 2))
            stroke_polyline(stem_f, [(px, gy), (px, y1 - 0.01 * H)], 0.9 * SS, amp=0.5)
    wc.wash(bead_f, 'ink')
    wc.wash(fence_f, 'rose')
    wc.wash(fence_f * 0.45, 'ink')
    wc.wash(stem_f, 'clay')
    # sextets in this lane (l>=6 beads drawn as diamonds = rotated squares)
    if g == 24:
        for s in res['sextets']['starts']:
            px = xmap(s)
            gy = y0 + 0.5 * (y1 - y0)
            dd = (np.abs(xx - px) + np.abs(yy - gy))
            wc.wash(4.0 * np.exp(-(dd / (4.5 * SS)) ** 2), 'ink')

# lane labels + axis
img = Image.new('L', (W, H), 0)
dr = ImageDraw.Draw(img)
try:
    f_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', int(0.025 * H))
    f_lab = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', int(0.011 * H))
    f_tiny = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', int(0.0085 * H))
except Exception:
    f_title = f_lab = f_tiny = ImageFont.load_default()
for g, pig, ytop in LANES:
    lab = {25: "channel 25 — the proved gate; fences must strike 94",
           24: "channel 24 — the loudening lane (sextets live here)",
           23: "channel 23 — count reported, no verdict (precommit rule)"}[g]
    dr.text((int(0.06 * W), int((ytop - 0.028) * H)), lab, fill=255, font=f_lab)
    for gi, cls in enumerate(GATE):
        gy = ytop * H + (gi + 1) / (len(GATE) + 1) * lane_h * H
        dr.text((int(0.017 * W), gy - 0.005 * H), f"≡{cls}", fill=255, font=f_tiny)
dr.text((int(0.06 * W), int(0.045 * H)), "Atlas 51 — The Weather, in Daylight", fill=255, font=f_title)
dr.text((int(0.06 * W), int(0.085 * H)),
        "runs of equal gaps among the norms of Z[sqrt(2)] integers, window 3.0–3.1 trillion; "
        "every bead is pinned to a guide line by a theorem", fill=255, font=f_lab)
# x axis ticks
for t in np.linspace(X0, X1, 6):
    px = xmap(t)
    dr.text((px - 0.012 * W, 0.925 * H), f"{t/1e12:.2f}e12", fill=255, font=f_tiny)
# verdict strip
for i, ln in enumerate(verdict[:5]):
    dr.text((int(0.06 * W), int((0.945 + 0.012 * i) * H)), ln[:230], fill=255, font=f_tiny)
tf = np.asarray(img, dtype=np.float32) / 255.0
wc.wash(2.0 * gaussian_filter(tf, 0.6 * SS), 'ink')

wc.save(f'atlas51_{FINAL}.png', final_size=(FINAL, FINAL), dmax=2.3)
print('saved atlas51', FINAL)
