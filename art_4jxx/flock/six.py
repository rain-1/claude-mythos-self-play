"""One flock seen from six places: python3 six.py base.json out.png PANEL"""
import sys, json, subprocess, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "..")
from caption import caption, font, INK, CORAL
base = json.load(open(sys.argv[1])); out = sys.argv[2]; P = int(sys.argv[3])
yaws = [0, 60, 120, 180, 240, 300]
tiles = []
for k, yw in enumerate(yaws):
    c = json.loads(json.dumps(base))
    c["flocks"][0]["yaw"] = yw
    c["horizon"] = 0.86; c["fov"] = 50
    c["flocks"][0]["pos"] = [0, 150, 700]
    c["fg"] = {"reeds": []}
    c["sun"] = [0.15 + 0.7 * ((yw / 360 + 0.3) % 1), 0.84]
    json.dump(c, open(f"six_{k}.json", "w"))
procs = [subprocess.Popen(["python3", "scene.py", f"six_{k}.json", f"six_{k}.png", str(P)]) for k in range(6)]
for p in procs: p.wait()
gap = int(P * 0.05); W = 3 * P + 4 * gap; band = int(W * 0.16)
H = 2 * int(P * 0.78) + 3 * gap + band
img = Image.new("RGB", (W, H), (249, 249, 251))
ph = int(P * 0.78)
for k in range(6):
    t = Image.open(f"six_{k}.png").crop((0, int(P * 0.10), P, int(P * 0.10) + ph))
    x = gap + (k % 3) * (P + gap); y = gap + (k // 3) * (ph + gap)
    img.paste(t, (x, y))
    d = ImageDraw.Draw(img)
    d.text((x + int(P * 0.03), y + int(P * 0.025)), f"{yaws[k]}°", font=font("ital", P * 0.05), fill=INK)
s = W / 4096
y0 = 2 * ph + 3 * gap
caption(img, gap + int(20 * s), y0 + int(0.06 * band), int(2800 * s), "One Flock, Six Shapes",
        "The same 1,500,000 starlings at the same instant, seen by six walkers spaced around the lake.",
        "the birds are spread evenly through their sheet (a volume-preserving flow); a dark seam is the sheet seen edge-on, so it moves when you do",
        scale=s * 1.0, series="SOMETHING WE PROJECT ONTO IT  ·  II")
# little map: the flock seen from above with six walkers around it
d = ImageDraw.Draw(img)
cx, cy, R = int(W - 380 * s), int(y0 + band * 0.52), int(220 * s)
d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(190, 180, 200), width=max(1, int(3 * s)))
Pts = np.load(base["flocks"][0]["file"])[::300].astype(float)
Pts = Pts - np.median(Pts, 0)
ax, ay, az = np.radians(base["flocks"][0]["rot"])
Rx = np.array([[1, 0, 0], [0, np.cos(ax), -np.sin(ax)], [0, np.sin(ax), np.cos(ax)]])
Ry = np.array([[np.cos(ay), 0, np.sin(ay)], [0, 1, 0], [-np.sin(ay), 0, np.cos(ay)]])
Rz = np.array([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]])
Pts = Pts @ (Rz @ Ry @ Rx).T
sc = R * 0.55 / np.percentile(np.abs(Pts[:, [0, 2]]), 99)
for p in Pts:
    d.point((cx + p[0] * sc, cy + p[2] * sc), fill=(150, 130, 175))
d.text((cx - 95 * s, cy + R + 40 * s), "seen from above", font=font("ital", 26 * s), fill=(128, 110, 136))
for k, yw in enumerate(yaws):
    # rotating the flock by +yaw = the walker standing at (sin yaw, -cos yaw) in the flock's frame
    th = np.radians(yw)
    a = np.arctan2(-np.cos(th), np.sin(th))
    x, y = cx + R * np.cos(a), cy + R * np.sin(a)
    r = 15 * s
    d.ellipse([x - r, y - r, x + r, y + r], fill=CORAL)
    d.text((x + 1.5 * r * np.cos(a) - 18 * s, y + 1.6 * r * np.sin(a) - 16 * s), f"{yw}°", font=font("reg", 26 * s), fill=INK)
img.save(out); print("saved", out, img.size)
