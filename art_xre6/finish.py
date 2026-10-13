"""tone-map a beads.c render and set a caption (plum ink, bottom-left)."""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from tone import tone
F='/usr/share/fonts/truetype/liberation/'
def finish(fn, W, H, expo, out, title, line1, line2, pos='bl'):
    im = tone(fn, W, H, expo).convert('RGB'); d = ImageDraw.Draw(im)
    s = W / 4096
    ft = ImageFont.truetype(F + 'LiberationSerif-Bold.ttf', int(96 * s))
    f1 = ImageFont.truetype(F + 'LiberationSerif-Italic.ttf', int(54 * s))
    f2 = ImageFont.truetype(F + 'LiberationSerif-Italic.ttf', int(40 * s))
    ink = (92, 77, 102); ink2 = (128, 112, 138)
    x = int(150 * s); y = H - int(330 * s)
    d.text((x, y), title, font=ft, fill=ink)
    d.text((x, y + int(125 * s)), line1, font=f1, fill=ink)
    d.text((x, y + int(200 * s)), line2, font=f2, fill=ink2)
    im.save(out, optimize=True)
if __name__ == '__main__':
    a = sys.argv
    finish(a[1], int(a[2]), int(a[3]), float(a[4]), a[5], a[6], a[7], a[8])
