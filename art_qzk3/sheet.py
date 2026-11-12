"""Sixty-four tides: one six-bridge sub-cube of the 8192 outcomes, exactly 32 of them connected,
laid out so that neighbouring pictures (and the wrap-around) differ by one bridge.
usage: python3 sheet.py pick | python3 sheet.py tiles A B (render tiles A..B-1) | python3 sheet.py compose OUT"""
import sys, os, itertools, json, numpy as np
from PIL import Image
from islands import EDGES, FRAME, reach, render
TS = 508; GAP = 22; G = [0, 1, 3, 2, 6, 7, 5, 4]
def conn(m): return len(reach(m)) == 7
def pick():
    C = [conn(m) for m in range(8192)]; best = None
    for free in itertools.combinations(range(13), 6):
        fixed = [k for k in range(13) if k not in free]
        for fm in range(128):
            base = sum(1 << fixed[i] for i in range(7) if fm >> i & 1)
            ms = [base | sum(1 << free[i] for i in range(6) if sub >> i & 1) for sub in range(64)]
            if sum(C[m] for m in ms) != 32: continue
            infl = [sum(C[m] != C[m ^ (1 << e)] for m in ms) for e in free]
            # every coin should matter, and about equally; prefer few forced-absent bridges
            score = (min(infl), -max(infl), bin(fm).count('1'))
            if best is None or score > best[0]: best = (score, free, base, infl)
    json.dump(dict(free=best[1], base=best[2], influence=best[3]), open('sheet_pick.json', 'w'))
    print(best)
def cells():
    p = json.load(open('sheet_pick.json')); free = p['free']; base = p['base']; out = []
    for r in range(8):
        for c in range(8):
            sub = G[c] | (G[r] << 3)
            out.append(base | sum(1 << free[i] for i in range(6) if sub >> i & 1))
    return out
if __name__ == '__main__':
    if sys.argv[1] == 'pick': pick()
    elif sys.argv[1] == 'tiles':
        os.makedirs('tiles', exist_ok=True); cs = cells()
        for n in range(int(sys.argv[2]), int(sys.argv[3])):
            S = render(TS, None, cs[n], seed=3, title=False, pseed=100 + n)
            x0, y0, x1, y1 = FRAME; a = np.clip(S.img, 0, 1)
            crop = a[int(y0 * TS) - 1:int(y1 * TS) + 2, int(x0 * TS) - 1:int(x1 * TS) + 2]
            Image.fromarray((crop * 255 + .5).astype(np.uint8)).save(f'tiles/t{n:02d}.png'); print(n, flush=True)
    else:
        from hanga import Sheet, INK, SERIF_B, SERIF_I, SERIF
        S = Sheet(4096, seed=21); cs = cells(); t0 = np.asarray(Image.open('tiles/t00.png')); th, tw = t0.shape[:2]
        gw = 8 * tw + 7 * GAP; x0 = (4096 - gw) // 2; y0 = 92
        suns = 0
        for n in range(64):
            r, c = divmod(n, 8); t = np.asarray(Image.open(f'tiles/t{n:02d}.png'), np.float32) / 255
            S.img[y0 + r * (th + GAP):y0 + r * (th + GAP) + th, x0 + c * (tw + GAP):x0 + c * (tw + GAP) + tw] = t
            suns += conn(cs[n])
        assert suns == 32, suns
        yb = (y0 + 8 * th + 7 * GAP) / 4096; xl = x0 / 4096; xr = (x0 + gw) / 4096
        cap = S.text_mask([(xl, yb + 0.030, 'Sixty-Four Tides', SERIF_B, 0.0215, 'ls'),
            (xl, yb + 0.054, 'Seven bridges are settled and six are left to the coin. Step to the next picture, in any direction, and one bridge changes.', SERIF_I, 0.0152, 'ls'),
            (xl, yb + 0.074, 'The sun comes out when every island can still be reached on foot: thirty-two suns.', SERIF_I, 0.0152, 'ls'),
            (xr, yb + 0.030, 'MO 516850', SERIF, 0.0125, 'rs')])
        S.key(cap, strength=0.88, rough=0.25)
        S.save(sys.argv[2])
