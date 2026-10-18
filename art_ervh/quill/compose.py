"""Caption band for the quilled pieces: serif-bold title, italic object line, small legend line."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

INK = (92, 77, 102)
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
ITAL = '/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf'
REG = '/usr/share/fonts/truetype/freefont/FreeSerif.ttf'


def wrap(draw, text, font, maxw):
    words = text.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def caption(img, y0, title, line, legend, scale=1.0, maxw_frac=0.86):
    im = Image.fromarray(img) if isinstance(img, np.ndarray) else img
    d = ImageDraw.Draw(im)
    W = im.width
    ft = ImageFont.truetype(BOLD, int(78 * scale))
    fi = ImageFont.truetype(ITAL, int(50 * scale))
    fl = ImageFont.truetype(REG, int(36 * scale))
    y = y0
    tw = d.textlength(title, font=ft)
    d.text(((W - tw) / 2, y), title, font=ft, fill=INK)
    y += int(78 * scale * 1.45)
    for ln in wrap(d, line, fi, W * maxw_frac):
        d.text(((W - d.textlength(ln, font=fi)) / 2, y), ln, font=fi, fill=INK)
        y += int(50 * scale * 1.25)
    y += int(14 * scale)
    for ln in wrap(d, legend, fl, W * maxw_frac):
        d.text(((W - d.textlength(ln, font=fl)) / 2, y), ln, font=fl, fill=(128, 112, 136))
        y += int(36 * scale * 1.3)
    return im, y


def small_label(im, x, y, text, size):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(ITAL, int(size))
    d.text((x - d.textlength(text, font=f) / 2, y), text, font=f, fill=INK)
