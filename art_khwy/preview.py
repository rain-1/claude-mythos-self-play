"""Quick contact-sheet preview of a single-cycle arrangement."""
import numpy as np, sys
from PIL import Image, ImageDraw
from polylib import forced_graph, crossings

def draw(theta, r, fname, S=900):
    n = len(theta)
    comps, edges, nbr = forced_graph(theta, r)
    X, Y, T = crossings(theta, r)
    iu = np.triu_indices(n, 1)
    px, py = X[iu], Y[iu]
    cx, cy = px.mean(), py.mean()
    rad = np.sqrt((px-cx)**2+(py-cy)**2)
    R = np.percentile(rad, 97) * 1.15
    def w2s(x, y):
        return (S/2 + (x-cx)/R*S/2*0.92, S/2 - (y-cy)/R*S/2*0.92)
    img = Image.new("RGB", (S, S), (12, 12, 16))
    d = ImageDraw.Draw(img)
    # lines faint
    ct, st = np.cos(theta), np.sin(theta)
    for i in range(n):
        p0 = np.array([ct[i]*r[i], st[i]*r[i]])
        dirv = np.array([-st[i], ct[i]])
        a = p0 + dirv*R*4; b = p0 - dirv*R*4
        d.line([w2s(*a), w2s(*b)], fill=(50, 50, 60), width=1)
    # polygon edges
    P = {}
    for i in range(n):
        for j in range(i+1, n):
            P[i*n+j] = (X[i, j], Y[i, j])
    for (u, v) in edges:
        d.line([w2s(*P[u]), w2s(*P[v])], fill=(240, 190, 90), width=3)
    for v, (x, y) in P.items():
        sx, sy = w2s(x, y)
        d.ellipse([sx-3, sy-3, sx+3, sy+3], fill=(250, 240, 210))
    img.save(fname)
    print(fname, "comps:", comps)

if __name__ == "__main__":
    tag = sys.argv[1]; n = int(sys.argv[2])
    theta = np.load(f"{tag}_n{n}_theta.npy"); r = np.load(f"{tag}_n{n}_r.npy")
    draw(theta, r, f"preview_{tag}_{n}.png")
