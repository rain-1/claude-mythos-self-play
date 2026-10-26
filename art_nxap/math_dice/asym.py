import sympy as sp
x = sp.symbols('x', positive=True)  # x = 1/n
pi = sp.pi
a = sp.cos(pi*x); t = sp.sin(pi*x); s = sp.sin(pi*x/(1+2*x))
F = 4*a**2*s**2/(t**2 - s**2) * x       # = L*^2 / n
N = 7
Fs = sp.series(F, x, 0, N).removeO()
G = sp.series(sp.sqrt(Fs), x, 0, N).removeO()
print("L*/sqrt(n) =")
for k in range(N):
    print(k, sp.nsimplify(sp.simplify(G.coeff(x, k))), sp.N(G.coeff(x,k), 15))
# compare with L*/sqrt(n+2) and L*/sqrt(n+1)
for name, shift in (("n+1",1),("n+2",2)):
    H = sp.series(sp.sqrt(Fs/(1+shift*x)), x, 0, 5).removeO()
    print("L*/sqrt(%s):" % name, [sp.simplify(H.coeff(x,k)) for k in range(5)])
# equal-area disc prediction r_eff*n/sqrt(n+1)
reff = sp.sqrt(sp.sin(2*pi*x)/(2*pi*x))
D = sp.series(reff/sp.sqrt(1+x), x, 0, N).removeO()
print("equal-area-disc minus exact:", sp.simplify(sp.series(D - G, x, 0, N).removeO()))
