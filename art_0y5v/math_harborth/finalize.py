"""Exact verification + export of the chosen drawings.
Each drawing is given by integer lattice coordinates (x, y) standing for the point
(x/s, y*sqrt(k)/s).  Squared edge length = (dx^2 + k dy^2)/s^2, checked to be a perfect integer square.
Planarity is checked exactly on the integer (x, y) (the map (x,y)->(x/s, y sqrt(k)/s) is affine with
positive determinant, so crossings, collinearity, betweenness and orientations are preserved)."""
import json, math, sys
sys.path.insert(0, '.')
from common import is_plane, faces_from_drawing, orient, min_angle_deg
import graphs

def check(name, edges, k, s, XY, nverts):
    assert len(XY) == nverts
    ok, why = is_plane(XY, edges)
    assert ok, (name, why)
    out_edges = []
    for a, b in edges:
        num = (XY[a][0]-XY[b][0])**2 + k*(XY[a][1]-XY[b][1])**2
        assert num % (s*s) == 0, (name, a, b)
        q = num // (s*s); r = math.isqrt(q)
        assert r*r == q and r > 0, (name, a, b, num)
        out_edges.append([a, b, r])
    faces = faces_from_drawing(XY, edges)        # CCW, bounded faces, exact integer arithmetic
    n, m = nverts, len(edges)
    assert m == 3*n - 6 and len(faces) == m - n + 1, (name, len(faces))  # maximal planar, all faces triangles
    # outer face = the triangle not listed (convex hull)
    real = [(x/s, y*math.sqrt(k)/s) for x, y in XY]
    ang = min_angle_deg(real, faces)
    def exact(c, rad):
        from fractions import Fraction
        f = Fraction(c, s)
        txt = str(f)
        return txt if rad == 1 or c == 0 else f"{txt}*sqrt({rad})"
    return dict(name=name, field=("Q" if k == 1 else f"Q(sqrt({k}))"),
                vertices=[[round(x, 4), round(y, 4)] for x, y in real],
                vertices_exact=[[exact(x, 1), exact(y, k)] for x, y in XY],
                edges=out_edges, faces=[list(f) for f in faces],
                max_edge=max(e[2] for e in out_edges), min_angle_deg=round(ang, 2))

if __name__ == "__main__":
    spec = json.load(open('chosen.json'))
    res = []
    for d in spec:
        n, edges, _ = getattr(graphs, d['graph'])()
        r = check(d['name'], edges, d['k'], d['s'], [tuple(p) for p in d['xy']], n)
        res.append(r)
        print(r['name'], r['field'], 'max edge', r['max_edge'], 'min angle', r['min_angle_deg'], 'VERIFIED')
    json.dump(res, open('drawings.json', 'w'), indent=1)
