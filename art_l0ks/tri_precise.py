import numpy as np, math, json
SQRT2 = math.sqrt(2.0)
nmax = 262144
A = np.array([1.0])
masses = []
Cs = []   # (n, C_est) at even rows
snap_at = sorted(set([int(round(2**(k/8.0))) for k in range(48, 146)]))  # log-spaced rows for art later
for n in range(1, nmax+1):
    inv = 1.0/A
    Anew = np.empty(n+1); Anew[0]=Anew[n]=1.0
    if n>=2: Anew[1:n] = inv[:-1]+inv[1:]
    if n >= nmax-3 or n in (nmax//2, nmax//2+1, nmax//4, nmax//4+1):
        s = 1.0 if n%2==0 else -1.0
        masses.append((n, float(s*(Anew-SQRT2).sum())))
    if n % 2 == 0 and n >= 1024 and (n & (n-1)) == 0:
        Cs.append((n, float((Anew[n//2]-SQRT2)*math.sqrt(n))))
    A = Anew
print("masses:", masses)
# Mbar from last two rows
M1 = masses[-2][1]; M2 = masses[-1][1]
Mbar = 0.5*(M1+M2)
print("Mbar =", repr(Mbar))
print("pred C =", repr(math.sqrt(2/math.pi)*Mbar))
print("C series with sqrt-Richardson:")
for i in range(1, len(Cs)):
    n1,c1 = Cs[i-1]; n2,c2 = Cs[i]
    r = math.sqrt(2.0)
    print(f"  n={n2:7d} C={c2:.10f}  R2={(c2*r-c1)/(r-1):.10f}")
json.dump({'Mbar': Mbar, 'predC': math.sqrt(2/math.pi)*Mbar, 'Cs': Cs}, open('tri_precise.json','w'))
