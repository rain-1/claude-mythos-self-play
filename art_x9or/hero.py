import sys, time
from render_doors import render
t = time.time()
S = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
render('flower5', S, 2, (0, 144, 252), 0.0, f'hero_raw_{S}.png', ext=1.55, cy=-0.15, rows=128)
print('done', time.time() - t)
