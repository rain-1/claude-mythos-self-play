"""Caption blocks (Caladea serif): bold title, italic object line, small legend lines."""
import sys
from PIL import Image, ImageDraw, ImageFont
F = '/usr/share/fonts/truetype/liberation/'
INK = (92, 77, 102); SOFT = (128, 112, 138); CORAL = (232, 112, 104)
def font(n, s): return ImageFont.truetype(F + n, s)

def caption(im, y, title, line, legend, series=None, scale=1.0, x=None, align='center'):
    d = ImageDraw.Draw(im); W = im.width
    ft = font('LiberationSerif-Bold.ttf', int(92*scale)); fi = font('LiberationSerif-Italic.ttf', int(50*scale)); fl = font('LiberationSerif-Regular.ttf', int(38*scale))
    fs = font('LiberationSerif-Regular.ttf', int(34*scale))
    def put(txt, f, col, yy):
        w = d.textlength(txt, font=f)
        xx = (W - w)/2 if align == 'center' else x
        d.text((xx, yy), txt, font=f, fill=col)
    if series:
        put(' '.join(series), fs, CORAL, y); y += int(62*scale)
    put(title, ft, INK, y); y += int(118*scale)
    put(line, fi, INK, y); y += int(68*scale)
    for l in legend:
        put(l, fl, SOFT, y); y += int(52*scale)
    return im

def hero():
    im = Image.open('hero_raw_4096.png').convert('RGB')
    caption(im, 3440, 'Three Doors in a Flower',
        'Every point is painted by where a Brownian walker started there would leave: through which of the three arcs between the coral hinges.',
        ['Matching these three chances with the disc’s is the Riemann map (MO 515949); it carries the disc’s Farey tiles in, tile for tile.',
         'Every white wire is a curve of even odds: on it a walker is as likely to leave by the arc between the wire’s two ends as by all the rest.',
         'Hue = the likely door · paleness = indecision · central triangle = where no door has even odds · fine wire = the (2,3,∞) halves'],
        series='TRUTHS INDEPENDENT OF THE FRAME · I', scale=1.0)
    im.save('three_doors_in_a_flower.png', optimize=True)

def sheet():
    from sheet import CELLS
    cs = 1000; W = 3*cs + 200
    im = Image.new('RGB', (W, 3*cs + 620), (253, 251, 249))
    for i, (n, _) in enumerate(CELLS):
        c = Image.open(f'cell_{n}.png').convert('RGB'); im.paste(c, (100 + (i % 3)*cs, 80 + (i//3)*cs))
    d = ImageDraw.Draw(im)
    x0, y0 = 100 + cs, 80 + cs
    d.rounded_rectangle((x0 + 22, y0 + 22, x0 + cs - 22, y0 + cs - 32), radius=60, outline=CORAL, width=5)
    d.text((x0 + cs/2 - d.textlength('the disc', font=font('LiberationSerif-Italic.ttf', 40))/2, y0 + cs - 22), 'the disc', font=font('LiberationSerif-Italic.ttf', 40), fill=CORAL)
    caption(im, 3*cs + 150, 'Every Room Is the Disc',
        'Nine rooms with three doors each, one rule for the paint: a point’s colour is its three chances of leaving by each door.',
        ['Brownian motion does not notice the shape of the room, so every room inherits the disc’s tiles (centre, coral frame).',
         'Same hue, same three probabilities, and the same hyperbolic tile, in every frame.'],
        series='TRUTHS INDEPENDENT OF THE FRAME · II', scale=0.9)
    im.save('every_room_is_the_disc.png', optimize=True)

def gems(vals):
    g = Image.open('gems_raw_3200.png').convert('RGB')
    im = Image.new('RGB', (3200, 3720), (253, 251, 249)); im.paste(g, (0, 0))
    d = ImageDraw.Draw(im)
    fl = font('LiberationSerif-Italic.ttf', 40)
    for i in range(9):
        t = f'θ = {10*i}°'; cx = 3200/3*(i % 3 + 0.5); cy = 3200/3*(i//3 + 0.47) + 470
        d.text((cx - d.textlength(t, font=fl)/2, cy), t, font=fl, fill=SOFT)
    caption(im, 3260, 'Every Pebble Loses the Same',
        'One ellipse at nine angles on one lattice. Each pebble’s lattice hull is cut as a gem; coral is what the hull misses.',
        [vals, 'At R = 10^6, θ = 0 and θ = 0.618 both give 0.6861. Translations alone already forget the angle; averaging over rotations adds nothing (MO 515905).'],
        series='TRUTHS INDEPENDENT OF THE FRAME · III', scale=0.9)
    im.save('every_pebble_loses_the_same.png', optimize=True)

if __name__ == '__main__':
    for a in sys.argv[1:]:
        if a == 'gems': gems('Perimeter lost × R^1/3 / ∫κ^4/3 ds at R = 10^5:  0.6711 · 0.6710 · 0.6720 · 0.6714 · 0.6719  for θ = 0, π/16, π/8, π/4, 0.618  (± 0.0005)')
        else: globals()[a]()
