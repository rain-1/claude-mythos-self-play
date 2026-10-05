"""caption.py — shared sorbet caption block (serif-bold title, italic object line, small legend)."""
from PIL import ImageFont, ImageDraw
FD = '/usr/share/fonts/truetype/liberation/'
INK = (92, 77, 102)
def font(kind, size):
    return ImageFont.truetype(FD + {'b': 'LiberationSerif-Bold.ttf', 'i': 'LiberationSerif-Italic.ttf',
                                     'r': 'LiberationSerif-Regular.ttf', 'm': 'LiberationMono-Regular.ttf'}[kind], size)
def caption(im, x, y, title, lines, size, align='left', ink=INK, coral=(232, 96, 92)):
    """lines: list of (text, kind, scale). returns bottom y"""
    d = ImageDraw.Draw(im)
    rows = [(title, 'b', 1.0, ink)] + [(t, k, s, ink) for t, k, s in lines]
    for t, k, s, c in rows:
        f = font(k, int(size * s))
        w = d.textlength(t, font=f)
        xx = x - w if align == 'right' else x
        d.text((xx, y), t, font=f, fill=c)
        y += int(size * s * 1.32)
    return y
