# Scene setup + render driver for the city. usage: python3 scene.py cfg.json out.npy [y0 y1]
import numpy as np, json, sys, math
from tracer import render

def palette(n=48):
    # Burano-style: one clear sorbet colour per common height, towers walk butter->lime->mint->sky
    base = {0: [0.9, 0.9, 0.9], 1: [1.00, 0.93, 0.70], 2: [1.00, 0.80, 0.64], 3: [0.99, 0.70, 0.72], 4: [0.90, 0.70, 0.92],
            5: [0.72, 0.76, 0.99], 6: [0.64, 0.86, 0.98], 7: [0.62, 0.92, 0.82], 8: [0.82, 0.94, 0.62], 9: [1.00, 0.90, 0.58]}
    P = np.zeros((n, 3))
    tw = np.array([[1.00, 0.88, 0.62], [1.00, 0.76, 0.70], [0.97, 0.70, 0.84], [0.84, 0.74, 0.97], [0.70, 0.82, 0.99]])
    for h in range(n):
        if h in base: P[h] = base[h]
        else:
            x = min((h - 10) / 20, 1) * (len(tw) - 1); i = min(int(x), len(tw) - 2); f = x - i
            P[h] = tw[i] ** (1 - f) * tw[i + 1] ** f
    P = np.clip(1 - (1 - P) * 1.35, 0, 1)
    return P

def lookat(eye, tgt, fov, up=(0, 0, 1)):
    eye = np.array(eye, float); tgt = np.array(tgt, float)
    f = tgt - eye; f /= np.linalg.norm(f)
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return eye, f, r, u, math.tan(math.radians(fov) / 2)

def threads_for(A, i, j, HU, PLH=0.03):
    h = A[i, j]; T = []
    top = (i + .5, j + .5, PLH + HU * h)
    def vis(line, n, h):
        out = []; best = -1e300
        for k in range(n - 1, -1, -1):
            s = (line[k] - h) / (n - k)
            if s >= best - 1e-12: out.append(k)
            best = max(best, s)
        return out
    for k in vis(A[:i, j].astype(float), i, h): T.append(top + (k + .5, j + .5, PLH + HU * A[k, j]))
    for k in vis(A[i, :j].astype(float), j, h): T.append(top + (i + .5, k + .5, PLH + HU * A[i, k]))
    return np.array(T, float)

def main():
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
    W, H = cfg['W'], cfg['H']
    y0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    y1 = int(sys.argv[4]) if len(sys.argv) > 4 else H
    A0 = np.load(cfg['city'])
    n = cfg['n']; A = np.ascontiguousarray(A0[:n, :n]).astype(np.int64)
    HU = cfg['HU']
    hl = np.zeros_like(A)
    thr = np.zeros((0, 6))
    for (i, j) in cfg.get('focus', []):
        hl[i, j] = 1
        thr = np.vstack([thr, threads_for(A, i, j, HU)])
    eye, f, r, u, tanh = lookat(cfg['eye'], cfg['tgt'], cfg['fov'])
    fd = np.linalg.norm(np.array(cfg['focus_pt']) - eye) if 'focus_pt' in cfg else np.linalg.norm(np.array(cfg['tgt']) - eye)
    cam = np.array(list(eye) + list(f) + list(r) + list(u) + [tanh, cfg.get('ap', 0.0), fd, cfg.get('tilt', 0.0)])
    sun = np.array(cfg['sun'], float); sun /= np.linalg.norm(sun)
    hor = cfg.get('horizon', [1.0, 0.90, 0.87]); zen = cfg.get('zenith', [0.70, 0.82, 0.98])
    P = np.array(hor + zen + list(sun) + [cfg.get('sunE', 1.0), cfg.get('skyE', 0.55), cfg.get('amb2', 0.25), cfg.get('sunjit', 0.03)]
                 + cfg.get('thread', [1.4, 0.55, 0.45]) + cfg.get('water', [0.62, 0.80, 0.86]) + cfg.get('suncol', [1.0, 0.96, 0.90])
                 + [cfg.get('haze', 60.0), cfg.get('shallow_d', 2.5)] + cfg.get('shallow', [0.66, 0.94, 0.86]), float)
    tr = cfg.get('trees', [[0.0, 0.0, 0.16, 0.55, 0.11], [0.5, 0.0, 0.14, 0.0, 0.09], [0.5, 0.5, 0.30, 1.01, 0.30]])
    trees = np.ascontiguousarray(np.array(tr, float).T)
    BO = np.array(cfg.get('boats', [[0, 0, 0, 0, 0, 0]]), float)
    if 'boats' not in cfg: BO = BO[:0]
    img = render(W, H, cam, A, HU, palette(), hl, trees, thr, cfg.get('thr_r', 0.012), P, cfg['spp'], y0, y1, cfg.get('seed', 1), BO)
    np.save(out, img)

if __name__ == '__main__':
    main()
