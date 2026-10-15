"""caption helper: plum serif ink on a finished PIL image (coordinates in units of W/4096)."""
from PIL import Image, ImageDraw, ImageFont
F = '/usr/share/fonts/truetype/liberation/'
INK = (92, 77, 102); INK2 = (128, 112, 138); CORAL = (236, 112, 98)
def caption(im, lines, x, y, anchor='la', scale=None):
    """lines: list of (text, style) with style in 'title','line','small','mono'"""
    d = ImageDraw.Draw(im); s = (scale or im.size[0] / 4096)
    fonts = {'title': ('LiberationSerif-Bold.ttf', 104, INK, 135), 'line': ('LiberationSerif-Italic.ttf', 56, INK, 78),
             'small': ('LiberationSerif-Italic.ttf', 42, INK2, 60), 'mono': ('LiberationMono-Regular.ttf', 36, INK2, 54)}
    yy = y
    for text, st in lines:
        fn, sz, col, lh = fonts[st]; f = ImageFont.truetype(F + fn, int(sz * s))
        d.text((x * s, yy * s), text, font=f, fill=col, anchor=anchor); yy += lh
    return im
