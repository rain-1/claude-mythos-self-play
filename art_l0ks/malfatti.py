#!/usr/bin/env python3
"""Malfatti's 1803 symmetric answer vs the greedy packing that always beats it
(Lob-Richmond 1930 counterexamples; Zalgaller-Los 1994: greedy is optimal for 3 circles).

Triangle with angles A,B,C (A<=B<=C), unit inradius WLOG.
Greedy: incircle r; then corner circle at smallest angle r*k(A)^2... careful:
corner circle in angle A tangent to incircle: k(A) = (1-sin(A/2))/(1+sin(A/2)),
radius = r*k(A). Third: max(corner at B, second nested circle in corner A = r*k(A)^2).
Malfatti: three circles each tangent to two sides + other two circles (Newton solve).
"""
import numpy as np, math, json

def triangle_geometry(A, B, C):
    """Unit inradius; returns vertices, incenter at origin."""
    # side lengths proportional: a = r*(cot(B/2)+cot(C/2)) etc with r=1
    cot = lambda x: 1.0/math.tan(x)
    a = cot(B/2)+cot(C/2); b = cot(A/2)+cot(C/2); c = cot(A/2)+cot(B/2)
    # place: vertex A at origin-ish; easier: place side c on x-axis: A=(0,0), B=(c,0)
    VA = np.array([0.0, 0.0]); VB = np.array([c, 0.0])
    VC = np.array([b*math.cos(A), b*math.sin(A)])
    I = np.array([ (a*VA[0]+b*VB[0]+c*VC[0])/(a+b+c), (a*VA[1]+b*VB[1]+c*VC[1])/(a+b+c) ])
    return VA, VB, VC, I

def greedy(A, B, C):
    """returns list of (center, radius) with unit inradius; A<=B<=C assumed."""
    VA, VB, VC, I = triangle_geometry(A, B, C)
    r = 1.0
    k = lambda X: (1-math.sin(X/2))/(1+math.sin(X/2))
    rA = r*k(A); rB = r*k(B); rA2 = r*k(A)**2
    circles = [(I, r)]
    # corner circle at A: on bisector of A at distance rad/sin(A/2) from vertex
    def corner(V, other1, other2, half, rad):
        d1 = (other1-V)/np.linalg.norm(other1-V); d2 = (other2-V)/np.linalg.norm(other2-V)
        bis = (d1+d2); bis /= np.linalg.norm(bis)
        return V + bis*(rad/math.sin(half))
    cA = corner(VA, VB, VC, A/2, rA)
    circles.append((cA, rA))
    if rB >= rA2:
        circles.append((corner(VB, VA, VC, B/2, rB), rB))
        third = 'cornerB'
    else:
        circles.append((corner(VA, VB, VC, A/2, rA2), rA2))
        third = 'nestedA'
    return circles, third

def malfatti(A, B, C):
    """Newton solve for the three Malfatti radii; returns circles."""
    VA, VB, VC, I = triangle_geometry(A, B, C)
    Vs = [VA, VB, VC]; angs = [A, B, C]
    others = [(VB, VC), (VA, VC), (VA, VB)]
    def centers(rs):
        cs = []
        for V, (P, Q), ang, rr in zip(Vs, others, angs, rs):
            d1 = (P-V)/np.linalg.norm(P-V); d2 = (Q-V)/np.linalg.norm(Q-V)
            bis = d1+d2; bis /= np.linalg.norm(bis)
            cs.append(V + bis*(rr/math.sin(ang/2)))
        return cs
    def F(rs):
        cs = centers(rs)
        return np.array([
            np.linalg.norm(cs[0]-cs[1]) - (rs[0]+rs[1]),
            np.linalg.norm(cs[1]-cs[2]) - (rs[1]+rs[2]),
            np.linalg.norm(cs[0]-cs[2]) - (rs[0]+rs[2])])
    rs = np.array([0.5, 0.5, 0.5])
    for _ in range(80):
        f = F(rs)
        J = np.zeros((3, 3)); h = 1e-8
        for j in range(3):
            rp = rs.copy(); rp[j] += h
            J[:, j] = (F(rp)-f)/h
        step = np.linalg.solve(J, -f)
        rs = rs + np.clip(step, -0.2, 0.2)
        if np.abs(f).max() < 1e-13:
            break
    cs = centers(rs)
    return list(zip(cs, rs)), np.abs(F(rs)).max()

def areas(A, B, C):
    g, third = greedy(A, B, C)
    m, resid = malfatti(A, B, C)
    ag = sum(r*r for _, r in g)*math.pi
    am = sum(r*r for _, r in m)*math.pi
    return ag, am, third, resid

if __name__ == '__main__':
    # equilateral exact check
    E = math.pi/3
    ag, am, third, resid = areas(E, E, E)
    r_m_exact = None
    # unit inradius equilateral: side = 2*sqrt(3); malfatti radius exact = side/(2(1+sqrt3)) * ... check numerically
    print(f"equilateral: greedy={ag:.10f}  malfatti={am:.10f}  greedy/malfatti={ag/am:.10f} third={third} resid={resid:.1e}")
    # closed-form check: unit-inradius equilateral: r_greedy = [1, 1/3, 1/3] -> area = pi*(1+2/9)
    print(f"  greedy exact = pi*11/9 = {math.pi*11/9:.10f}")
    # Malfatti exact for equilateral, unit inradius: side s = 2*sqrt(3), r_m = s/(2(1+sqrt(3)))
    s = 2*math.sqrt(3); rm = s/(2*(1+math.sqrt(3)))
    print(f"  malfatti exact = 3*pi*rm^2 = {3*math.pi*rm*rm:.10f}")
    # scan shape space: angles A<=B<=C, param by (A,B)
    N = 160
    grid = []
    for i in range(N):
        for j in range(N):
            A = 1e-3 + (math.pi/3 - 2e-3)*i/(N-1)
            Bmax = (math.pi - A)/2
            B = A + (Bmax - A)*j/(N-1)
            C = math.pi - A - B
            if B > C + 1e-12: continue
            try:
                ag, am, third, resid = areas(A, B, C)
                if resid < 1e-8:
                    grid.append((A, B, ag/am, third))
            except Exception:
                pass
    arr = np.array([(a, b, g) for a, b, g, t in grid])
    print(f"scan: {len(grid)} triangles, gap range {arr[:,2].min():.6f} .. {arr[:,2].max():.6f}")
    worst = arr[np.argmax(arr[:, 2])]
    print(f"max greedy/malfatti = {worst[2]:.6f} at A={worst[0]:.4f} B={worst[1]:.4f}")
    n_violate = (arr[:, 2] < 1.0-1e-9).sum()
    print(f"violations of greedy>=malfatti: {n_violate}")
    np.save('malfatti_grid.npy', np.array([(a, b, g, 1.0 if t == 'nestedA' else 0.0) for a, b, g, t in grid]))
    json.dump({'equilateral_ratio': ag/am if False else areas(E,E,E)[0]/areas(E,E,E)[1]},
              open('malfatti.json', 'w'))
