"""THE PICKET FENCE - AP-obstruction atlas piece 39: Z[sqrt2].  2560^2.
Log-embedding country: horizontal = position along hyperbola (log boost), vertical = ln n.
S elements = strata; integer points = beads spaced by the regulator; record equal-gap runs = gold fences;
right panel: fence census + the empty l=6 channel + the 24|g theorem."""
import numpy as np, sys
import artlib as A

PREVIEW = len(sys.argv)>1 and sys.argv[1]=='preview'
FINAL = 1024 if PREVIEW else 2560
SS = 1 if PREVIEW else 2
S = FINAL*SS
rs = S/5120.0
rng = np.random.default_rng(39)

# ---- membership sieve to NMAX --------------------------------------------
NMAX = 3000
good = np.ones(NMAX+1, bool); good[0]=False
for p in range(2, NMAX+1):
    # primality by trial division fine at this scale
    if any(p % q == 0 for q in range(2, int(p**0.5)+1)): continue
    if p % 8 in (3,5):
        for j in range(p, NMAX+1, p):
            n = j; v = 0
            while n % p == 0: n //= p; v += 1
            if v % 2: good[j] = False
Sset = np.nonzero(good)[0]

# ---- layout ---------------------------------------------------------------
# main field box
fx0, fx1 = 0.05*S, 0.655*S
fy0, fy1 = 0.075*S, 0.93*S
ln_lo, ln_hi = np.log(2)-0.15, np.log(NMAX)
XI = 13.0     # horizontal half-range of xi-zeta = log boost
def ypos(n): return fy1 - (np.log(n)-ln_lo)/(ln_hi-ln_lo)*(fy1-fy0)
def xpos(b): return (fx0+fx1)/2 + b/(2*XI)*(fx1-fx0)

buf = A.canvas(S)
GOLD  = np.array([1.00, 0.80, 0.38])
STEEL = np.array([0.42, 0.62, 0.88])
CYANB = np.array([0.55, 0.85, 1.00])
ICE   = np.array([0.62, 0.80, 1.00])
EMBER = np.array([1.00, 0.45, 0.28])

runs = {3:(7,1), 4:(223,1), 5:(574,1)}   # first (start, gap)
run_ns = {n for l,(st,g) in runs.items() for n in range(st, st+l*g, g)}

# strata lines
for n in Sset:
    if n < 2: continue
    y = ypos(n)
    isrec = n in run_ns
    col = GOLD if isrec else STEEL
    amp = (2.6 if isrec else 0.55/(1+n/150)) * rs
    A.polyline(buf, np.array([[fx0, y],[fx1, y]]), col, amp=amp, step=1.2)

# beads: integer points |x^2-2y^2|=n<=NMAX, position b = ln((x+y*sqrt2)/|x-y*sqrt2|)
s2 = np.sqrt(2.0)
pts = []
for y in range(0, 4000):
    xc = y*s2
    xlo = max(1, int(xc - NMAX/(2*max(xc,1))) - 2); xhi = int(np.sqrt(NMAX + 2*y*y)) + 1
    xs = np.arange(xlo, xhi+1)
    nn = np.abs(xs*xs - 2*y*y)
    ok = (nn >= 2) & (nn <= NMAX)
    for x, n in zip(xs[ok], nn[ok]):
        if not good[n]: continue
        w = x + y*s2; z = abs(x - y*s2)
        if z < 1e-12: continue
        b = np.log(w/z)/1.0
        if abs(b) <= 2*XI:
            pts.append((b, n)); pts.append((-b, n))
pts = np.array(pts)
for b, n in pts:
    if abs(b) > XI: continue
    y = ypos(n); x = xpos(b)
    isrec = n in run_ns
    col = GOLD if isrec else CYANB
    fade = 1.0/(1.0 + n/420.0)
    A.star(buf, x, y, col, amp=(2.0 if isrec else 0.62*fade), rad=(2.6 if isrec else (1.15+0.8*fade))*rs*2)

# light-cone edge glow: left/right borders of field = the asymptote void
for xedge in (fx0, fx1):
    A.polyline(buf, np.array([[xedge, fy0],[xedge, fy1]]), ICE*0.6, amp=0.35*rs, step=1.2)

# ---- linear zoom inset: the l=5 fence and its broken 6th post -------------
ix0, ix1 = 0.705*S, 0.965*S
iy0, iy1 = 0.755*S, 0.885*S
A.polyline(buf, np.array([[ix0,iy0],[ix1,iy0],[ix1,iy1],[ix0,iy1]]), STEEL*0.8, amp=0.28*rs, closed=True)
lo, hi = 570, 585
for n in range(lo, hi+1):
    x = ix0 + (n-lo)/(hi-lo)*(ix1-ix0)
    if good[n]:
        col = GOLD if 574 <= n <= 578 else CYANB
        amp = 2.2 if 574 <= n <= 578 else 0.8
        A.polyline(buf, np.array([[x, iy0+0.30*(iy1-iy0)],[x, iy1-0.06*(iy1-iy0)]]), col, amp=amp*rs, step=1.0)
