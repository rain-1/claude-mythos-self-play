#!/usr/bin/env python3
"""Finalize piece 3: inset t(x,y,9) table + annotation block."""
import numpy as np
from PIL import Image, ImageDraw
from annot import annotate, fonts

img = Image.open("mesh_main_nolabel.png").convert("RGB")
W, H = img.size

# ---- inset: the poster's t(x,y,9) table from our verified DP ----
g = np.load("mesh_g_200.npy") if __import__("os").path.exists("mesh_g_200.npy") else None
if g is None:
    from mesh_small import solve
    g = solve(40)
K = 25
cell = 13
pad = 10
iw = K*cell + 2*pad
inset = Image.new("RGB", (iw, iw), (6, 8, 14))
di = ImageDraw.Draw(inset)
vmax = int(g[:K, :K, 9].max())
def rampc(t):
    stops = [(255,238,158),(255,184,71),(89,140,153),(31,71,133),(13,26,71)]
    pos = [0.0, 0.22, 0.55, 0.8, 1.0]
    for i in range(4):
        if t <= pos[i+1]:
            f = (t - pos[i])/(pos[i+1]-pos[i])
            return tuple(int(stops[i][k]+(stops[i+1][k]-stops[i][k])*f) for k in range(3))
    return stops[-1]
for x in range(K):
    for y in range(K):
        v = int(g[x, y, 9])
        c = rampc(v/vmax)
        di.rectangle([pad+y*cell, pad+x*cell, pad+(y+1)*cell-2, pad+(x+1)*cell-2], fill=c)
# paste bottom-right with border
bx, by = W - iw - 84, H - iw - 84
img.paste(inset, (bx, by))
d = ImageDraw.Draw(img)
d.rectangle([bx-2, by-2, bx+iw+1, by+iw+1], outline=(120, 130, 150), width=2)
F = fonts(1.0)
d.text((bx, by - 34), "t(x,y,9), x,y=0..24 — the poster's table",
       font=F["mono_s"], fill=(140, 148, 168))

annotate(img,
    "THE MESH, RESOLVED",
    ["An impartial game: three piles; take any amounts from exactly two.",
     "Its Grundy value has a closed form — each level set a glass pane:",
     "t(x,y,z) = min( x+y,  y+z,  z+x,  ⌊(x+y+z)/2⌋ )"],
    ["shells v = 3..43: hexagonal-medial plate  ⌊s/2⌋ regime  +  three 45° curtains  (dominant-pile regime)",
     "gold seams: where the two regimes glue — the truncation the poster saw at 45°",
     "proved by induction (every move strictly lowers f; all lower values reachable);",
     "verified: formula ≡ full DP on 200³ = 8,000,000 states; reachability lemma exhaustive to 30³",
     "MO question 514559 (“Closed form for the nimbers of this mesh game?”) — answered here",
     "the axes glow faint: the only positions worth exactly nothing — two piles already empty"],
    margin=84)
img.save("mesh25_2560.png")
print("saved mesh25_2560.png")
