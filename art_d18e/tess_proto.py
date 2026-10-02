import numpy as np, pickle, math, itertools, sys
from PIL import Image
from clay import render
from sorbet import PIG
res = pickle.load(open('tess261.pkl', 'rb'))
ROT = []
for perm in itertools.permutations(range(3)):
    for sg in itertools.product((1, -1), repeat=3):
        M = np.zeros((3, 3), int)
        for a in range(3): M[a, perm[a]] = sg[a]
        ROT.append(M)
def orient(P):
    best = None
    for M in ROT:
        Q = P @ M.T; Q = Q - Q.min(0)
        ext = Q.max(0)
        key = (-ext[0], ext[2], -ext[1], tuple(np.sort(Q[:, 2])), tuple(map(tuple, Q[np.lexsort(Q.T)])))
        if best is None or key < best[0]: best = (key, Q)
    return best[1]
PAIRHUE = ['strawberry', 'butter', 'mint', 'periwinkle']
def colours(r, Q):
    axes = [c[0] for c in r['cells']]
    # order pairs by mean x of the pair
    mx = [np.mean([Q[i, 0] + 0.3 * Q[i, 2] for i in range(8) if axes[i] == a]) for a in range(4)]
    order = np.argsort(mx)
    col = np.zeros((8, 3))
    for rank, a in enumerate(order):
        base = np.array(PIG[PAIRHUE[rank]]) ** 0.85
        for i in range(8):
            if axes[i] == a:
                col[i] = base if r['cells'][i][1] > 0 else base ** 1.6
    return col
if __name__ == '__main__':
    ids = list(map(int, sys.argv[1].split(','))); S = int(sys.argv[2])
    tiles = []
    for k in ids:
        r = res[k]; Q = orient(r['pos'])
        col = colours(r, Q)
        c = Q.mean(0) + 0.5
        img, m = render(Q.astype(np.float64), col, S, S, c[0], c[1], S / 6.2, math.radians(-58), math.radians(34),
                        np.array([-0.45, 0.35, 0.82]) / np.linalg.norm([-0.45, 0.35, 0.82]), 12, 12, np.array([0.985, 0.975, 0.965]))
        tiles.append(img)
    T = np.concatenate(tiles, 1)
    srgb = np.where(T <= 0.0031308, 12.92 * T, 1.055 * np.clip(T, 0, None) ** (1 / 2.4) - 0.055)
    Image.fromarray((np.clip(srgb, 0, 1) * 255).astype(np.uint8)).save('proto_tess.png')
