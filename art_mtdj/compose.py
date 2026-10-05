"""compose.py — stitch strip renders and add a caption block.
usage: compose.py out.png strips_prefix W H corner title line1 line2 [line3]"""
import sys, glob, numpy as np
from PIL import Image
sys.argv += [''] * 3
out, pre, W, H, corner = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
title, lines = sys.argv[6], [l for l in sys.argv[7:] if l]
parts = sorted(glob.glob(pre + '_*.npy'), key=lambda p: int(p.rsplit('_', 1)[1][:-4]))
img = np.concatenate([np.load(p) for p in parts], 0)
assert img.shape[:2] == (H, W), img.shape
lin = np.clip(img, 0, 1)
srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
srgb = srgb * 255 + np.random.default_rng(9).uniform(-0.5, 0.5, srgb.shape)
im = Image.fromarray(np.clip(srgb + 0.5, 0, 255).astype(np.uint8))
from caption import caption
fs = int(W * 0.026)
specs = [(lines[0], 'i', 0.5)] + [(l, 'r', 0.40) for l in lines[1:]]
if corner == 'tl': caption(im, int(W * 0.045), int(H * 0.045), title, specs, fs)
elif corner == 'br': caption(im, int(W * 0.955), int(H * 0.86), title, specs, fs, align='right')
elif corner == 'bl': caption(im, int(W * 0.05), int(H * 0.855), title, specs, fs)
im.save(out); print('saved', out, im.size)
