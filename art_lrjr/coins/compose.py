"""Caption + legend-by-construction for the coin city.  usage: python3 compose.py RAW.png OUT.png"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
sys_argv = sys.argv[:]
raw, out = sys_argv[1], sys_argv[2]
n = 8; q = [0, 4, 1, 3, 6, 2, 7, 5]
L = np.array([[(i + q[j]) % n for j in range(n)] for i in range(n)])
Hs = n - L
LAYER = ['8fe3c8', '9ad8f2', 'a9bdf6', 'c4acf3', 'eaa8e6', 'ffa8bd', 'ffc08f', 'ff7a6a']
def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
im = Image.open(raw).convert('RGB')
W, H = im.size
dr = ImageDraw.Draw(im)
F = '/usr/share/fonts/truetype/freefont/'
s = W / 4096
fT = ImageFont.truetype(F + 'FreeSerifBold.ttf', int(110 * s))
fI = ImageFont.truetype(F + 'FreeSerifItalic.ttf', int(52 * s))
fS = ImageFont.truetype(F + 'FreeSerif.ttf', int(40 * s))
ink = (92, 77, 102)
x0, y = int(150 * s), int(150 * s)
dr.text((x0, y), 'Every Slice a Solution', font=fT, fill=ink); y += int(140 * s)
for line in ['Sixty-four coin towers on a chessboard. Square (i, j) holds 8 − L(i, j) coins,',
             'where L(i, j) = i + q(j) mod 8 and q = 0 4 1 3 6 2 7 5.',
             'Cut the city at any height and the coins you cut stand c to a row and c to a column,',
             'and never more than c on a diagonal. The top layer is eight queens.']:
    dr.text((x0, y), line, font=fI, fill=ink); y += int(68 * s)
y += int(10 * s)
dr.text((x0, y), 'Only ten permutations q do this on the 8×8 board (five up to mirror image). (MO 516225)', font=fS, fill=ink)
# legend: the eight slices as little boards, bottom-left
cell = int(22 * s); gap = int(34 * s)
bx, by = int(150 * s), H - int(150 * s) - 8 * cell - int(70 * s)
dr.text((bx, by - int(62 * s)), 'the slices, from the floor up', font=fS, fill=ink)
for k in range(n):
    ox = bx + k * (8 * cell + gap)
    col = rgb(LAYER[k])
    for i in range(n):
        for j in range(n):
            xx, yy = ox + j * cell, by + i * cell
            dr.rectangle([xx, yy, xx + cell - 1, yy + cell - 1], fill=(250, 244, 238) if (i + j) % 2 == 0 else (243, 228, 233))
            if Hs[i, j] >= k + 1:
                m = int(cell * 0.16)
                dr.ellipse([xx + m, yy + m, xx + cell - m, yy + cell - m], fill=col)
    lab = f'{n - k} per row'
    w = dr.textlength(lab, font=fS)
    dr.text((ox + 4 * cell - w / 2, by + 8 * cell + int(14 * s)), lab, font=fS, fill=ink)
im.save(out)
