#!/usr/bin/env python3
"""Annotation kit: title/caption blocks baked after bloom; per-face font fallback."""
from PIL import Image, ImageDraw, ImageFont

def _load(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def fonts(scale=1.0):
    S = lambda s: int(s * scale)
    base = "/usr/share/fonts/truetype/dejavu/"
    return {
        "title":  _load(base + "DejaVuSerif-Bold.ttf", S(64)),
        "sub":    _load(base + "DejaVuSans.ttf", S(30)),
        "mono":   _load(base + "DejaVuSansMono.ttf", S(24)),
        "mono_s": _load(base + "DejaVuSansMono.ttf", S(19)),
    }

def annotate(img, title, sublines, monolines, margin=64, gap=10,
             col_title=(235, 225, 200), col_sub=(160, 165, 185),
             col_mono=(120, 130, 150), bottom=True, scale=1.0):
    """Draw a text block near the bottom-left; returns the image (in place)."""
    F = fonts(scale)
    d = ImageDraw.Draw(img)
    W, H = img.size
    lines = []
    lines.append((title, F["title"], col_title, int(18*scale)))
    for s in sublines: lines.append((s, F["sub"], col_sub, int(8*scale)))
    for s in monolines: lines.append((s, F["mono_s"], col_mono, int(6*scale)))
    total = sum(f.getbbox(t)[3] - f.getbbox(t)[1] + g for t, f, c, g in lines)
    y = H - margin - total if bottom else margin
    for t, f, c, g in lines:
        d.text((margin, y), t, font=f, fill=c)
        bb = f.getbbox(t)
        y += bb[3] - bb[1] + g
    return img
