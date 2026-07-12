"""THE LOOM OF BROWN — Karhunen-Loeve anatomy of one Brownian bridge.

B(t) = sum_k Z_k sqrt(2) sin(k pi t)/(k pi),  Z_k iid N(0,1).

Rows: knowledge stages m = 0,1,2,4,...,512,inf. In row m the first m dice
Z_1..Z_m of THE bridge are known: gold thread = conditional mean (partial sum
S_m), ice fog = exact conditional law of the remainder (fresh tail dice).
The fog narrows as 1/sqrt(m); the gold thread grows its jaggedness. The last
row is the bridge alone: fully known, fully particular.

Usage: python3 kl_loom.py proto|final
"""
import os, sys, time
import numpy as np
from scipy.ndimage import gaussian_filter
from raster import splat_points, sample_polyline, filmic, save_png, downscale

def bridge_from_dice(Z, tgrid):
    """Sum Z_k sqrt2 sin(k pi t)/(k pi) vectorized: (nZ,) x (T,) -> (T,)."""
    K = len(Z)
    k = np.arange(1, K + 1)
    # (T,K) sin matrix is big; chunk over k
    out = np.zeros(len(tgrid))
    for k0 in range(0, K, 512):
        kk = k[k0:k0 + 512]
        out += (np.sqrt(2) * np.sin(np.outer(tgrid, kk * np.pi)) /
                (kk * np.pi)) @ Z[k0:k0 + 512]
    return out

def render(mode="proto"):
    if mode == "proto":
        W, H, SS = 800, 1100, 2
        NFOG, T = 700, 900
    else:
        W, H, SS = 2560, 3520, 2
        NFOG, T = 2200, 2600
    Wb, Hb = W * SS, H * SS
    K = 2048
    stages = [0, 1, 2, 4, 8, 16, 64, 256, None]  # None = the bare path
    nrows = len(stages)

    rng_hero = np.random.default_rng(20260712)
    Z = rng_hero.standard_normal(K)          # THE dice of the hero bridge
    tg = np.linspace(0, 1, T)
    S_full = bridge_from_dice(Z, tg)

    # precompute mode matrix in chunks for fog tails
    acc_fog = np.zeros((Hb, Wb), np.float32)
    acc_gold = np.zeros((Hb, Wb), np.float32)
    acc_env = np.zeros((Hb, Wb), np.float32)

    x_margin = 0.05 * Wb
    xs = x_margin + tg * (Wb - 2 * x_margin)
    pitch = Hb / (nrows + 0.8)
    A = 1.55 * pitch          # canvas px per unit bridge value
    rng_fog = np.random.default_rng(555)

    t0 = time.time()
    sin_cache = {}
    def partial(Zvec, upto):
        return bridge_from_dice(Zvec[:upto], tg) if upto > 0 else np.zeros(T)

    for i, m in enumerate(stages):
        yc = pitch * (i + 0.9)
        if m is None:
            gold = S_full
            fog_n = 0
        else:
            gold = partial(Z, m)
            fog_n = NFOG
        # gold thread (polyline-resampled so jagged rows stay continuous)
        ys = yc - gold * A
        smp, mm = sample_polyline(np.stack([xs, ys], axis=1), 0.7)
        splat_points(acc_gold, smp[:, 0], smp[:, 1], 4.2 * mm)
        # exact conditional 1.5-sigma envelope, hairline (only once the tube
        # is narrow enough that the law needs a witness)
        if m is not None and m >= 4:
            kk = np.arange((0 if m is None else m) + 1, K + 1)
            sig = np.sqrt((2 * np.sin(np.outer(tg, kk * np.pi)) ** 2 /
                           (kk * np.pi) ** 2).sum(axis=1))
            for sgn in (+1, -1):
                ye = yc - (gold + sgn * 1.5 * sig) * A
                se, me = sample_polyline(np.stack([xs, ye], axis=1), 0.7)
                splat_points(acc_env, se[:, 0], se[:, 1], 0.9 * me)
        # fog: conditional samples share Z_1..Z_m, fresh tail
        if fog_n:
            tail_k = np.arange(m + 1, K + 1)
            # build fog in chunks of samples
            for c0 in range(0, fog_n, 64):
                nc = min(64, fog_n - c0)
                Zt = rng_fog.standard_normal((nc, K - m))
                # (nc, T): chunk over k
                paths = np.tile(gold, (nc, 1))
                for k0 in range(0, K - m, 512):
                    kk = tail_k[k0:k0 + 512]
                    Msin = (np.sqrt(2) * np.sin(np.outer(tg, kk * np.pi)) /
                            (kk * np.pi)).astype(np.float32)
                    paths += Zt[:, k0:k0 + 512] @ Msin.T
                for j in range(nc):
                    yf = yc - paths[j] * A
                    sf, mf = sample_polyline(np.stack([xs, yf], axis=1), 0.9)
                    splat_points(acc_fog, sf[:, 0], sf[:, 1], mf)
        print(f"row {i} (m={m}) done {time.time()-t0:.0f}s")

    # tone: fog ice-blue, gold thread warm
    fog = acc_fog / max(1, NFOG)
    kf = 1.45 / np.percentile(fog[fog > 0], 99.5) if (fog > 0).any() else 1
    Lf = filmic(fog * kf, 1.0)
    gold = acc_gold
    kg = 1.0 / np.percentile(gold[gold > 0], 92)
    Lg = np.clip(gold * kg, 0, 1.6)
    # fog hue drifts cold steel -> slate violet as knowledge deepens
    rowpos = np.linspace(0, 1, Hb, dtype=np.float32)[:, None]
    c_top = np.array([0.40, 0.63, 0.88], np.float32)
    c_bot = np.array([0.55, 0.52, 0.86], np.float32)
    c_fog = c_top[None, None] * (1 - rowpos)[..., None] + c_bot[None, None] * rowpos[..., None]
    c_fog = c_fog[:, 0]  # (Hb,3), broadcast over width
    c_gold = np.array([1.00, 0.80, 0.38], np.float32)
    c_env = np.array([0.30, 0.85, 0.80], np.float32)
    ke = 0.9 / max(np.percentile(acc_env[acc_env > 0], 95), 1e-9) if (acc_env > 0).any() else 0
    Le = filmic(acc_env * ke, 1.0)
    rgb = (Lf[..., None] * c_fog[:, None, :] + np.clip(Lg, 0, 1.4)[..., None] * c_gold
           + 0.5 * Le[..., None] * c_env)
    # bloom the gold
    bl = gaussian_filter(np.clip(Lg - 0.5, 0, None), Wb / 500)
    rgb += bl[..., None] * c_gold * 0.8
    rgb = 1 - np.exp(-rgb * 1.1)
    rgb = np.clip(rgb, 0, 1) ** 0.95
    from PIL import Image
    img = Image.fromarray((rgb * 255).astype(np.uint8))
    img = img.resize((W, H), Image.LANCZOS)
    outdir = os.path.join(os.path.dirname(__file__), "proto" if mode == "proto" else ".")
    path = os.path.join(outdir, f"loom_{mode}.png")
    img.save(path)
    print("saved", path)

if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else "proto")
