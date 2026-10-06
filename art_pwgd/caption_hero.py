"""caption_hero.py in.png out.png [hero|neck] — caption block in the airy top-left of a marble render."""
import sys
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert('RGB'); W, H = im.size
dr = ImageDraw.Draw(im)
FD = '/usr/share/fonts/truetype/liberation/'
INK = (92, 77, 102)
tb = ImageFont.truetype(FD + 'LiberationSerif-Bold.ttf', int(0.034 * W))
ti = ImageFont.truetype(FD + 'LiberationSerif-Italic.ttf', int(0.0150 * W))
tr = ImageFont.truetype(FD + 'LiberationSerif-Regular.ttf', int(0.0122 * W))
TEXT = {
    'hero': ('Home Through the Dream', [
        ("Three gradient-index marbles, ray-traced in closed form: Luneburg (waking), Maxwell's fish-eye (dreaming), Eaton (deep sleep).", ti),
        ('One coral ray goes waking → dreaming → deep sleep → dreaming → waking: the Eaton lens sends every ray home.', tr),
        ('Only the sleeping marble holds the rainbow — a perfect retroreflector, it shows exactly the sky behind the one who looks.', tr)]),
    'neck': ('The Rainbow Behind You', [
        ('Seven Eaton marbles — perfect retroreflectors — strung along the curve where the line of sight is 41° from the sun.', ti),
        ('Each one shows exactly the sky behind the viewer, and that is where the rainbow is:', tr),
        ('every marble holds its own slice of the bow, while the sky in front of you holds none.', tr)])}
title, lines = TEXT[sys.argv[3] if len(sys.argv) > 3 else 'hero']
x, y = int(0.055 * W), int(0.045 * H)
dr.text((x, y), title, font=tb, fill=INK); y += int(tb.size * 1.32)
for t, f in lines:
    dr.text((x, y), t, font=f, fill=INK); y += int(f.size * 1.42)
im.save(sys.argv[2], optimize=True)
