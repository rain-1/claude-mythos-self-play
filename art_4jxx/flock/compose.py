"""Hero: scene + paper caption band faded over the bottom of the lake.  python3 compose.py raw.png out.png"""
import sys, numpy as np
from PIL import Image
sys.path.insert(0, "..")
from caption import caption
im = Image.open(sys.argv[1]).convert("RGB"); W, H = im.size
s = W / 4096
caption(im, int(170 * s), int(150 * s), int(3700 * s),
        "The Flock Is Equally Thick Everywhere",
        "1,500,000 starlings carried by a volume-preserving flow: the birds never crowd.\nEvery dark seam is only the sheet seen edge-on, from where she stands.",
        "birds = points advected by a curl-noise velocity field (div v = 0, density stays uniform)\nink ∝ birds along each line of sight · the reflection is a second projection",
        scale=s, series="SOMETHING WE PROJECT ONTO IT  ·  I")
im.save(sys.argv[2]); print("saved", sys.argv[2], im.size)
