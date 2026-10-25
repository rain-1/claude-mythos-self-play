"""Caption block: serif-bold title, one italic line, one small legend line, plum ink."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np

FB = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
FI = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
FR = '/usr/share/fonts/truetype/freefont/FreeSerif.ttf'
INK = (92, 77, 102)

def mist_band(img, y0, y1, colour=(252, 250, 252), strength=0.55):
    """lighten a horizontal band softly (top edge feathered)"""
    a = np.asarray(img).astype(np.float32)
    H = a.shape[0]
    y = np.arange(H)[:, None, None]
    w = np.clip((y - y0) / max(1, (y1 - y0)), 0, 1)
    w = (w * w * (3 - 2 * w)) * strength
    a = a * (1 - w) + np.array(colour, np.float32) * w
    return Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8))

def caption(img, lines, y, sizes=(0.022, 0.0135, 0.0105), gap=0.55, ink=INK, align='center', x=None):
    """lines = [title, italic, legend...]; sizes as fractions of width"""
    d = ImageDraw.Draw(img)
    W = img.width
    fonts = [ImageFont.truetype(FB, int(sizes[0] * W)), ImageFont.truetype(FI, int(sizes[1] * W))]
    for _ in lines[2:]:
        fonts.append(ImageFont.truetype(FR, int(sizes[2] * W)))
    yy = y
    for t, f in zip(lines, fonts):
        bb = d.textbbox((0, 0), t, font=f)
        w = bb[2] - bb[0]
        xx = (W - w) / 2 if align == 'center' else x
        d.text((xx, yy), t, font=f, fill=ink)
        yy += (bb[3] - bb[1]) + gap * f.size
    return yy
