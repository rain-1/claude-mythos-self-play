# Fair length of right regular n-gon prism (circumradius R=1) under the solid-angle model.
import mpmath as mp
mp.mp.dps = 40

def tri_solid(r1, r2, r3):
    # Van Oosterom-Strackee
    def dot(a,b): return sum(x*y for x,y in zip(a,b))
    def cross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    n1,n2,n3 = [mp.sqrt(dot(r,r)) for r in (r1,r2,r3)]
    num = dot(r1, cross(r2,r3))
    den = n1*n2*n3 + dot(r1,r2)*n3 + dot(r1,r3)*n2 + dot(r2,r3)*n1
    return 2*mp.atan2(num, den)

def verts(n, z):
    return [(mp.cos(2*mp.pi*k/n), mp.sin(2*mp.pi*k/n), z) for k in range(n)]

def cap_vos(n, h):
    # sum of n triangles fan from cap centre, by symmetry = n * one triangle
    v = verts(n, h)
    return n*abs(tri_solid((0,0,h), v[0], v[1]))

def side_vos(n, h):
    v1, v2 = verts(n, h)[:2]
    w1, w2 = verts(n, -h)[:2]
    return abs(tri_solid(v1, v2, w2)) + abs(tri_solid(v1, w2, w1))

def cap_closed(n, h):
    # Gauss-Bonnet closed form: Omega = 2pi - 2n*arcsin( sin(pi/n) * h / sqrt(h^2 + a^2) ), a = cos(pi/n)
    a = mp.cos(mp.pi/n)
    return 2*mp.pi - 2*n*mp.asin(mp.sin(mp.pi/n)*h/mp.sqrt(h*h+a*a))

def fair_L(n, f=cap_closed):
    target = 4*mp.pi/(n+2)
    g = lambda L: f(n, L/2) - target
    L0 = n/mp.sqrt(n+1)
    return mp.findroot(g, L0)

def fair_L_exact(n):
    # closed form solve of cap_closed = 4pi/(n+2):
    # sin(pi/n) h/sqrt(h^2+a^2) = s := sin(pi (n/(n+2)) / n) = sin(pi/(n+2)) * ...  (see RESULTS.md)
    a = mp.cos(mp.pi/n); t = mp.sin(mp.pi/n)
    s = mp.sin((2*mp.pi - 4*mp.pi/(n+2))/(2*n))   # = sin(pi/(n+2))
    # h^2 (t^2 - s^2) = s^2 a^2
    h = s*a/mp.sqrt(t*t - s*s)
    return 2*h

if __name__ == "__main__":
    # consistency checks
    for n in (3, 4, 7, 12):
        h = mp.mpf('0.37')*n**0.5
        c1, c2 = cap_vos(n, h), cap_closed(n, h)
        tot = 2*c1 + n*side_vos(n, h)
        print("check n=%d  vos-closed=%.2e  total-4pi=%.2e" % (n, float(c1-c2), float(tot-4*mp.pi)))
    ns = list(range(3, 31)) + [50, 100, 1000]
    print("n  L*(n)  L*/sqrt(n)  n/sqrt(n+1)  L*_vos-L*_closedform")
    for n in ns:
        L = fair_L_exact(n)
        Lv = fair_L(n, cap_vos)
        print(n, mp.nstr(L, 15), mp.nstr(L/mp.sqrt(n), 15), mp.nstr(n/mp.sqrt(n+1), 15), mp.nstr(L-Lv, 3))
