import mpmath as mp
from prism_fair import fair_L_exact
mp.mp.dps = 40
def Lc(n):  # closed form, real n allowed
    n = mp.mpf(n); a=mp.cos(mp.pi/n); t=mp.sin(mp.pi/n); s=mp.sin(mp.pi/(n+2))
    return 2*a*s/mp.sqrt(t*t-s*s)
# monotonicity checks on a fine real grid n in [3, 1e6]
for name, f in (("L/sqrt(n)", lambda n: Lc(n)/mp.sqrt(n)),
                ("L/sqrt(n+1)", lambda n: Lc(n)/mp.sqrt(n+1)),
                ("L/sqrt(n+2)", lambda n: Lc(n)/mp.sqrt(n+2)),
                ("L*sqrt(n+1)/n", lambda n: Lc(n)*mp.sqrt(n+1)/n)):
    grid = [3 + k*0.01 for k in range(1600)] + [mp.mpf(10)**(1.3 + 0.001*k) for k in range(4800)]
    vals = [f(g) for g in grid]
    inc = all(vals[i+1] > vals[i] for i in range(len(vals)-1))
    dec = all(vals[i+1] < vals[i] for i in range(len(vals)-1))
    print(name, "increasing" if inc else ("decreasing" if dec else "not monotone"), mp.nstr(vals[0],8), mp.nstr(vals[-1],12))
print("ratio L*/(n/sqrt(n+1)) and L*/(n cos(pi/n)/sqrt(n+1)): exact lies between apothem- and circumradius-disc?")
for n in (3,4,6,10,30,100):
    L = Lc(n); up = n/mp.sqrt(n+1); lo = n*mp.cos(mp.pi/n)/mp.sqrt(n+1)
    print(n, mp.nstr(lo,10), mp.nstr(L,10), mp.nstr(up,10), lo < L < up)
# aspect ratios
print("n, L*, L*/edge, L*/(2*apothem), L*/(2R)")
for n in range(3,13):
    L = Lc(n); e = 2*mp.sin(mp.pi/n); a = mp.cos(mp.pi/n)
    print(n, mp.nstr(L,10), mp.nstr(L/e,10), mp.nstr(L/(2*a),10), mp.nstr(L/2,10))

# Barrier model: tipping barrier of a resting face = min over its edges of (dist centroid-edge) - (dist centroid-face).
# Fair-by-barrier: equal minimal barrier for caps and sides.
print("barrier model")
for n in list(range(3,13))+[20,30,100]:
    a = mp.cos(mp.pi/n)
    def gap(L):
        h = L/2
        cap = mp.sqrt(h*h+a*a) - h
        side = min(1 - a, mp.sqrt(a*a+h*h) - a)
        return cap - side
    Lb = (2*a-1)/(1-a) if n>3 else mp.findroot(gap, 1.2)   # closed form when side barrier = 1-a (lateral edge)
    print(n, mp.nstr(Lb,10), mp.nstr(gap(Lb),3), "  solid-angle L*:", mp.nstr(Lc(n),10))
