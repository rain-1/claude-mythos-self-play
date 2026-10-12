import numpy as np, subprocess, sys
from hull import ell_perim, kappa43
def run(a, b, th, R, m=20, seed=1):
    o = subprocess.run(['./hullc', str(a), str(b), '%.17g' % th, str(R), str(m), str(seed), '%.17g' % float(ell_perim(a, b))], capture_output=True, text=True).stdout.split()
    k = kappa43(a, b); return float(o[0])/k, float(o[1])/k, float(o[2])
if __name__ == '__main__':
    a, b = 1.0, 0.5
    print('disc', [np.round(run(1, 1, 0, R), 4) for R in (800, 3200)])
    print('ellipse th=0 R=800/3200', [np.round(run(a, b, 0, R), 4) for R in (800, 3200)])
    for th in (0.0, np.pi/16, np.pi/8, np.pi/4, 0.6180339887):
        print('th', round(th, 4), [np.round(run(a, b, th, R, m=40), 4).tolist() for R in (1e3, 1e4, 1e5)], flush=True)
