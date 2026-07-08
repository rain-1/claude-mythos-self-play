"""Render a braid closure as a glossy woven wreath with Fox-colored arcs.

The closed braid winds around a circle: slot k rides at radius R + k*gap,
crossings swap the two slots with a cosine ease and push the over strand
toward the viewer (z-bump). Every sample is stamped as a tiny opaque
sprite (dark outline disk, colored body, off-center specular) and sprites
are painted in z-order -- the over/under weave falls out of the painter's
algorithm. Arc labels follow the Fox coloring: the under-strand label
becomes 2*over - under (mod p) at each crossing.
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from braidknot import perm_of_word, fox_colorings, monodromy


def label_palette(p):
    """v in F_p -> RGB, curated cyclic ramp."""
    anchors = np.array([
        (1.00, 0.80, 0.35),   # gold
        (0.98, 0.45, 0.25),   # ember
        (0.85, 0.30, 0.55),   # rose
        (0.55, 0.35, 0.85),   # violet
        (0.25, 0.55, 0.95),   # blue
        (0.25, 0.85, 0.80),   # teal
        (0.65, 0.90, 0.40),   # leaf
    ])
    K = len(anchors)
    ts = np.arange(p) / p * K
    i0 = ts.astype(int) % K
    i1 = (i0 + 1) % K
    f = (ts - np.floor(ts))[:, None]
    return anchors[i0] * (1 - f) + anchors[i1] * f


GOLD = np.array([0.82, 0.66, 0.38])


def trace_wreath(n, word, coloring, p, samples_per_seg=64):
    """Sample the closed braid. Returns a list of GROUPS, one per
    (trajectory, crossing-interval), each a dict of arrays
    (theta, slot(float), z, lab) plus a path id for seam-free ordering.

    coloring: length-n label vector (slot labels at theta=0), or None.
    """
    K = max(1, len(word))
    slot_of = list(range(n))     # slot -> trajectory index
    labels = list(coloring) if coloring is not None else [0] * n
    lab_of_traj = [0] * n
    for j in range(n):
        lab_of_traj[slot_of[j]] = labels[j]

    groups = []
    dth = 2 * np.pi / K
    OV = 6                        # samples of overlap into neighbours
    for c in range(K):
        th0 = c * dth
        i, s = word[c] if word else (None, 0)
        tloc = np.linspace(-OV / samples_per_seg, 1 + OV / samples_per_seg,
                           samples_per_seg + 2 * OV)
        ths = th0 + tloc * dth
        easec = np.clip(tloc, 0, 1)
        ease = 0.5 - 0.5 * np.cos(np.pi * easec)      # 0 -> 1
        bump = np.sin(np.pi * easec)                   # 0 -> 1 -> 0
        for slot in range(n):
            tj = slot_of[slot]
            if i is not None and slot in (i, i + 1):
                other = i + 1 if slot == i else i
                r = slot * (1 - ease) + other * ease
                over = (s > 0 and slot == i) or (s < 0 and slot == i + 1)
                z = (1.0 if over else -1.0) * bump
            else:
                r = np.full_like(ths, float(slot))
                z = np.zeros_like(ths)
            half = len(tloc) // 2
            labs = np.full(len(tloc), lab_of_traj[tj])
            if i is not None and slot in (i, i + 1):
                over_slot = i if s > 0 else i + 1
                if slot != over_slot and p:
                    newlab = (2 * lab_of_traj[slot_of[over_slot]]
                              - lab_of_traj[tj]) % p
                    labs[half:] = newlab
            groups.append(dict(theta=ths, slot=r, z=z, lab=labs,
                               zkey=float(z[len(z) // 2]), gid=len(groups)))
        if i is not None:
            over_slot = i if s > 0 else i + 1
            under_slot = i + 1 if s > 0 else i
            if p:
                lab_of_traj[slot_of[under_slot]] = (
                    2 * lab_of_traj[slot_of[over_slot]]
                    - lab_of_traj[slot_of[under_slot]]) % p
            slot_of[i], slot_of[i + 1] = slot_of[i + 1], slot_of[i]
    return groups


def stamp_knot(canvas, cx, cy, n, word, p, coloring, R, gap, tube_w,
               phase=0.0, colors=None, spp=None):
    """Paint the wreath onto canvas (H,W,3). Groups are painted in z-order;
    within a group: all outlines, then all bodies, then the specular
    stripe -- smooth tubes, honest occlusion at crossings."""
    H, W, _ = canvas.shape
    K = max(1, len(word))
    circumference = 2 * np.pi * R
    if spp is None:
        spp = max(72, int(circumference / K / (tube_w * 0.16)))
    groups = trace_wreath(n, word, coloring, p, samples_per_seg=spp)

    r_o = tube_w * 0.90
    r_b = tube_w * 0.84
    r_s = tube_w * 0.22
    span = int(np.ceil(r_o)) + 2
    yy, xx = np.mgrid[-span:span + 1, -span:span + 1].astype(np.float64)

    def disk(r, ox=0.0, oy=0.0):
        return (xx - ox) ** 2 + (yy - oy) ** 2 <= r * r

    m_out = disk(r_o)
    m_body = disk(r_b)
    m_spec = disk(r_s, -0.30 * tube_w, -0.30 * tube_w) & m_body
    m_shadow = disk(tube_w * 1.35)
    rr = np.sqrt((xx + 0.25 * tube_w) ** 2 + (yy + 0.25 * tube_w) ** 2) / (r_b + 1e-9)
    shade = np.clip(1.08 - 0.50 * rr, 0.38, 1.08)
    out_col = np.array([0.02, 0.02, 0.045])
    spec_col = np.array([1.0, 0.98, 0.92])

    span_sh = int(np.ceil(tube_w * 1.35)) + 2
    yys, xxs = np.mgrid[-span_sh:span_sh + 1, -span_sh:span_sh + 1].astype(np.float64)
    m_shadow_big = (xxs ** 2 + yys ** 2) <= (tube_w * 1.22) ** 2
    for g in sorted(groups, key=lambda g: (g["zkey"], g["gid"])):
        rad = R + g["slot"] * gap
        th = g["theta"] + phase
        xs = np.round(cx + rad * np.cos(th)).astype(int)
        ys = np.round(cy + rad * np.sin(th)).astype(int)
        ok = (xs >= span_sh) & (xs < W - span_sh) & (ys >= span_sh) & (ys < H - span_sh)
        xs, ys = xs[ok], ys[ok]
        labs = g["lab"][ok]
        if len(xs) == 0:
            continue
        if g["zkey"] > 0.1:
            zz = g["z"][ok]
            for x0, y0, zv in zip(xs[::2], ys[::2], zz[::2]):
                if zv < 0.15:
                    continue
                patch = canvas[y0 - span_sh:y0 + span_sh + 1,
                               x0 - span_sh:x0 + span_sh + 1]
                patch[m_shadow_big] *= 0.70
        for x0, y0 in zip(xs, ys):
            canvas[y0 - span:y0 + span + 1,
                   x0 - span:x0 + span + 1][m_out] = out_col
        for x0, y0, lb in zip(xs, ys, labs):
            col = GOLD if colors is None else colors[lb]
            patch = canvas[y0 - span:y0 + span + 1, x0 - span:x0 + span + 1]
            patch[m_body] = col[None, :] * shade[m_body][:, None]
        for x0, y0 in zip(xs, ys):
            patch = canvas[y0 - span:y0 + span + 1, x0 - span:x0 + span + 1]
            patch[m_spec] = patch[m_spec] * 0.55 + 0.45 * spec_col
    return canvas
