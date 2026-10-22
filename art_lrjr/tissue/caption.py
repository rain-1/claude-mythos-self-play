"""Caption the 4096 lightbox hero.  usage: python3 caption.py RAW.png OUT.png T"""
import sys
from PIL import Image, ImageDraw, ImageFont
raw, out, T = sys.argv[1], sys.argv[2], int(sys.argv[3])
im = Image.open(raw).convert('RGB')
S = im.size[0]
dr = ImageDraw.Draw(im)
F = '/usr/share/fonts/truetype/freefont/'
fT = ImageFont.truetype(F + 'FreeSerifBold.ttf', 104)
fI = ImageFont.truetype(F + 'FreeSerifItalic.ttf', 54)
fS = ImageFont.truetype(F + 'FreeSerif.ttf', 44)
ink = (92, 77, 102)
def centred(y, text, font):
    w = dr.textlength(text, font=font)
    dr.text(((S - w) / 2, y), text, font=font, fill=ink)
y = int(0.880 * S)
centred(y, 'Three Places the Light Still Gets In', fT); y += 136
centred(y, 'A lightbox and 1,214 sheets of tissue. Sheet n is a disc of area π/n, its centre dropped anywhere in the window.', fI); y += 70
centred(y, 'The areas add up to infinity only as fast as log n, the exact critical rate, and still every point goes dark in the end.', fI); y += 84
centred(y, f'Hue: the direction of each sheet’s centre.   Coral rings: the holes left now.   Double ring: the last light, covered by sheet {T:,}.   (MO 458793)', fS)
im.save(out)
