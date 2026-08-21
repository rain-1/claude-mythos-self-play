#!/usr/bin/env python3
"""THE ETERNAL ROUND — full retrograde solution of the schoolyard game
(MO 514521).  The draw-sea: 624 states that circle forever, woven by their
draw-preserving moves; the tactical reefs: mate-in-1/2/3 states in warm and
violet; the 60 corpse-states beyond; the symmetric start, a gold star that
never has to fall.
"""
import numpy as np, json, sys
from collections import deque
import artlib

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 1280
SS   = int(sys.argv[2]) if len(sys.argv) > 2 else 1
OUT  = sys.argv[3] if len(sys.argv) > 3 else 'round_prev.png'
S = SIZE*SS
rs = S/2560.0

D = json.load(open('chop_data.json'))
states = [((tuple(s[0][0:2])), tuple(s[1][0:2]), s[2], s[3]) for s in
          [[tuple(x[0]), tuple(x[1]), x[2], x[3]] for x in D['states']]]
states = [(tuple(s[0]), tuple(s[1]), s[2], s[3]) for s in states]
val = D['val']; depth = D['depth']; succ = D['succ']; start = D['start']
N = len(states)

# reachable set from start
reach = set([start]); q = deque([start])
while q:
    i = q.popleft()
    for j in succ[i]:
        if j not in reach: reach.add(j); q.append(j)
print("reachable states from start:", len(reach),
      " draws:", sum(1 for i in reach if val[i]==0),
      " W:", sum(1 for i in reach if val[i]==1),
      " L:", sum(1 for i in reach if val[i]==-1))

# ---------------- layout ----------------
hands_list = sorted(set(s[0] for s in states))          # 15 hand-multisets
house = {h:k for k,h in enumerate(hands_list)}
cx, cy = 0.5*S, 0.485*S
ring_r = {(0,0): 0.130, (0,1): 0.185, (1,0): 0.240, (1,1): 0.295}
R_W = {1: 0.405, 2: 0.372, 3: 0.345}
R_L = {0: 0.478, 2: 0.440}
GOLD  = np.array([1.00, 0.80, 0.32])
ICE   = np.array([0.55, 0.80, 1.00])
ICE2  = np.array([0.40, 0.62, 0.92])
EMBER = np.array([1.00, 0.46, 0.18])
VIOL  = np.array([0.70, 0.40, 1.00])
ASH   = np.array([0.55, 0.58, 0.66])

rng = np.random.default_rng(3)
pos = {}
for i,(m,o,mcd,ocd) in enumerate(states):
    hm, ho = house[m], house[o]
    base = 2*np.pi*(((hm + ho) % 15)/15.0) + (2*np.pi/15.0)*(((hm - ho) % 15 + 0.5)/15.0)
    if val[i] == 0:
        r = ring_r[(mcd,ocd)]
    elif val[i] == 1:
        r = R_W[depth[i]] + 0.010*np.sin(7*base)
    else:
        r = R_L.get(depth[i], 0.49) + 0.010*np.cos(5*base)
    r *= S
    pos[i] = (cx + r*np.cos(base - np.pi/2), cy + r*np.sin(base - np.pi/2))

buf = artlib.canvas(S)

def arc_pts(p0, p1, bow=0.18, n=None):
    # polar interpolation around (cx,cy): threads flow along their annulus
    a0 = np.arctan2(p0[1]-cy, p0[0]-cx); a1 = np.arctan2(p1[1]-cy, p1[0]-cx)
    r0 = np.hypot(p0[0]-cx, p0[1]-cy);   r1 = np.hypot(p1[0]-cx, p1[1]-cy)
    da = (a1 - a0 + np.pi) % (2*np.pi) - np.pi
    if n is None: n = max(10, int(abs(da)*max(r0,r1)/ (2.2*rs) ))
    t = np.linspace(0, 1, n)
    te = t*t*(3-2*t)
    aa = a0 + da*t
    rrr = r0 + (r1-r0)*te + bow*0.10*max(r0,r1)*np.sin(np.pi*t)*np.sign(r1-r0+1e-9)
    return np.stack([cx + rrr*np.cos(aa), cy + rrr*np.sin(aa)], 1)

# ---------------- draw-sea web ----------------
for i in range(N):
    if val[i] != 0: continue
    for j in succ[i]:
        if val[j] != 0: continue
        amp = 0.030*rs * (1.6 if (i in reach and j in reach) else 0.35)
        cc = ICE if (i in reach and j in reach) else ICE2*0.45
        artlib.polyline(buf, arc_pts(pos[i], pos[j]), cc, amp=amp, step=0.8)
# draw nodes
for i in range(N):
    if val[i] != 0: continue
    x,y = pos[i]
    b = 1.8 if i in reach else 0.45
    artlib.star(buf, x, y, ICE, amp=0.30*rs*rs*b, rad=2.2*rs)

