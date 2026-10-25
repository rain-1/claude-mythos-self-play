import sys, numpy as np
from PIL import Image
sys.path.insert(0, '..')
from post import tone
from caption import caption, mist_band
img = np.load(sys.argv[1]); H, W = img.shape[:2]
s = tone(img, 1.0)
rng = np.random.default_rng(5)
s = s + rng.normal(0, 0.006, s.shape[:2])[..., None]
im = Image.fromarray((np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8))
im = mist_band(im, int(0.865 * H), int(0.925 * H), strength=0.62)
caption(im, ['Every Balloon Is Sewn from Its Friend',
             'the thirteen amicable pairs below 100,000 — each balloon is cut from its proper divisors, one panel per divisor, as wide as the divisor',
             '220 = 1 + 2 + 4 + 71 + 142   and   284 = 1 + 2 + 4 + 5 + 10 + 11 + 20 + 22 + 44 + 55 + 110 :  each balloon\'s panels go round to its friend   ·   warm: the smaller   ·   cool: the larger'],
        int(0.912 * H), sizes=(0.024, 0.0128, 0.0098))
im.save(sys.argv[2])
