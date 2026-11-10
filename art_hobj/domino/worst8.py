"""The two tilings of the 8x8 board (of 12 988 816) whose longest domino-respecting path ties only 28 of 32."""
import numpy as np, sys
from path import build
from render import render, bead, font
from PIL import Image, ImageDraw
sys.setrecursionlimit(10000)
def conv(own):
    n = own.shape[0]; d = np.zeros((n, n), np.int32)
    for r in range(n):
        for c in range(n):
            if c + 1 < n and own[r, c + 1] == own[r, c]: d[r, c] = 0
            elif c > 0 and own[r, c - 1] == own[r, c]: d[r, c] = 1
            elif r + 1 < n and own[r + 1, c] == own[r, c]: d[r, c] = 2
            else: d[r, c] = 3
    return d
def find(out, target):
    ND = len(out); res = []
    def dfs(v, vis, p):
        if len(p) >= target: res.append(p[:]); return True
        for u in out[v]:
            if u >= 0 and not vis >> u & 1:
                p.append(u)
                if dfs(u, vis | 1 << u, p): return True
                p.pop()
        return False
    for s in range(ND):
        if dfs(s, 1 << s, [s]): return res[0]
S = int(sys.argv[1]); canvas = Image.new('RGB', (S, int(S * 0.62)), (253, 251, 249)); d = ImageDraw.Draw(canvas)
for k, f in enumerate(('min8_0.bin', 'min8_3.bin')):
    own = conv(np.fromfile(f, np.int32).reshape(-1, 8, 8)[-1]); idx, cells, o = build(own); p = find(o, 28)
    np.save(f'worst8_{k}.npy', own); np.savez('/tmp/_t.npz', own=own, idx=idx, cells=cells, out=o, path=np.array(p))
    T = int(S * 0.44 / 0.80); im, info = render('/tmp/_t.npz', T, cycles=0.92)
    P = info['P']; bead(im, *P[0], 0.17 * info['u']); bead(im, *P[-1], 0.17 * info['u']); pad = int(info['u'] * 0.3)
    canvas.paste(im.crop((int(info['x0']) - pad, int(info['y0']) - pad, int(info['x0'] + info['B']) + pad, int(info['y0'] + info['B']) + pad + 4)), (int(S * (0.04 + 0.48 * k)), int(S * 0.03)))
    print(k, len(p), flush=True)
ink = (92, 77, 102)
d.text((0.05 * S, 0.505 * S), 'Two in Thirteen Million', font=font('liberation/LiberationSerif-Bold.ttf', 0.030 * S), fill=ink)
d.text((0.05 * S, 0.548 * S), 'Of the 12 988 816 domino tilings of the chessboard, only this mirror pair cannot be tied past 28 of 32.', font=font('liberation/LiberationSerif-Italic.ttf', 0.0165 * S), fill=ink)
d.text((0.05 * S, 0.578 * S), 'exhaustive search · worst case 2/2, 7/8, 16/18, 28/32 for n = 2, 4, 6, 8 · white = left out', font=font('dejavu/DejaVuSansMono.ttf', 0.0100 * S), fill=(132, 118, 146))
canvas.save(sys.argv[2])
