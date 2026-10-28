"""Shared caption band: serif-bold title, italic statement, small legend line."""
from PIL import ImageFont, ImageDraw

FS = "/usr/share/fonts/truetype/freefont/"
INK = (92, 77, 102)
CORAL = (240, 112, 98)

def font(kind, size):
    name = {"bold": "FreeSerifBold.ttf", "ital": "FreeSerifItalic.ttf", "reg": "FreeSerif.ttf",
            "bi": "FreeSerifBoldItalic.ttf"}[kind]
    return ImageFont.truetype(FS + name, int(size))

def caption(img, x, y, W, title, line, legend, scale=1.0, align="left", series=None):
    dr = ImageDraw.Draw(img)
    s = scale
    items = []
    if series: items.append((series, font("reg", 34 * s), (150, 128, 160), 14 * s))
    items += [(title, font("bold", 92 * s), INK, 22 * s), (line, font("ital", 50 * s), INK, 16 * s),
              (legend, font("reg", 38 * s), (128, 110, 136), 0)]
    for txt, f, col, gap in items:
        if not txt: continue
        for sub in txt.split("\n"):
            w = dr.textlength(sub, font=f)
            xx = x if align == "left" else (x + (W - w) / 2 if align == "center" else x + W - w)
            dr.text((xx, y), sub, font=f, fill=col)
            y += f.size * 1.18
        y += gap
    return y
