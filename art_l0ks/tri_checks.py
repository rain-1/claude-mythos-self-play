import mpmath as mp
mp.mp.dps = 40
# boundary layer tower to high precision
B = [mp.mpf(1)]
for j in range(1, 200):
    u = 1/B[-1]
    B.append((u + mp.sqrt(u*u+4))/2)
S = sum(b - mp.sqrt(2) for b in B)   # one-edge layer mass sum
print("Sum_j (B_j - sqrt2) =", mp.nstr(S, 20))
print("M_odd - M_even pred = -4*S =", mp.nstr(-4*S, 20), " (measured 1.0140040694)")
print("check B1 - phi =", mp.nstr(B[1] - (1+mp.sqrt(5))/2, 5))
# constant hunt for Mbar (11-digit honesty)
Mbar = mp.mpf('0.0654503304268973')
cands = {'pi': mp.pi, 'sqrt2': mp.sqrt(2), 'phi': (1+mp.sqrt(5))/2, 'log2': mp.log(2),
         'e': mp.e, 'sqrt(pi)': mp.sqrt(mp.pi), 'S_layer': S, 'gamma': mp.euler}
for name, v in cands.items():
    for op, val in [('M/v', Mbar/v), ('M*v', Mbar*v)]:
        # is val close to a small rational?
        fr = mp.pslq([val, 1], maxcoeff=200, maxsteps=5000)
        print(f"  {op} {name}: {mp.nstr(val,12)}  pslq={fr}")
try:
    rel = mp.pslq([Mbar, 1, mp.sqrt(2), mp.pi, S], maxcoeff=60, maxsteps=20000)
    print("pslq [Mbar,1,sqrt2,pi,S]:", rel)
except Exception as ex:
    print("pslq fail", ex)
