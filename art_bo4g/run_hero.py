"""run_hero.py — run one dumbbell to extinction at hero resolution and save the record + certificates."""
import sys, json, time, pickle
import numpy as np
from ricci import run_flow

a = float(sys.argv[1]); w = float(sys.argv[2]); N = int(sys.argv[3]); tag = sys.argv[4]
t0 = time.time()
rec, cert = run_flow(a=a, w=w, N=N, verbose=True, log_every=20000, record_dt=0.0005, eps=0.02)
cert['elapsed'] = time.time() - t0
# certificates: neck law d(psi_min^2)/dt -> -2(n-1) = -2 ; child law d(psi_max^2)/dt -> -2n = -4
neck = np.array(cert['neck'])
ev = {e[1]: e for e in cert['events']}
if 'S' in ev and ev['S'][0] == 'surgery':
    T = ev['S'][2]
    sel = (neck[:, 0] > T - 0.02) & (neck[:, 0] < T - 0.0005)
    if sel.sum() > 5:
        slope = np.polyfit(neck[sel, 0], neck[sel, 1] ** 2, 1)[0]
        cert['neck_law_slope'] = float(slope)
        print('neck law: d(psi_min^2)/dt = %.4f (Angenent–Knopf: -2)' % slope)
for k, v in cert['radius'].items():
    if k == 'S':
        continue
    arr = np.array(v)
    ext = [e for e in cert['events'] if e[1] == k and e[0] == 'extinct']
    if ext:
        Te = ext[0][2]
        sel = (arr[:, 0] > Te - 0.03) & (arr[:, 0] < Te - 0.001)
        if sel.sum() > 5:
            slope = np.polyfit(arr[sel, 0], arr[sel, 1] ** 2, 1)[0]
            cert['child_law_slope_' + k] = float(slope)
            print('child %s: d(psi_max^2)/dt = %.4f (round S^3: -4)' % (k, slope))
pickle.dump(rec, open('cache/rec_%s.pkl' % tag, 'wb'))
json.dump(cert, open('cache/cert_%s.json' % tag, 'w'), indent=1, default=float)
print('saved', tag, 'frames', len(rec), 'events', cert['events'], 'elapsed %.0f s' % cert['elapsed'])
