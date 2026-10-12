"""EVERY ROOM HAS THE SAME THREE DOORS — nine domains, one colouring: the disc in the middle is the legend."""
import numpy as np, sys
from PIL import Image
import render_doors as R
a, b = 1.25, 0.72
R.SHAPES.update({
 'disc':    lambda s: 1.0 + 0*s,
 'ellipse': lambda s: a*b/np.sqrt((b*np.cos(s))**2 + (a*np.sin(s))**2),
 'peanut':  lambda s: 1 + 0.30*np.cos(2*s),
 'kidney':  lambda s: 1 + 0.22*np.cos(s) + 0.20*np.cos(2*s + 0.3) + 0.04*np.cos(4*s),
 'flower7': lambda s: 1 + 0.17*np.cos(7*s),
})
CELLS = [('clover', (60, 180, 300)), ('flower7', (0, 103, 206)), ('peanut', (0, 120, 180)),
         ('ellipse', (0, 90, 200)), ('disc', (0, 120, 240)), ('cloud', (40, 160, 280)),
         ('kidney', (10, 150, 250)), ('star5', (18, 162, 306)), ('bean', (0, 110, 230))]
if __name__ == '__main__':
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    only = sys.argv[2:] 
    for name, doors in CELLS:
        if only and name not in only: continue
        s = np.linspace(0, 2*np.pi, 4000); rmax = R.SHAPES[name](s).max()
        R.render(name, S, 2, doors, 0.0, f'cell_{name}.png', ext=1.12*rmax)
        print(name, flush=True)