# ghost 6th post at 579 (not in S: 579=3*193, and 579 = 3 mod 8) - broken ice picket
x579 = ix0 + (579-lo)/(hi-lo)*(ix1-ix0)
yg0, yg1 = iy0+0.30*(iy1-iy0), iy1-0.06*(iy1-iy0)
for t0,t1 in [(0.0,0.25),(0.42,0.58),(0.80,1.0)]:
    A.polyline(buf, np.array([[x579, yg0+(yg1-yg0)*t0],[x579, yg0+(yg1-yg0)*t1]]), ICE, amp=0.7*rs, step=1.0)

# ---- right panel: fence census -------------------------------------------
px0, px1 = 0.705*S, 0.965*S
py0, py1 = 0.105*S, 0.475*S
counts = {3: 29231485, 4: 3172415, 5: 58590, 6: 0}
null6 = 7600.0
maxlog = np.log10(counts[3])
def cy(v):  # candle height by log10 count
    return py1 - (np.log10(max(v,0.7))/maxlog)*(py1-py0)*0.86
bw = (px1-px0)/4.6
for i, l in enumerate([3,4,5,6]):
    x = px0 + (i+0.5)*bw
    v = counts[l]
    if v > 0:
        y = cy(v)
        A.polyline(buf, np.array([[x, y],[x, py1]]), GOLD, amp=2.0*rs, step=1.0)
        A.star(buf, x, y, GOLD, amp=2.5, rad=3.2*rs*2)
    else:
        # empty channel exiting bottom: phantom expectation candle
        ye = cy(null6)
        for t0,t1 in [(0.0,0.12),(0.2,0.32),(0.4,0.52),(0.6,0.72),(0.8,0.92)]:
            yy0 = ye + (py1-ye)*t0; yy1 = ye + (py1-ye)*t1
            A.polyline(buf, np.array([[x, yy0],[x, yy1]]), ICE*0.8, amp=0.55*rs, step=1.0)
        A.star(buf, x, ye, ICE, amp=1.2, rad=2.6*rs*2)
A.polyline(buf, np.array([[px0, py1],[px1, py1]]), STEEL*0.7, amp=0.3*rs)

img = A.bloom(buf, sigmas=(2.0*rs*2, 8*rs*2, 26*rs*2), weights=(1.0, 0.38, 0.20))
img = A.tonemap(img, k=1.5, gamma=0.88)

tx = []
W = S
def T(x,y,s,size,col=(0.88,0.84,0.76),bold=False,anchor='la'): tx.append((x*W,y*W,s,int(size*rs*2),col,bold,anchor))
T(0.050, 0.022, "THE PICKET FENCE", 40, (1.0,0.87,0.55), True)
T(0.050, 0.049, "AP-obstruction atlas, piece 39 - Z[sqrt(2)], the country on the light cone", 19, (0.75,0.72,0.66))
T(0.050, 0.955, "|x^2-2y^2| censused to 4x10^9: 601,376,078 members - horizontal = log boost (units translate), height = ln n, beads = integer points", 14, (0.60,0.58,0.54))
T(0.835, 0.735, "the five-post fence 574..578, and the post that is not there (579 = 3*193)", 12.5, (0.85,0.75,0.5), anchor="ma")
T(0.835, 0.062, "fences by length", 18, (0.85,0.80,0.68), anchor='ma')
T(0.835, 0.082, "maximal equal-gap runs <= 4x10^9", 13, (0.62,0.60,0.56), anchor='ma')
for i,l in enumerate([3,4,5,6]):
    x = (px0 + (i+0.5)*bw)/W
    T(x, 0.482, f"l={l}", 15, (0.7,0.67,0.6), anchor='ma')
T((px0+3.5*bw)/W, cy(7600)/W-0.014, "iid ghost: ~7,600", 12, (0.62,0.78,0.95), anchor='ma')
T((px0+3.5*bw)/W, 0.452, "seen: 0", 14, (0.75,0.85,1.0), anchor='ma')
T(0.835, 0.545, "THEOREM (2-adic tower + p=3):", 15, (0.95,0.85,0.6), anchor='ma')
T(0.835, 0.565, "a six-post fence needs 24 | gap;", 14, (0.8,0.76,0.68), anchor='ma')
T(0.835, 0.583, "every other gap dies in the tower", 14, (0.8,0.76,0.68), anchor='ma')
T(0.835, 0.601, "(g=3 survives mod 8, dies mod 32)", 12, (0.65,0.62,0.58), anchor='ma')
T(0.835, 0.625, "6-term g=24 APs abound: 1,25,49,73,97,121", 12, (0.65,0.62,0.58), anchor='ma')
T(0.835, 0.643, "six consecutive: never below 4x10^9 (est >10^13)", 12, (0.65,0.62,0.58), anchor='ma')
img = A.bake_text(img, tx, S)
A.save(img, 'fence_preview.png' if PREVIEW else 'fence_2560.png', final=FINAL)
print("saved")
