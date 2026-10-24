"""Caption block: serif-bold title, italic object line, small legend line, in thin plum ink.
python3 caption.py in.png out.png x y align 'Title' 'italic line' 'legend line' [bg_check]"""
import sys
from PIL import Image, ImageDraw, ImageFont

FB = '/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf'
FI = '/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf'
FR = '/usr/share/fonts/truetype/freefont/FreeSerif.ttf'
INK = (92, 77, 102)


def caption(img, x, y, align, title, line1, line2, scale=1.0, ink=INK):
    S = img.size[0] / 4096 * scale
    d = ImageDraw.Draw(img)
    fonts = [ImageFont.truetype(FB, int(118 * S)), ImageFont.truetype(FI, int(64 * S)),
             ImageFont.truetype(FR, int(50 * S))]
    texts = [title, line1, line2]
    cy = y
    for k, (t, f) in enumerate(zip(texts, fonts)):
        col = ink if k < 2 else tuple(min(255, int(c * 1.25)) for c in ink)
        for ln in t.split('\n'):
            w = d.textlength(ln, font=f)
            xx = x - w if align == 'right' else (x - w / 2 if align == 'center' else x)
            d.text((xx, cy), ln, font=f, fill=col)
            cy += int(f.size * 1.18)
        cy += int(f.size * 0.30)
    return img


if __name__ == '__main__':
    im = Image.open(sys.argv[1]).convert('RGB')
    caption(im, int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])
    im.save(sys.argv[2])
