"""The same lightbox (seed 9) at six moments: the light goes out.
usage: python3 strip.py OUT.png T"""
import sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor

out, T = sys.argv[1], int(sys.argv[2])
P = 1300
Ns = [1, 10, 100, 1214, 34963, T]
here = os.path.dirname(os.path.abspath(__file__))
tmp = os.path.join(here, '..', 'proto')
def job(N):
    f = os.path.join(tmp, f'strip_{N}.png')
    if os.path.exists(f) and '--reuse' in sys.argv:
        return f
    subprocess.run(['python3', os.path.join(here, 'lightbox.py'), str(P), str(N), '9', f, '--dens', '0.13',
                    '--cy', '0.43', '--last=-0.260,0.156'], check=True)
    return f
with ThreadPoolExecutor(3) as ex:
    files = list(ex.map(job, Ns))
gap, mx, top = 0, 48, 40
capH = 520
W = mx * 2 + 3 * P
H = top + 2 * P + capH
import numpy as np
c0 = np.asarray(Image.open(files[0]))[:60, :60].reshape(-1, 3).mean(0)
grain = np.random.default_rng(3).normal(0, 1.6, (H, W, 1))
canvas = Image.fromarray(np.clip(c0[None, None, :] + grain, 0, 255).astype(np.uint8))
F = '/usr/share/fonts/truetype/freefont/'
fL = ImageFont.truetype(F + 'FreeSerifItalic.ttf', 46)
fLb = ImageFont.truetype(F + 'FreeSerifBold.ttf', 46)
ink = (92, 77, 102)
labels = {1: 'one sheet', 10: 'ten', 100: 'a hundred', 1214: '1,214 (the large picture)',
          34963: '34,963: one hole left, smaller than a pixel', T: f'{T:,}: the last light goes out'}
dr = ImageDraw.Draw(canvas)
for k, (N, f) in enumerate(zip(Ns, files)):
    r, c = divmod(k, 3)
    x0, y0 = mx + c * P, top + r * P
    canvas.paste(Image.open(f), (x0, y0))
    lab = labels[N]
    w = dr.textlength(lab, font=fL)
    dr.text((x0 + P / 2 - w / 2, y0 + int(0.885 * P)), lab, font=fL, fill=ink)
fT = ImageFont.truetype(F + 'FreeSerifBold.ttf', 96)
fI = ImageFont.truetype(F + 'FreeSerifItalic.ttf', 52)
fS = ImageFont.truetype(F + 'FreeSerif.ttf', 44)
y = top + 2 * P + 60
dr.text((mx + 40, y), 'The Light Goes Out', font=fT, fill=ink)
y += 125
dr.text((mx + 40, y), 'One lightbox, six moments. Sheet n is a disc of tissue of area π/n dropped with its centre anywhere in the window.',
        font=fI, fill=ink)
y += 66
dr.text((mx + 40, y), 'The areas add up to infinity only as fast as log n, exactly the critical rate, so the last points of light hold out for a very long time.',
        font=fI, fill=ink)
y += 76
dr.text((mx + 40, y), 'Coral double ring: the last point to go dark.  Hue = the direction of the sheet’s centre.  (MO 458793)', font=fS, fill=ink)
canvas.save(out)
