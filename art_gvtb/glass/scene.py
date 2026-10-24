"""Compose the suncatcher window: python3 scene.py cfg.json out.png"""
import numpy as np, json, sys, time, os
from scipy import ndimage
from PIL import Image
import scene_data as SD
from tracer import photon_map, render

# sorbet wheel (sRGB) — strawberry, peach, butter, lime, mint, sky, periwinkle, lilac, bubblegum
WHEEL = np.array([
    [0.98, 0.55, 0.62], [1.00, 0.72, 0.55], [1.00, 0.90, 0.52], [0.78, 0.92, 0.52],
    [0.55, 0.90, 0.75], [0.55, 0.82, 0.98], [0.62, 0.66, 0.98], [0.80, 0.62, 0.95],
    [0.98, 0.60, 0.85]])


def wheel(t):
    t = (t % 1) * len(WHEEL)
    i = int(t); f = t - i
    a = WHEEL[i % len(WHEEL)]; b = WHEEL[(i + 1) % len(WHEEL)]
    return np.exp(np.log(a) * (1 - f) + np.log(b) * f)


def lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def build(cfg):
    az, lat = SD.face_colours()
    nF = len(SD.F)
    rng = np.random.default_rng(cfg.get('cseed', 5))
    FT = np.zeros((nF, 3))
    for k in range(nF):
        c = wheel(az[k] + cfg.get('hoff', 0.0) + 0.02 * rng.standard_normal())
        s = cfg.get('sat', 0.85) * (0.75 + 0.25 * lat[k]) * (0.9 + 0.2 * rng.random())
        c = 1 - s * (1 - c)
        FT[k] = lin(c) ** cfg.get('tpow', 1.0)
    FT = np.r_[FT ** cfg.get('ppow', 1.6), FT]
    drs = SD.drawings()
    K = len(cfg['panels'])
    res = cfg.get('res', 1400)
    FID = np.zeros((K, res, res), np.int16); LEAD = np.zeros((K, res, res), np.float32)
    HW = np.zeros((K, res, res), np.float32); RG = np.zeros((K, res, res), np.float32)
    TH = []
    PO = np.zeros((K, 3)); PU = np.zeros((K, 3)); PV = np.zeros((K, 3)); PN = np.zeros((K, 3))
    for k, pc in enumerate(cfg['panels']):
        name, outer, P = drs[pc['draw']]
        Q = SD.normalise(P, outer, pc.get('apex_up', True))
        if pc.get('mirror', False):
            Q[:, 0] *= -1
        fid, ld, hw, h, half = SD.panel_texture(Q, outer, res, lead=cfg.get('lead', 0.0075),
                                                frame=cfg.get('frame', 0.016), seed=k + 11)
        FID[k] = fid; LEAD[k] = ld; HW[k] = hw; RG[k] = h
        yaw = np.radians(pc.get('yaw', 0)); size = pc.get('size', 1.0)
        u = np.array([np.cos(yaw), np.sin(yaw), 0.0])
        v = np.array([0, 0, 1.0])
        nrm = np.cross(u, v)
        PO[k] = pc['pos']; PU[k] = u / size; PV[k] = v / size; PN[k] = nrm
        A, B, C = Q[list(outer)]
        tops = sorted([A, B, C], key=lambda q: -q[1])
        tops = tops[:1] if pc.get('apex_up', True) else tops[:2]
        for q in tops:
            p3 = np.array(pc['pos']) + u * q[0] * size + v * q[1] * size
            TH.append([p3[0], p3[1], p3[2] - 0.004, cfg.get('thread', 0.0035)])
    # globe
    g = cfg['globe']
    gc = np.array(g['pos'], float); R = g['r']
    rot = np.radians(g.get('rot', [0, 0, 0]))
    def Rm(ax, a):
        c, s = np.cos(a), np.sin(a)
        M = np.eye(3); i, j = [(1, 2), (0, 2), (0, 1)][ax]
        M[i, i] = c; M[j, j] = c; M[i, j] = -s; M[j, i] = s
        return M
    M = Rm(2, rot[2]) @ Rm(1, rot[1]) @ Rm(0, rot[0])
    Vg = (SD.V @ M.T) * R
    GN = []; GD = []
    for f in SD.F:
        a, b, c = Vg[list(f)]
        nrm = np.cross(b - a, c - a); nrm /= np.linalg.norm(nrm)
        if nrm @ a < 0:
            nrm = -nrm
        GN.append(nrm); GD.append(nrm @ a)
    GN = np.array(GN); GD = np.array(GD); GF = np.arange(nF) + nF
    gc[2] = -min(Vg[:, 2]) + 0.001  # rest on the sill
    return dict(FT=FT, FID=FID, LEAD=LEAD, HW=HW, RG=RG, PO=PO, PU=PU, PV=PV, PN=PN,
                GN=GN, GD=GD, gc=gc, GF=GF, half=0.62, TH=np.array(TH, float))


