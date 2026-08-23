#!/usr/bin/env python3
"""AP-obstruction atlas, piece 43: THE DOOR PAST THE GATE.
Five channels of Z[sqrt2] (equal-gap quintuple runs, gaps 14/17/24/23/25) as five
lanes of one hallway, each dark until its first fence. Channel 25's door was
predicted (piece 42, committed before the verdict) at median 6e11-1.2e12,
certified silent through 4.0e11 - and heard THIS RUN at 458,171,603,806."""
import numpy as np, math
import artlib as A

FINAL = 2560
SS = 2
S = FINAL*SS
rs = S/1024.0

GOLD = np.array([1.00, 0.76, 0.34])
GOLD_HI = np.array([1.00, 0.90, 0.62])
CYAN = np.array([0.30, 0.68, 0.95])
ICE = np.array([0.72, 0.86, 1.00])

FENCES = [  # (gap, first n, lane label)
    (14, 5341738436, "channel 14"),
    (17, 33099743774, "channel 17"),
    (24, 52909727729, "channel 24"),
    (23, 158783559650, "channel 23"),
    (25, 458171603806, "channel 25"),
]
LX0, LX1 = 9.55, 12.08          # log10 n range
SCAN_END = 8.8e11               # this run's relay target
GATE42 = 4.0e11

def xof(n):
    return 0.06*S + (math.log10(n)-LX0)/(LX1-LX0)*0.90*S

