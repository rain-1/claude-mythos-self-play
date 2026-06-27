"""Conway topograph of a binary quadratic form, drawn as a radial trivalent tree.

Faces of the topograph are primitive vectors (p,q); a face's value is Q(p,q).
Adjacent faces are Farey neighbours (|pq'-p'q|=1); they meet along an edge whose
two ends carry the apex faces F1+F2 and F1-F2 (the parallelogram law
Q(F1+F2)+Q(F1-F2)=2Q(F1)+2Q(F2)). We grow the dual trivalent tree outward from
the form's "well" (its three smallest faces), each vertex sprouting two children
at +-60 degrees, lengths decaying so the tree fills a disc. For a definite form
all values are positive and grow outward -- a luminous warm well cooling to the
rim.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter


def _Q(form):
    a, b, c = form
    return lambda p, q: a * p * p + b * p * q + c * q * q


def build(form, maxdepth=11, L0=1.0, decay=0.62, spread=60.0):
    """Return (segments, faces). segments: (P0,P1,valL,valR). faces: {vec:(pos,val)}."""
    Q = _Q(form)
    segs = []
    faces = {}

    def addface(vec, pos, val):
        key = vec if vec[0] > 0 or (vec[0] == 0 and vec[1] > 0) else (-vec[0], -vec[1])
        if key not in faces:
            faces[key] = (pos, val)

    def vsub(u, v): return (u[0] - v[0], u[1] - v[1])
    def vadd(u, v): return (u[0] + v[0], u[1] + v[1])

    # central vertex, three faces F0,F1,F2 with F2=F0+F1
    F0, F1 = (1, 0), (0, 1)
    F2 = vadd(F0, F1)
    O = (0.0, 0.0)
    tri = [F0, F1, F2]
    # seed face labels around the centre
    for i, Fv in enumerate(tri):
        ang = math.radians(90 + 120 * i + 60)
        addface(Fv, (0.45 * L0 * math.cos(ang), 0.45 * L0 * math.sin(ang)), Q(*Fv))

    def grow(P, ang, L, Fa, Fb, apex_in, depth):
        Qp = (P[0] + L * math.cos(ang), P[1] + L * math.sin(ang))
        segs.append((P, Qp, Q(*Fa), Q(*Fb)))
        if depth <= 0:
            return
        s_plus = vadd(Fa, Fb)
        Sout = s_plus if s_plus != apex_in and (-s_plus[0], -s_plus[1]) != apex_in else vsub(Fa, Fb)
        # label the new face just beyond the far vertex
        addface(Sout, (Qp[0] + 0.5 * L * decay * math.cos(ang),
                       Qp[1] + 0.5 * L * decay * math.sin(ang)), Q(*Sout))
        sp = math.radians(spread)
        grow(Qp, ang + sp, L * decay, Fa, Sout, Fb, depth - 1)
        grow(Qp, ang - sp, L * decay, Sout, Fb, Fa, depth - 1)

    for i in range(3):
        Fa, Fb = tri[i], tri[(i + 1) % 3]
        apex_in = tri[(i + 2) % 3]
        ang = math.radians(90 + 120 * i)
        grow(O, ang, L0, Fa, Fb, apex_in, maxdepth)
    return segs, faces


# warm(small value) -> cool(large value) ramp, on a log scale
def valcolor(v, vmin):
    t = math.log(max(v, 1) / vmin) / math.log(38)
    t = min(max(t, 0), 1)
    warm = np.array([1.0, 0.78, 0.30])
    mid = np.array([0.95, 0.42, 0.40])
    cool = np.array([0.25, 0.62, 0.92])
    if t < 0.5:
        return warm * (1 - t * 2) + mid * (t * 2)
    return mid * (1 - (t - 0.5) * 2) + cool * ((t - 0.5) * 2)


def render_one(form, S=700, ss=2, label=True, fname=None, title=None):
    W = S * ss
    segs, faces = build(form)
    vmin = min(form[0], form[2])
    # world extent
    R = 1.9
    def to_px(p):
        return ((p[0] / R * 0.5 + 0.5) * W, (-p[1] / R * 0.5 + 0.5) * W)

    base = Image.new("RGB", (W, W), (4, 6, 12))
    dr = ImageDraw.Draw(base)
    # draw edges thick->thin by depth (approx via length), colored by min face value
    for P0, P1, vL, vR in segs:
        a, b = to_px(P0), to_px(P1)
        seglen = math.hypot(b[0] - a[0], b[1] - a[1])
        col = valcolor(min(vL, vR), vmin)
        wdt = max(1, int(seglen * 0.05))
        wdt = min(wdt, int(0.012 * W))
        rgb = tuple(int(255 * c) for c in np.clip(col, 0, 1))
        dr.line([a, b], fill=rgb, width=wdt)
    arr = np.asarray(base).astype(np.float32) / 255.0
    # bloom
    lum = arr.mean(2)
    for sig, amp in [(2.0 * ss, 0.5), (7.0 * ss, 0.3)]:
        bl = gaussian_filter(lum, sig)
        arr += bl[..., None] * amp * np.array([1.0, 0.85, 0.6])
    arr = 1.0 - np.exp(-1.4 * np.clip(arr, 0, None))
    arr = np.clip(arr, 0, 1) ** (1 / 1.9)
    out = Image.fromarray((arr * 255).astype(np.uint8), "RGB")

    if label:
        out = out.resize((S, S), Image.LANCZOS)        # downscale first
        dr2 = ImageDraw.Draw(out)
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                 max(11, int(0.034 * S)))

        def to_pxS(p):
            return (p[0] / R * 0.5 + 0.5) * S, (-p[1] / R * 0.5 + 0.5) * S
        for vec, (pos, val) in faces.items():
            if val > 22:
                continue
            x, y = to_pxS(pos)
            if not (0.05 * S < x < 0.95 * S and 0.05 * S < y < 0.95 * S):
                continue
            txt = str(val)
            bb = dr2.textbbox((0, 0), txt, font=fnt)
            w_, h_ = bb[2] - bb[0], bb[3] - bb[1]
            col = tuple(int(255 * c) for c in np.clip(valcolor(val, vmin) * 1.25 + 0.2, 0, 1))
            # dark halo for legibility
            for dx in (-2, 0, 2):
                for dy in (-2, 0, 2):
                    dr2.text((x - w_ / 2 + dx, y - h_ / 2 + dy), txt, font=fnt, fill=(0, 0, 0))
            dr2.text((x - w_ / 2, y - h_ / 2), txt, font=fnt, fill=col)
        return out, faces, segs
    return out, faces, segs


if __name__ == "__main__":
    for form, nm in [((1, 1, 6), "principal_116"), ((2, 1, 3), "g_213"), ((2, -1, 3), "g2_2m13")]:
        im, faces, segs = render_one(form, S=600, ss=2, label=True)
        im.save(f"topo_{nm}.png")
        print("saved", nm, "segments", len(segs), "faces<=24:", sum(1 for _, (_, v) in faces.items() if v <= 24))