def mksp(cfg):
    hz = cfg.get('horizon', [1.0, 0.90, 0.88]); zn = cfg.get('zenith', [0.62, 0.76, 1.0])
    st = cfg.get('star', [0, 1, 0, 0, 0])  # dir xyz, size, power
    sd = np.array(st[:3], float); sd /= np.linalg.norm(sd)
    sc = cfg.get('suncol', [1.0, 0.97, 0.90])
    return np.array([np.radians(0.6), cfg.get('sunpow', 40.0), *hz, *zn, *sd, st[3], st[4], *sc,
                     cfg.get('sunk', 1.0), cfg.get('amb', 0.42), cfg.get('gold', 1.0)], float)


def main(cfg, out):
    S = build(cfg)
    sun = np.array(cfg['sun'], float); sun /= np.linalg.norm(sun)
    YW = cfg['YW']; WIN = np.array(cfg['WIN'], float); TB = np.array(cfg['TB'], float)
    LB = np.array(cfg['LB'], float)
    LW = cfg['LW']; LH = int(LW * (LB[3] - LB[2]) / (LB[1] - LB[0]))
    t = time.time()
    common = (S['PO'], S['PU'], S['PV'], S['PN'], S['FID'], S['LEAD'], S['HW'], S['RG'], S['FT'],
              S['half'], cfg['ramp'], S['GN'], S['GD'], S['gc'], S['GF'], YW, WIN, TB, S['TH'])
    lmfile = cfg.get('lmcache')
    if lmfile and os.path.exists(lmfile):
        LM = np.load(lmfile)
    else:
        LM = photon_map(int(cfg['nphot']), sun, np.radians(cfg['cone']), *common, LB, LH, LW, 1234, 8, mksp(cfg))
        if lmfile:
            np.save(lmfile, LM)
    LM = ndimage.gaussian_filter(LM, (0, cfg.get('lmblur', 1.0), cfg.get('lmblur', 1.0)))
    print('photons', time.time() - t, LM.mean(), flush=True)
    # ambient occlusion: wall corner + globe contact
    xs = np.linspace(LB[0], LB[1], LW); ys = np.linspace(LB[2], LB[3], LH)
    X, Y = np.meshgrid(xs, ys)
    ao = 1 - 0.35 * np.exp(-(YW - Y) / 0.25)
    gc = S['gc']; R = cfg['globe']['r']
    rr = np.hypot(X - gc[0], Y - gc[1]) / R
    ao *= 1 - 0.55 * np.exp(-np.maximum(rr - 0.3, 0) ** 2 / 0.35)
    AO = ao[None].astype(np.float32)
    # camera
    c = cfg['cam']
    eye = np.array(c['eye'], float); tgt = np.array(c['tgt'], float)
    fw = tgt - eye; fd = np.linalg.norm(fw) if 'focus' not in c else c['focus']; fw /= np.linalg.norm(fw)
    rt = np.cross(fw, [0, 0, 1]); rt /= np.linalg.norm(rt); up = np.cross(rt, fw)
    cam = np.r_[eye, fw, rt, up, np.tan(np.radians(c['fov']) / 2), c.get('ap', 0.0), fd]
    H, W = cfg['H'], cfg['W']
    sp = mksp(cfg)
    t = time.time()
    rows = cfg.get('rows', [0, H])
    img = render(H, W, cfg['spp'], cam, *common, LM, LB, AO, sun, sp, 77, rows[0], rows[1])
    print('render', time.time() - t, flush=True)
    np.save(out.replace('.png', '.npy'), img)
    tone(img, cfg, out)


def tone(img, cfg, out):
    ex = cfg.get('exposure', 1.0)
    x = img * ex
    wpt = cfg.get('white', 1.6)
    x = x * (1 + x / wpt ** 2) / (1 + x)
    x = np.clip(x, 0, 1)
    srgb = np.where(x <= 0.0031308, 12.92 * x, 1.055 * x ** (1 / 2.4) - 0.055)
    Image.fromarray((np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out)


if __name__ == '__main__':
    cfg = json.load(open(sys.argv[1]))
    for kv in sys.argv[3:]:
        k, v = kv.split('=')
        cfg[k] = json.loads(v)
    main(cfg, sys.argv[2])
