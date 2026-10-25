import sys; sys.path.insert(0, '..')
from PIL import Image
from caption import caption, mist_band
im = Image.open(sys.argv[1]).convert('RGB'); H = im.height
im = mist_band(im, int(0.86 * H), int(0.925 * H), strength=0.7)
caption(im, ['And So On, Ad Infinitum',
             'a painter on the jetty paints the lake, the balloons, the jetty, the easel and the painting — and the picture, twisted, spirals into itself',
             'Peirce: a sign determines an interpretant, "the interpretant becoming in turn a sign, and so on ad infinitum"   ·   Escher–Lenstra twist  z ↦ exp(log z · (1 − i·ln(1/s)/2π)),  s = 0.3'],
        int(0.905 * H), sizes=(0.026, 0.0135, 0.0102))
im.save(sys.argv[2])