# ---------------- tactical reefs ----------------
for i in range(N):
    if val[i] == 0: continue
    x,y = pos[i]
    if val[i] == 1:
        cc = EMBER if depth[i] == 1 else EMBER*0.6 + GOLD*0.4
        # winning move thread: to the L child of minimal depth (or the kill)
        best = None
        for j in succ[i]:
            if val[j] == -1 and (best is None or depth[j] < depth[best]): best = j
        if best is not None:
            artlib.polyline(buf, arc_pts(pos[i], pos[best], bow=0.10), cc*0.60, amp=0.10*rs, step=0.8)
        artlib.star(buf, x, y, cc, amp=1.9*rs*rs, rad=3.6*rs)
    else:
        cc = VIOL
        for j in succ[i]:      # all escapes lead to winning opponents
            if val[j] == 1:
                artlib.polyline(buf, arc_pts(pos[i], pos[j], bow=0.08), VIOL*0.35, amp=0.05*rs, step=0.9)
        artlib.star(buf, x, y, cc, amp=2.1*rs*rs, rad=3.8*rs)

# corpses ring: states with m=(0,0) (val -1 depth 0)
for i in range(N):
    m,o,mcd,ocd = states[i]
    if m == (0,0):
        x,y = pos[i]
        artlib.star(buf, x, y, np.array([0.95,0.22,0.28]), amp=2.6*rs*rs, rad=4.6*rs)

# ---------------- the start ----------------
sx, sy = pos[start]
artlib.star(buf, sx, sy, GOLD, amp=13.0*rs*rs, rad=11.0*rs)
for j in succ[start]:
    artlib.polyline(buf, arc_pts(pos[start], pos[j], bow=0.22), GOLD*0.9, amp=0.30*rs, step=0.7)

# reef guide circles
th = np.linspace(0, 2*np.pi, 720)
for rr_, cc_ in ((0.345,'w'),(0.372,'w'),(0.405,'w'),(0.440,'l'),(0.478,'c')):
    col = {'w': EMBER*0.40, 'l': VIOL*0.40, 'c': np.array([0.95,0.22,0.28])*0.38}[cc_]
    artlib.polyline(buf, np.stack([cx + rr_*S*np.cos(th), cy + rr_*S*np.sin(th)],1), col, amp=0.012*rs, step=1.0)

# house spokes (faint)
for k in range(15):
    a = 2*np.pi*k/15.0 - np.pi/2
    p0 = (cx + 0.10*S*np.cos(a), cy + 0.10*S*np.sin(a))
    p1 = (cx + 0.545*S*np.cos(a), cy + 0.545*S*np.sin(a))
    artlib.polyline(buf, np.array([p0,p1]), ASH*0.16, amp=0.012*rs, step=1.0)

artlib.bloom(buf, sigmas=(2*max(rs,0.5), 9*rs, 30*rs), weights=(1.0, 0.30, 0.14))
img = artlib.tonemap(buf, k=1.4, gamma=0.93)
if SS > 1:
    from PIL import Image
    im = Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).resize((SIZE,SIZE), Image.LANCZOS)
    img = np.asarray(im).astype(np.float32)/255.0
F = SIZE
nreach = len(reach)
texts = [
 (F*0.5, F*0.040, "T H E   E T E R N A L   R O U N D", int(F*0.021), (0.93,0.90,0.82), True, 'mm'),
 (F*0.5, F*0.068, "a schoolyard game, solved to the bone — two hands each, attacks add mod 5, a split that must rest a turn · MathOverflow 514521", int(F*0.0090), (0.62,0.63,0.68), False, 'mm'),
 (F*0.5, F*0.905, "the verdict: from the symmetric start ((1,1),(1,1)) the game is a DRAW — under every reading of the rules (cooldown, no cooldown, no-revival) optimal play circles forever", int(F*0.0078), (0.75,0.77,0.82), False, 'mm'),
 (F*0.5, F*0.923, f"900 positions: 624 eternal draws (ice web, rings = the four cooldown constellations), 164 wins and 112 losses (warm and violet reefs), 60 corpses (crimson) · the deepest tactic in the whole game is mate-in-3", int(F*0.0072), (0.58,0.60,0.66), False, 'mm'),
 (F*0.5, F*0.941, f"gold star = the start; its three moves all keep the draw · {nreach} positions are reachable from it (bright ice), the rest of the sea (dim) exists only beyond perfect play", int(F*0.0072), (0.58,0.60,0.66), False, 'mm'),
 (F*0.5, F*0.959, "the one game where symmetry keeps its promise: what begins level, stays level — nobody can be made to fall", int(F*0.0072), (0.72,0.66,0.50), False, 'mm'),
]
img = artlib.bake_text(img, texts, F)
artlib.save(img, OUT)
print("saved", OUT)