def main():
    img = A.canvas(S)
    lanes_y0 = 0.415*S; laneh = 0.098*S
    # prediction nebula for lane 25 (drawn first, under everything)
    y0 = lanes_y0 + 4*laneh  # lane 25 is top lane (index 4), but we draw bottom-up later
    # ---- lanes
    for li, (g, n1, name) in enumerate(FENCES):
        y_top = lanes_y0 + (4-li)*laneh
        y_bot = y_top + laneh*0.86
        yy0, yy1 = int(y_top), int(y_bot)
        xs = np.arange(S)
        # base: faint cold floor inside plotted x-range
        x_first = xof(10**LX0); x_last = xof(10**LX1)
        # after-door warm glow
        xd = xof(n1)
        m = (xs > xd) & (xs < xof(SCAN_END))
        fade = np.zeros(S)
        fade[m] = 0.14*np.exp(-(xs[m]-xd)/(0.22*S))+0.05
        for c in range(3):
            img[yy0:yy1, :, c] += fade[None, :]*GOLD[c]
        # pre-door: cold darkness with sparse ticks
        rng = np.random.default_rng(g)
        mpre = (xs > x_first) & (xs < xd)
        for c in range(3):
            img[yy0:yy1, mpre, c] += 0.016*np.array([0.5, 0.7, 1.0])[c]
        # unscanned region (lane 25 only extends visually)
        mun = xs > xof(SCAN_END)
        dash = ((xs//int(9*rs)) % 2 == 0) & mun & (xs < x_last)
        yc = (yy0+yy1)//2
        for c in range(3):
            img[yc-1:yc+2, dash, c] += 0.10*ICE[c]
        # the door
        bar = A.canvas(S)
        A.polyline(bar, np.array([[xd, y_top+2], [xd, y_bot-2]]), GOLD_HI, amp=3.2*rs**0.85*0.5)
        A.star(bar, xd, (y_top+y_bot)/2, GOLD_HI, amp=3.4*rs*rs*0.25, rad=4.2*rs*0.5)
        img += A.bloom(bar, sigmas=(1.6*rs*0.5, 7*rs*0.5), weights=(1.0, 0.4))
        # lane 25 extras: ice gate at 4e11 + prediction nebula + later fences
        if g == 25:
            for nf in (615709112638, 830595732286):
                xf = xof(nf)
                fb = A.canvas(S)
                A.polyline(fb, np.array([[xf, y_top+laneh*0.18], [xf, y_bot-laneh*0.10]]), GOLD, amp=2.0*rs**0.85*0.5)
                A.star(fb, xf, (y_top+y_bot)/2, GOLD, amp=1.8*rs*rs*0.25, rad=3.0*rs*0.5)
                img += A.bloom(fb, sigmas=(1.5*rs*0.5, 6*rs*0.5), weights=(1.0, 0.35))
            xg = xof(GATE42)
            gate = A.canvas(S)
            A.polyline(gate, np.array([[xg, y_top-0.012*S], [xg, y_bot+0.012*S]]), ICE, amp=2.2*rs**0.85*0.5)
            img += A.bloom(gate, sigmas=(2.4*rs*0.5, 10*rs*0.5), weights=(0.9, 0.5))
            # nebula: 10%-quantile band 1.2e11-2.4e11 faint; median band 6e11-1.2e12 brighter
            for (a, b, w) in [(1.2e11, 2.4e11, 0.055), (6e11, 1.2e12, 0.17)]:
                xa, xb = xof(a), min(xof(b), 0.985*S)
                mm = (xs > xa) & (xs < xb)
                prof = np.sin(np.pi*(xs[mm]-xa)/max(xb-xa, 1))**1.2
                for c in range(3):
                    img[yy0:yy1, mm, c] += w*prof[None, :]*CYAN[c]
    # ---- axis ticks (decades)
    axb = A.canvas(S)
    ytick = lanes_y0 + 5*laneh + 0.012*S
    for e in [10, 11, 12]:
        x = xof(10.0**e)
        A.polyline(axb, np.array([[x, ytick], [x, ytick+0.014*S]]), np.array([0.7, 0.75, 0.85]), amp=1.6*rs**0.85*0.5)
    img += A.bloom(axb, sigmas=(1.2*rs*0.5,), weights=(1.0,))
    # ---- the five candles (top inset)
    cx0, cy_base = 0.315*S, 0.315*S
    step = 0.075*S
    membs = [("2 - 7^2 - 41 - 114029767", True), ("prime", True), ("2^4 - 3^2 - 3181747249", True),
             ("prime", True), ("2 - 17 - 47 - 286715647", True)]
    cnd = A.canvas(S)
    for k in range(-1, 6):
        x = cx0 + (k+1)*step
        if 0 <= k <= 4:
            h = 0.155*S
            A.polyline(cnd, np.array([[x, cy_base], [x, cy_base-h]]), GOLD, amp=2.6*rs**0.85*0.5)
            A.star(cnd, x, cy_base-h, GOLD_HI, amp=2.6*rs*rs*0.25, rad=3.4*rs*0.5)
        else:
            h = 0.045*S
            A.polyline(cnd, np.array([[x, cy_base], [x, cy_base-h]]), np.array([0.35, 0.42, 0.55]), amp=1.8*rs**0.85*0.5)
    A.polyline(cnd, np.array([[cx0-0.5*step, cy_base+0.004*S], [cx0+6.5*step, cy_base+0.004*S]]),
               np.array([0.55, 0.60, 0.70]), amp=1.4*rs**0.85*0.5)
    img += A.bloom(cnd, sigmas=(1.5*rs*0.5, 7*rs*0.5), weights=(1.0, 0.35))
    out = A.tonemap(img, k=1.5, gamma=0.95)
    # ---- text
    F = FINAL
    small = np.asarray(A.save(out, '/tmp/tmp_atlas.png', final=F)).astype(np.float32)/255.0
    GOLDt = (1.0, 0.86, 0.55); GREY = (0.62, 0.66, 0.72); CYANt = (0.55, 0.78, 0.95); ICEt = (0.78, 0.88, 1.0)
    texts = [
      (0.030*F, 0.020*F, "THE DOOR PAST THE GATE", int(0.0205*F), GOLDt, True, 'ls'),
      (0.970*F, 0.016*F, "AP-OBSTRUCTION ATLAS - PIECE 43", int(0.0112*F), CYANt, True, 'rs'),
      (0.970*F, 0.0315*F, "Z[sqrt2]: n whose primes p = +-3 (mod 8) divide to even powers", int(0.0088*F), GREY, False, 'rs'),
      (0.030*F, 0.040*F, "five channels = five gaps g: the first maximal quintuple n, n+g, ..., n+4g all norms of Z[sqrt2] - each lane dark until its door opens", int(0.0090*F), GREY, False, 'ls'),
      (0.030*F, 0.054*F, "piece 40 heard 14 - piece 41 heard 17, 24, 23 and certified 25 silent to 1.6e11 - piece 42 built the gate (l=5 gap-25 forces start = 94 mod 144), certified silence to 4.0e11, and COMMITTED the prediction", int(0.0088*F), GREY, False, 'ls'),
      (0.030*F, 0.068*F, "P(silent through 4e11) = 65-80% (it was) - median first fence 6e11..1.2e12 - 10% quantile 1.2e11..2.4e11", int(0.0088*F), CYANt, False, 'ls'),
      (0.055*F, 0.105*F, "this run's relay [4.0e11 -> 8.8e11) heard it almost at once - and then the channel kept talking:", int(0.0100*F), GOLDt, False, 'ls'),
      (0.055*F, 0.122*F, "n = 458,171,603,806 = 94 (mod 144), exactly as the gate demanded - then 615,709,112,638 and 830,595,732,286 (both = 94 mod 144), and a fourth beyond 8.3e11", int(0.0100*F), GOLDt, True, 'ls'),
      # candle labels
      (0.315*F, 0.330*F, "n\n2 - 7^2 - 41\n- 114029767", int(0.0068*F), GREY, False, 'ms'),
      (0.3525*F, 0.330*F, "n+25\nprime", int(0.0068*F), GREY, False, 'ms'),
      (0.390*F, 0.330*F, "n+50\n2^4 - 3^2\n- 3181747249", int(0.0068*F), GREY, False, 'ms'),
      (0.4275*F, 0.330*F, "n+75\nprime", int(0.0068*F), GREY, False, 'ms'),
      (0.465*F, 0.330*F, "n+100\n2 - 17 - 47\n- 286715647", int(0.0068*F), GREY, False, 'ms'),
      (0.2775*F, 0.330*F, "n-25\n3 - ...", int(0.0068*F), (0.4, 0.45, 0.55), False, 'ms'),
      (0.5025*F, 0.330*F, "n+125\n3 - ...", int(0.0068*F), (0.4, 0.45, 0.55), False, 'ms'),
      (0.39*F, 0.372*F, "the five candles - verified by full factorisation; maximal on both sides (both flanks fall to a single 3)", int(0.0080*F), GREY, False, 'ms'),
      # lane labels + fence values
      (0.965*F, 0.4335*F, "gap 25 - 458,171,603,806   THIS RUN", int(0.0088*F), GOLDt, True, 'rs'),
      (0.965*F, 0.5315*F, "gap 23 - 158,783,559,650", int(0.0088*F), GREY, False, 'rs'),
      (0.965*F, 0.6295*F, "gap 24 - 52,909,727,729", int(0.0088*F), GREY, False, 'rs'),
      (0.965*F, 0.7275*F, "gap 17 - 33,099,743,774", int(0.0088*F), GREY, False, 'rs'),
      (0.965*F, 0.8255*F, "gap 14 - 5,341,738,436", int(0.0088*F), GREY, False, 'rs'),
      # axis
      (0.06*F, 0.935*F, "n (log scale)", int(0.0082*F), GREY, False, 'ls'),
      (0.365*F, 0.935*F, "1e10", int(0.0082*F), GREY, False, 'ms'),
      (0.72*F, 0.935*F, "1e11", int(0.0082*F), GREY, False, 'ms'),
      (0.955*F, 0.935*F, "1e12", int(0.0082*F), GREY, False, 'rs'),
      (0.030*F, 0.958*F, "ice wall: piece 42's certified frontier (4.0e11) - cyan haze: the committed prediction bands - dashes: the still-unscanned dark - drift confirmed again: l4/l3 for gap 25 rose 1.78e-3, 1.98e-3, 2.49e-3, now 2.53e-3 in [4e11, 5.6e11)", int(0.0084*F), GREY, False, 'ls'),
      (0.030*F, 0.9715*F, "the whole relay [4.0e11, 8.8e11): 63,534,246,948 members - gap-25 runs: 395,647 triples, 1,036 quadruples, FOUR quintuples - every verified start = 94 (mod 144); drift r34 rose 2.53, 2.59, 2.73 e-3 across the chunks", int(0.0084*F), GREY, False, 'ls'),
    ]
    outb = A.bake_text(small, texts, F)
    A.save(outb, 'atlas43_final.png', final=None, dither=False)
    print("saved atlas43_final.png")

if __name__ == '__main__':
    main()
