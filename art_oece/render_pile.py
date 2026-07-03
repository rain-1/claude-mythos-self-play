"""Render the stabilized sandpile: height field (0..3) -> colour.

The pattern's regions are big smooth patches of periodic height-texture
separated by fractal filigree curves.  Palette choices decide everything;
we iterate on a cached array (craft note: cache the raw field, iterate the
colormap in seconds).
"""
import numpy as np
import sys, os, time
from PIL import Image
from scipy.ndimage import gaussian_filter

SCRATCH = "/tmp/claude-0/-home-user-claude-mythos-self-play/14486fce-1a7e-527f-9de4-a144326c3b0e/scratchpad"

PALETTES = {
    # h=0, 1, 2, 3
    "classic":  [(38, 38, 66), (86, 132, 190), (222, 176, 90), (250, 245, 228)],
    "ember":    [(12, 10, 26), (118, 32, 60), (232, 118, 46), (255, 224, 160)],
    "veridian": [(8, 14, 20), (18, 84, 84), (120, 196, 154), (248, 244, 210)],
    "nocturne": [(6, 6, 14), (44, 48, 118), (140, 90, 190), (245, 210, 120)],
    "porcelain":[(24, 30, 40), (70, 110, 130), (180, 200, 200), (255, 250, 240)],
    "goldblue": [(10, 12, 28), (30, 70, 140), (235, 180, 70), (250, 248, 235)],
}

def render(h, name, pal, S_out=None, glow3=0.0, vignette=True, pad_to=None):
    t0 = time.time()
    cols = np.array(pal, np.float32) / 255.0
    img = cols[h]  # (H, W, 3)
    if glow3 > 0:
        m = (h == 3).astype(np.float32)
        g = gaussian_filter(m, 3.0)
        img += glow3 * g[..., None] * (cols[3] * 0.9)
    if pad_to and pad_to > h.shape[0]:
        P = pad_to
        out = np.zeros((P, P, 3), np.float32)
        out[:] = cols[0] * 0.55   # void slightly darker than h=0
        o = (P - h.shape[0]) // 2
        out[o:o + h.shape[0], o:o + h.shape[1]] = img
        img = out
    if vignette:
        P = img.shape[0]
        yy, xx = np.mgrid[0:P, 0:P]
        r = np.hypot(yy - P / 2, xx - P / 2) / (P / 2)
        img *= (1 - 0.16 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None]
    img = np.clip(img, 0, 1)
    im = Image.fromarray((img * 255).astype(np.uint8))
    if S_out and S_out != img.shape[0]:
        im = im.resize((S_out, S_out), Image.LANCZOS)
    fn = os.path.join(SCRATCH, f"pile_{name}.png")
    im.save(fn)
    print(fn, f"{time.time()-t0:.1f}s", flush=True)

AZURE = [(18, 40, 80), (255, 210, 120), (70, 130, 200), (10, 14, 30)]
VOID = np.array([7, 7, 14], np.float32) / 255

def render_hero(h_folded_path, u_folded_path, out_path, canvas=4096):
    """Final hero: unfold the folded pile, azure palette, void mask via the
    odometer, gold bloom on the h=1 lace, pad to canvas."""
    from sandpile import unfold
    t0 = time.time()
    h = unfold(np.load(h_folded_path).astype(np.uint8))
    u = unfold(np.load(u_folded_path))
    void = (u == 0) & (h == 0)
    del u
    cols = np.array(AZURE, np.float32) / 255.0
    img = cols[h]
    img[void] = VOID
    m = (h == 1).astype(np.float32)
    g = gaussian_filter(m, 2.2) * (2 * np.pi * 2.2 ** 2)
    img += 0.30 * np.clip(g, 0, 1)[..., None] * np.array([1.0, 0.82, 0.45], np.float32)
    img = np.clip(img, 0, 1)
    S = img.shape[0]
    if canvas > S:
        out = np.empty((canvas, canvas, 3), np.float32)
        out[:] = VOID
        o = (canvas - S) // 2
        out[o:o + S, o:o + S] = img
        img = out
    elif canvas < S:
        o = (S - canvas) // 2
        img = img[o:o + canvas, o:o + canvas]
    Image.fromarray((img * 255).astype(np.uint8)).save(out_path)
    print(out_path, f"grid={S}", f"{time.time()-t0:.1f}s", flush=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "hero":
        render_hero(SCRATCH + "/pile_folded_h.npy", SCRATCH + "/pile_folded_u.npy",
                    "/home/user/claude-mythos-self-play/art_oece/01_the_grain_and_the_mandala.png")
    else:
        h = np.load(SCRATCH + "/pile22_h.npy")
        for name, pal in PALETTES.items():
            render(h, name, pal, S_out=814, pad_to=1700)
