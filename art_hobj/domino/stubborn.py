"""The 20 tilings of the 6x6 board (of 6728) whose longest domino-respecting path ties only 16 of 18 dominoes,
each with one longest path (exhaustive DFS), plus the two worst 4x4 tilings (7 of 8)."""
import numpy as np, sys
from path import build
from render import render, bead, font
from PIL import Image, ImageDraw

def load(n):
    a = np.fromfile(f'min{n}.bin', np.int32).reshape(-1, n, n); res = []
    for own in a:
        d = np.zeros((n, n), np.int32)
        for r in range(n):
            for c in range(n):
                if c + 1 < n and own[r, c + 1] == own[r, c]: d[r, c] = 0
                elif c > 0 and own[r, c - 1] == own[r, c]: d[r, c] = 1
                elif r + 1 < n and own[r + 1, c] == own[r, c]: d[r, c] = 2
                else: d[r, c] = 3
        res.append(d)
    return res

def longest_path(out):
    ND = len(out); best = []
    def dfs(v, vis, p):
        nonlocal best
        if len(p) > len(best): best = p[:]
        for u in out[v]:
            if u >= 0 and not vis >> u & 1:
                p.append(u); dfs(u, vis | 1 << u, p); p.pop()
    for s in range(ND): dfs(s, 1 << s, [s])
    return best

if __name__ == '__main__':
    S = int(sys.argv[1]); out = sys.argv[2]
    canvas = Image.new('RGB', (S, S), (253, 251, 249)); d = ImageDraw.Draw(canvas)
    tiles = []
    for n in (6, 4):
        for k, own in enumerate(load(n)):
            idx, cells, o = build(own); p = longest_path(o)
            if len(p) != {6: 16, 4: 7}[n]: continue
            np.savez(f'/tmp/_t.npz', own=own, idx=idx, cells=cells, out=o, path=np.array(p))
            T = int(S * (0.172 if n == 6 else 0.118) / 0.80)
            im, info = render('/tmp/_t.npz', T, cycles=0.92)
            P = info['P']; bead(im, *P[0], 0.17 * info['u']); bead(im, *P[-1], 0.17 * info['u'])
            pad = int(info['u'] * 0.25)
            box = (int(info['x0']) - pad, int(info['y0']) - pad, int(info['x0'] + info['B']) + pad + 2, int(info['y0'] + info['B']) + pad + 4)
            tiles.append((n, im.crop(box), len(p), len(cells))); print(n, k, len(p), flush=True)
    six = [t for t in tiles if t[0] == 6]; four = [t for t in tiles if t[0] == 4]
    w = six[0][1].size[0]; gx = (0.91 * S - 5 * w) / 4; x0 = 0.045 * S; y0 = 0.060 * S
    for k, (n, t, L, ND) in enumerate(six):
        canvas.paste(t, (int(x0 + (k % 5) * (w + gx)), int(y0 + (k // 5) * (w + gx))))
    yb = y0 + 4 * (w + gx) + 0.012 * S
    w4 = four[0][1].size[0]
    for k, (n, t, L, ND) in enumerate(four):
        canvas.paste(t, (int(S * 0.955 - (2 - k) * (w4 + 0.02 * S) + 0.02 * S), int(yb - 0.012 * S)))
    ink = (92, 77, 102)
    d.text((x0, yb + 0.004 * S), 'The Twenty That Will Not Be Tied', font=font('liberation/LiberationSerif-Bold.ttf', 0.033 * S), fill=ink)
    it = font('liberation/LiberationSerif-Italic.ttf', 0.0165 * S)
    d.text((x0, yb + 0.048 * S), 'Of the 6 728 domino tilings of the 6×6 board, 4 858 can be threaded whole,', font=it, fill=ink)
    d.text((x0, yb + 0.071 * S), '1 850 lose one domino, and these twenty lose two.  None loses three.', font=it, fill=ink)
    d.text((x0, yb + 0.094 * S), 'Right: the two worst of the 36 tilings of the 4×4 board, 7 of 8.', font=it, fill=ink)
    d.text((x0, yb + 0.124 * S), 'exhaustive search · one longest string shown for each · white = left out', font=font('dejavu/DejaVuSansMono.ttf', 0.0098 * S), fill=(132, 118, 146))
    canvas.save(out); print('saved', out)
