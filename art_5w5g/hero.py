"""
hero.py — THE COURTS OF PERFECT FIT (4096²)

Center: the richest certified perfect fit (the court that skipped five).
Orbit: every certified rigid court from the exact census.
Underworld: the ghost courts — rings that close exactly in angle but whose
coins overlap; the only courts that ever hold a 1/5 coin. Their wounds
glow cyan. Above, in the world of the real, no cyan exists.

Usage: python3 hero.py [proto]
"""

import json
import math
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from engine import ring_positions, is_rigid
from render import (Canvas, draw_court, draw_ghost_court, draw_ring, glow,
                    soddy_fill, bloom, to_img, GHOST, PAL, WOUND, splat_points)

PROTO = len(sys.argv) > 1 and sys.argv[1] == "proto"
FINAL = 1280 if PROTO else 4096
rs = FINAL / 4096.0
SS = 2


def flipy(centers):
    return [[x, -y] for x, y in centers]


def stress_tuples(court):
    return [(k, i, j, w) for (k, i, j, w) in court["stress"]]


def main():
    courts = {c["name"]: c for c in json.load(open("courts.json"))}
    census = json.load(open("rings_census_K7.json"))
    ghosts = census["ghosts"]

    cv = Canvas(FINAL, FINAL, ss=SS)
    W = FINAL * SS

    def px(x):
        return x * rs * SS

    # ---------------- layout ----------------
    # central court
    C = (px(2048), px(1700), px(985))
    # orbit: 9 essential courts on an arc around the center;
    # the last seat is the redemption: the court that holds the five
    orbit_names = [
        "n=2 · [2,2]", "n=3 · [2,2,3]", "n=3 · [2,3,3,3,3]", "[2,3,2,3]",
        "n=4 · [2,3,2,4,4]", "seven thirds", "[3]x6", "[2,6,3,6]x2",
        "the court that holds the five",
    ]
    Rorb = px(325)
    labels = []

    n_orb = len(orbit_names)
    cxs, cys = [], []
    for k in range(n_orb):
        t = math.radians(206 - k * (232.0 / (n_orb - 1)))
        stag = px(60) if k % 2 else -px(30)
        ex = px(2048) + (px(1560) + stag) * math.cos(t)
        ey = px(1680) - (px(1290) + stag) * math.sin(t)
        cxs.append(ex)
        cys.append(ey)

    # ---------------- central court ----------------
    name = "the court that skipped five"
    c = courts[name]
    centers = flipy(c["centers"])
    radii = c["radii"]
    # orient: rotate so the 1/3 coin is at top (find it)
    i3 = radii.index(1 / 3) if (1 / 3) in radii else int(np.argmin(radii))
    a = math.atan2(centers[i3][1], centers[i3][0])
    rot = -math.pi / 2 - a          # 1/3 coin to the TOP of the screen
    ca, sa = math.cos(rot), math.sin(rot)
    centers = [[x * ca - y * sa, x * sa + y * ca] for x, y in centers]
    dream = soddy_fill([(x, y, r) for (x, y), r in zip(centers, radii)],
                       min_r=0.0028 if PROTO else 0.0012)
    for (x, y, r) in dream:
        draw_ring(cv, C[0] + x * C[2], C[1] + y * C[2], r * C[2], GHOST,
                  amp=0.15, width=1.0 * SS)
    draw_court(cv, C[0], C[1], C[2], centers, radii,
               stress_pairs=stress_tuples(c), scale_amp=1.0,
               chain_amp=1.5)
    labels.append((C[0], C[1] + C[2] + px(56),
                   "{ ½ ½ ⅓ ¼ ¼ ⅙ ⅙ ⅐ }  ·  the perfect fit that skipped five",
                   1.0))

    # ---------------- orbit courts ----------------
    for k, nm in enumerate(orbit_names):
        c = courts[nm]
        centers = flipy(c["centers"])
        radii = c["radii"]
        Rk = Rorb * (1.17 if nm.startswith("the court") else 1.0)
        if nm.startswith("the court"):
            cxs[k], cys[k] = px(3555), px(2500)   # seat of honor, lower right
        dream = soddy_fill([(x, y, r) for (x, y), r in zip(centers, radii)],
                           min_r=0.006 if PROTO else 0.0035)
        for (x, y, r) in dream:
            draw_ring(cv, cxs[k] + x * Rk, cys[k] + y * Rk, r * Rk,
                      GHOST, amp=0.08, width=0.9 * SS)
        draw_court(cv, cxs[k], cys[k], Rk, centers, radii,
                   stress_pairs=stress_tuples(c), scale_amp=0.92,
                   chain_amp=1.4)
        if nm.startswith("the court"):
            labels.append((cxs[k], cys[k] - Rk - px(36),
                           "the five, held at last  ·  [2,5,8,8,5]×2", 0.72))
        else:
            labels.append((cxs[k], cys[k] + Rk + px(40),
                           nm.replace(" · ", "  "), 0.62))

    # ------------- census strip: ALL rigid rings K<=9, tiny, archival ----
    k9 = json.load(open("rings_census_K9.json"))
    allrings = sorted([r["ring"] for r in k9["rigid"]], key=lambda r: (len(r), r))
    Rc = px(76)
    n_strip = len(allrings)
    for k, ring in enumerate(allrings):
        sx = px(2048) + (k - (n_strip - 1) / 2) * px(164)
        sy = px(3010)
        pos = ring_positions(ring)
        centers = [[x, -y] for x, y, r in pos]
        radii = [r for x, y, r in pos]
        draw_court(cv, sx, sy, Rc, centers, radii, stress_pairs=None,
                   scale_amp=0.55, coin_amp=1.0, tray_amp=0.8)
    labels.append((px(2048), px(3010) + Rc + px(46),
                   "the complete rim-ring census to curvature 9: these 24 courts hold — the five only ever clamped as [5 8 8 5] between halves; "
                   "7 and 9 never hold; 71 more rings close exactly and still rattle", 0.62))

    # ------------- the half-fallen court (closes exactly, still rattles) ----
    c = courts["[2,2,4,4] · closes but rattles"]
    fcenters = flipy(c["centers"])
    fradii = c["radii"]
    fx, fy, fR = px(430), px(3480), px(252)
    draw_court(cv, fx, fy, fR, fcenters, fradii, stress_pairs=None,
               scale_amp=0.85, coin_amp=1.0)
    for dth in (-0.085, 0.085):
        ca2, sa2 = math.cos(dth), math.sin(dth)
        for (x, y), r in zip(fcenters, fradii):
            if abs(r - 0.25) < 1e-9:
                x2, y2 = x * ca2 - y * sa2, x * sa2 + y * ca2
                draw_ring(cv, fx + x2 * fR, fy + y2 * fR, r * fR, WOUND,
                          amp=0.30, width=1.0 * SS)
    labels.append((fx, fy + fR + px(40),
                   "[2,2,4,4]  closes exactly — yet rattles", 0.55))

    # ---------------- underworld: the ghost courts ----------------
    show = [[2, 5, 2, 5, 2, 5], [2, 3, 3, 2, 5],
            [2, 5, 2, 5, 8, 8, 5, 8, 8, 5], [2, 9, 2, 9, 2, 9, 9, 2, 9, 9]]
    Rg = px(252)
    gx0, gx1 = px(1150), px(3660)
    for k, ring in enumerate(show):
        gx = gx0 + (gx1 - gx0) * (k / max(len(show) - 1, 1))
        gy = px(3480) + px(36) * math.sin(k * 2.2)
        pos = ring_positions(ring)
        centers = [[x, -y] for x, y, r in pos]
        radii = [r for x, y, r in pos]
        draw_ghost_court(cv, gx, gy, Rg, centers, radii, scale_amp=0.9)
        labels.append((gx, gy + Rg + px(40),
                       "[" + " ".join(map(str, ring)) + "]  closes — but cannot exist",
                       0.55))

    # ---------------- glow pass ----------------
    bloom(cv, 30 * rs * SS, 0.65, thresh=0.75)
    img = to_img(cv, k=1.32)

    # ---------------- text ----------------
    draw = ImageDraw.Draw(img)
    fdir = "/usr/share/fonts/truetype/dejavu/"
    def F(sz, bold=False):
        return ImageFont.truetype(fdir + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
                                  max(int(sz * rs), 8))
    silver = (168, 172, 182)
    dim = (120, 124, 136)
    for (x, y, txt, alpha) in labels:
        f = F(34 if alpha > 0.9 else 27, bold=alpha > 0.9)
        col = tuple(int(v * (0.55 + 0.45 * alpha)) for v in silver)
        draw.text((x / SS, y / SS), txt, font=f, fill=col, anchor="mm")

    title = "HELD  ·  THE COURTS OF PERFECT FIT"
    sub = ("coins of radius 1/2 … 1/n held rigidly in a unit tray — MO 513668 · every court above certified exact "
           "(ring closure proved in ℚ(i,√2,√3), rigidity prestress-stable) · below: the rings that close in angle but overlap in space — "
           "the only courts that ever held the five")
    draw.text((FINAL // 2, FINAL - int(150 * rs)), title, font=F(52, True),
              fill=(214, 218, 228), anchor="mm")
    draw.text((FINAL // 2, FINAL - int(96 * rs)), sub, font=F(24),
              fill=dim, anchor="mm")

    out = "hero_proto.png" if PROTO else "held_courts_4096.png"
    img.save(out)
    print("saved", out)


if __name__ == "__main__":
    main()
