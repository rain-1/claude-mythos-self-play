"""05 - The Cube That Composes to One.

A 2x2x2 integer cube, sliced three ways, yields three binary quadratic forms of
one shared discriminant; Bhargava proved they compose to the identity of the
form class group. We take the cube (-1,-1,-1,2,0,1,2,2): discriminant -23, the
smallest with three distinct classes (the cyclic group of order 3). Its three
forms (1,1,6),(2,1,3),(2,-1,3) are the whole class group {1, g, g^2}, and
1 * g * g^2 = 1 -- verified by Dirichlet composition. Each form is drawn as its
Conway topograph: a trivalent tree of values, warm at the well, cooling outward.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from bhargava_core import cube_forms, reduce_def, disc, compose_list
from topograph import render_one

CUBE = (-1, -1, -1, 2, 0, 1, 2, 2)
SLICE_COL = [(255, 150, 70), (120, 210, 120), (150, 150, 255)]   # i / j / k slicings


def F(path, sz):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" + path, sz)


def draw_cube(size, ss=2):
    """Glowing wireframe 2x2x2 cube with labelled vertices, on transparent-ish dark."""
    W = size * ss
    img = Image.new("RGB", (W, W), (6, 8, 14))
    dr = ImageDraw.Draw(img)
    # corner (i,j,k) -> value index per bhargava_core mapping a..h = 000,001,010,011,100,101,110,111
    idx = {(0, 0, 0): 0, (0, 0, 1): 1, (0, 1, 0): 2, (0, 1, 1): 3,
           (1, 0, 0): 4, (1, 0, 1): 5, (1, 1, 0): 6, (1, 1, 1): 7}
    # 3-D positions, small isometric-ish projection
    ax, ay = math.radians(26), math.radians(-32)
    def proj(i, j, k):
        # cube coords -> 3D (x right, y up, z depth)
        x = (k - 0.5) * 2
        y = (0.5 - i) * 2
        z = (j - 0.5) * 2
        # rotate about y then x
        x2 = x * math.cos(ay) + z * math.sin(ay)
        z2 = -x * math.sin(ay) + z * math.cos(ay)
        y2 = y * math.cos(ax) - z2 * math.sin(ax)
        zc = y * math.sin(ax) + z2 * math.cos(ax)
        f = 1.0 / (1.0 - 0.16 * zc)
        sx = W / 2 + x2 * f * 0.20 * W
        sy = W / 2 - y2 * f * 0.20 * W
        return sx, sy, zc
    P = {c: proj(*c) for c in idx}
    # edges: corners differing in exactly one coord
    corners = list(idx)
    edges = []
    for a in corners:
        for b in corners:
            if a < b and sum(1 for t in range(3) if a[t] != b[t]) == 1:
                edges.append((a, b))
    # colour each edge by the axis it runs along (the slicing it belongs to is the OTHER axes;
    # we colour by the changing axis so the 3 directions read)
    for a, b in sorted(edges, key=lambda e: (P[e[0]][2] + P[e[1]][2])):
        axis = [t for t in range(3) if a[t] != b[t]][0]
        col = SLICE_COL[axis]
        za = (P[a][2] + P[b][2]) / 2
        bright = 0.5 + 0.5 * (za + 1) / 2
        c = tuple(int(min(255, v * bright)) for v in col)
        dr.line([P[a][:2], P[b][:2]], fill=c, width=max(2, int(0.012 * W)))
    arr = np.asarray(img).astype(np.float32) / 255
    lum = arr.mean(2)
    for sig, amp in [(2.0 * ss, 0.5), (6.0 * ss, 0.3)]:
        arr += gaussian_filter(lum, sig)[..., None] * amp * np.array([1, .9, .7])
    arr = 1 - np.exp(-1.5 * np.clip(arr, 0, None))
    arr = np.clip(arr, 0, 1) ** (1 / 1.9)
    out = Image.fromarray((arr * 255).astype(np.uint8)).resize((size, size), Image.LANCZOS)
    # vertex dots + value labels at final res
    dr2 = ImageDraw.Draw(out)
    fnt = F("DejaVuSans-Bold.ttf", int(0.075 * size))
    for c, i in idx.items():
        x, y, z = P[c]
        x, y = x / ss, y / ss
        r = int(0.022 * size * (0.8 + 0.3 * (z + 1)))
        dr2.ellipse([x - r, y - r, x + r, y + r], fill=(250, 245, 235))
        val = str(CUBE[i])
        bb = dr2.textbbox((0, 0), val, font=fnt)
        w_, h_ = bb[2] - bb[0], bb[3] - bb[1]
        tx, ty = x - w_ / 2, y - h_ - r - 2
        for dx in (-2, 0, 2):
            for dy in (-2, 0, 2):
                dr2.text((tx + dx, ty + dy), val, font=fnt, fill=(0, 0, 0))
        dr2.text((tx, ty), val, font=fnt, fill=(255, 235, 180))
    return out


def tint_border(im, col, w=10):
    d = ImageDraw.Draw(im)
    for i in range(w):
        a = 1 - i / w
        c = tuple(int(col[k] * a + 0) for k in range(3))
        d.rectangle([i, i, im.size[0] - 1 - i, im.size[1] - 1 - i], outline=c)
    return im


def build_plate(S=2048):
    bg = Image.new("RGB", (S, S), (8, 10, 16))
    dr = ImageDraw.Draw(bg)
    forms = cube_forms(CUBE)
    red = [reduce_def(f) for f in forms]
    D = disc(forms[0])
    comp = compose_list(forms)

    # --- title ---
    ftitle = F("DejaVuSans-Bold.ttf", int(0.040 * S))
    fsub = F("DejaVuSans.ttf", int(0.0185 * S))
    dr.text((int(0.06 * S), int(0.035 * S)), "THE CUBE THAT COMPOSES TO ONE", font=ftitle, fill=(245, 235, 215))
    dr.text((int(0.06 * S), int(0.084 * S)),
            "Bhargava's cube  →  three forms of one discriminant  →  they compose to the identity",
            font=fsub, fill=(150, 170, 190))

    # --- cube (top-left) ---
    cs = int(0.34 * S)
    cube_im = draw_cube(cs)
    cx0, cy0 = int(0.045 * S), int(0.135 * S)
    bg.paste(cube_im, (cx0, cy0))

    # --- forms / equation block (top-right of cube) ---
    fx = cx0 + cs + int(0.035 * S)
    fy = cy0 + int(0.02 * S)
    fform = F("DejaVuSansMono-Bold.ttf", int(0.0215 * S))
    fnote = F("DejaVuSans.ttf", int(0.0175 * S))
    dr.text((fx, fy), f"discriminant  D = {D}", font=fform, fill=(200, 210, 225))
    names = ["Q1 (slice i)", "Q2 (slice j)", "Q3 (slice k)"]
    for n, (nm, rf, col) in enumerate(zip(names, red, SLICE_COL)):
        yy = fy + int(0.055 * S) + n * int(0.05 * S)
        dr.rectangle([fx, yy + int(0.004 * S), fx + int(0.02 * S), yy + int(0.026 * S)], fill=col)
        a, b, c = rf
        dr.text((fx + int(0.03 * S), yy), f"{nm} = {a}x² {'+' if b>=0 else '−'}{abs(b)}xy +{c}y²",
                font=fform, fill=tuple(min(255, int(v * 1.0)) for v in col))
    eqy = fy + int(0.055 * S) + 3 * int(0.05 * S) + int(0.012 * S)
    one = reduce_def((1, D % 2, ((D % 2) - D) // 4))
    ok = "✓ verified" if comp == one else "✗"
    dr.text((fx, eqy), f"[Q1]·[Q2]·[Q3] = 1   {ok}",
            font=fform, fill=(245, 225, 150))
    dr.text((fx, eqy + int(0.038 * S)),
            "class group of D=−23 is cyclic C₃:",
            font=fnote, fill=(140, 160, 180))
    dr.text((fx, eqy + int(0.064 * S)),
            "these forms are its whole {1, g, g²}.",
            font=fnote, fill=(140, 160, 180))

    # --- three topographs in a row ---
    margin = int(0.038 * S)
    inner = int(0.028 * S)
    ts = int((S - 2 * margin - 2 * inner) / 3)
    x = margin
    ytop = int(0.50 * S)
    fcap = F("DejaVuSansMono-Bold.ttf", int(0.0205 * S))
    labels = ["principal  (1, 1, 6)  =  1", "g  =  (2, 1, 3)", "g²  =  (2, −1, 3)"]
    order = [1, 0, 2]   # principal, g, g^2  (forms list is slice i,j,k = (2,1,3),(1,1,6),(2,-1,3))
    for slot, oi in enumerate(order):
        im, _, _ = render_one(red[oi], S=ts, ss=2, label=True)
        im = tint_border(im, SLICE_COL[oi], w=max(6, int(0.006 * S)))
        bg.paste(im, (x, ytop))
        cap = labels[slot]
        bb = dr.textbbox((0, 0), cap, font=fcap)
        dr.text((x + ts / 2 - (bb[2] - bb[0]) / 2, ytop + ts + int(0.012 * S)),
                cap, font=fcap, fill=tuple(min(255, int(v)) for v in SLICE_COL[oi]))
        x += ts + inner

    # --- caption block ---
    cy = int(0.875 * S)
    dr.rectangle([int(0.045 * S), cy, int(0.052 * S), cy + int(0.085 * S)], fill=(245, 225, 150))
    fctag = F("DejaVuSans-Bold.ttf", int(0.016 * S))
    fcbody = F("DejaVuSans.ttf", int(0.0175 * S))
    dr.text((int(0.066 * S), cy), "FIGURE · GAUSS COMPOSITION", font=fctag, fill=(245, 225, 150))
    body = ("A topograph face is a primitive vector (p,q); its value is Q(p,q). Neighbouring faces obey the\n"
            "parallelogram law Q(u+v)+Q(u−v)=2Q(u)+2Q(v) — the rule that grows the whole tree from its well.\n"
            "One identity from three slices: the law Gauss found by hand, that Bhargava re-saw inside a box.")
    dr.multiline_text((int(0.066 * S), cy + int(0.026 * S)), body, font=fcbody, fill=(180, 195, 210), spacing=int(0.008 * S))
    return bg


if __name__ == "__main__":
    import sys
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 1400
    im = build_plate(S)
    im.save("05_the_cube_that_composes_to_one.png")
    print("saved 05_the_cube_that_composes_to_one.png", im.size)
