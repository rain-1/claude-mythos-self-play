"""Drift-aware prediction for channel 25 (atlas piece 42), committed BEFORE
the [1.6e11, 4e11) hunt reports.

Data: exact run censuses from piece 40/41 (memory-branch runs):
  W1 = [0, 4e9)          range R1 = 4e9,   representative depth d1
  W2 = [2e10, 1.6e11)    range R2 = 1.4e11, representative depth d2
Ladder ratios r34 = l4/l3, r45 = l5/l4 per channel; per-unit-range l3 rates.

Model:
  * l3 rate per unit range rho3(g, n) drifts ~ linear in 1/sqrt(ln n)
    (member density is Landau-type c/sqrt(ln n); tail-gap probabilities rise).
    We fit log rho3 and log r34 linearly in u = 1/sqrt(ln n) through the two
    windows and extrapolate to W3 = [1.6e11, 4e11).
  * r45 for g=25 is not observed anywhere (channel silent) -> transfer from
    the odd wide channels: kappa(g) = r45/r34 measured in W2 on g=17,23,24,18,
    14; use the median kappa of the odd channels (17,23) and the full spread
    as uncertainty band.  r45(25, n) = kappa * r34(25, n).
  * Expected l5 count in [a,b) = integral rho3(n) r34(n) r45(n) dn;
    first-fence CDF = 1 - exp(-Lambda(n)) (Poisson clumping negligible).
"""
import numpy as np

# exact censuses
W1 = (0.0, 4.0e9); W2 = (2.0e10, 1.6e11); W3 = (1.6e11, 4.0e11)
l3 = {'W1': {14: 60419, 15: 288337, 16: 112125, 17: 18493, 18: 15697, 23: 2878, 24: 8541, 25: 1124},
      'W2': {14: 2487351, 15: 12702310, 16: 5270028, 17: 945939, 18: 845453, 23: 185433, 24: 586601, 25: 85376}}
l4 = {'W1': {14: 494, 15: 6119, 16: 1346, 17: 104, 18: 82, 23: 2, 24: 32, 25: 2},
      'W2': {14: 24478, 15: 327354, 16: 81766, 17: 6628, 18: 6611, 23: 244, 24: 3398, 25: 169}}
l5W2 = {14: 132, 15: 7590, 16: 689, 17: 13, 18: 20, 23: 1, 24: 10}

def rep_depth(a, b):
    # depth at which the window's average of u=1/sqrt(ln n) is attained ~ log-midpoint
    return np.exp(0.5*(np.log(max(a,2e8)) + np.log(b)))

d1, d2 = rep_depth(*W1), rep_depth(*W2)
u1, u2 = 1/np.sqrt(np.log(d1)), 1/np.sqrt(np.log(d2))

g = 25
R1 = W1[1]-W1[0]; R2 = W2[1]-W2[0]
rho3_1, rho3_2 = l3['W1'][g]/R1, l3['W2'][g]/R2
r34_1, r34_2 = l4['W1'][g]/l3['W1'][g], l4['W2'][g]/l3['W2'][g]

# linear fits in u for the logs
def linfit(y1, y2):
    a = (np.log(y2)-np.log(y1))/(u2-u1)
    b = np.log(y1) - a*u1
    return a, b
a3, b3 = linfit(rho3_1, rho3_2)
a4, b4 = linfit(r34_1, r34_2)

def rho3(n): return np.exp(a3/np.sqrt(np.log(n)) + b3)
def r34(n):  return np.exp(a4/np.sqrt(np.log(n)) + b4)

# kappa = r45/r34 in W2 per channel
kappa = {}
for gg in l5W2:
    r45 = l5W2[gg]/l4['W2'][gg]
    r34g = l4['W2'][gg]/l3['W2'][gg]
    kappa[gg] = r45/r34g
odd_k = [kappa[17], kappa[23]]
k_mid = float(np.sqrt(odd_k[0]*odd_k[1]))
k_lo, k_hi = min(kappa.values()), max(kappa.values())
print('kappa per channel:', {k: round(v,3) for k,v in kappa.items()})
print(f'kappa transfer for 25: mid={k_mid:.3f}  band=[{k_lo:.3f},{k_hi:.3f}]')

def Lam(a, b, k):
    ns = np.geomspace(max(a,1e6), b, 4000)
    lam = rho3(ns)*r34(ns)*(k*r34(ns))
    return float(np.trapezoid(lam, ns))

for k, tag in ((k_mid,'mid'),(k_lo,'lo'),(k_hi,'hi')):
    E3 = Lam(*W3, k)
    # cumulative from 0: where does P(first fence < n) = 0.5?
    print(f'[{tag}] E[l5(25) count in W3] = {E3:.3f}   P(>=1 in W3) = {1-np.exp(-E3):.3f}')

# predicted first-fence median over all n (from 4e9 onwards, adding earlier windows' zero observation)
for k, tag in ((k_mid,'mid'),(k_lo,'lo'),(k_hi,'hi')):
    grid = np.geomspace(4e9, 1e13, 300)
    cum = np.array([Lam(4e9, x, k) for x in grid])
    med = grid[np.searchsorted(cum, np.log(2))] if cum[-1] > np.log(2) else None
    q10 = grid[np.searchsorted(cum, -np.log(0.9))] if cum[-1] > -np.log(0.9) else None
    print(f'[{tag}] predicted first-fence: 10%-depth={q10:.3e}  median={med:.3e}' if med else f'[{tag}] median beyond 1e13')

# also verify the model retrodicts W2 counts for channels with data (predictive discipline)
print('\nretrodiction check on W2 (fit uses only l3/l4; l5 pred vs obs):')
for gg in [14, 17, 18, 23, 24]:
    rho3_1g, rho3_2g = l3['W1'][gg]/R1, l3['W2'][gg]/R2
    r34_1g, r34_2g = l4['W1'][gg]/l3['W1'][gg], l4['W2'][gg]/l3['W2'][gg]
    a3g, b3g = linfit(rho3_1g, rho3_2g); a4g, b4g = linfit(r34_1g, r34_2g)
    def lamg(n): return np.exp(a3g/np.sqrt(np.log(n))+b3g)*np.exp(a4g/np.sqrt(np.log(n))+b4g)**2
    ns = np.geomspace(W2[0], W2[1], 3000)
    for k, tag in ((k_mid,'mid'),):
        Epred = float(np.trapezoid(k*lamg(ns), ns))
        print(f'  g={gg}: predicted {Epred:.1f} vs observed {l5W2[gg]}')
