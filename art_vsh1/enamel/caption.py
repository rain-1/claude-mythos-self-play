"""Caption block in the sorbet house style: serif-bold title, italic object line, small legend."""
from PIL import Image, ImageDraw, ImageFont

INK = (92, 77, 102)
BOLD = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
ITAL = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"
REG = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"


def caption(im, title, line1, line2, y0, scale=1.0, line3=None):
    d = ImageDraw.Draw(im)
    W = im.size[0]
    s = W / 4096 * scale
    f1 = ImageFont.truetype(BOLD, int(104 * s))
    f2 = ImageFont.truetype(ITAL, int(58 * s))
    f3 = ImageFont.truetype(REG, int(44 * s))
    y = y0
    for txt, f, col, gap in ((title, f1, INK, 128), (line1, f2, INK, 76), (line2, f3, (128, 112, 138), 58),
                             (line3, f3, (128, 112, 138), 58)):
        if not txt:
            continue
        w = d.textlength(txt, font=f)
        d.text(((W - w) / 2, y), txt, font=f, fill=col)
        y += int(gap * s)
    return im
