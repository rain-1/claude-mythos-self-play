"""lns.py R C b mode [m] — anneal (dig3) to a near-solution, then large-neighbourhood search:
free a random window of cells, fix the rest as SAT assumptions, repeat."""
import sys, subprocess, random, json, time
from sat import solve, grid_of, check, board
R, C, b = map(int, sys.argv[1:4]); mode = sys.argv[4]; mirror = 'm' in sys.argv[5:]
seed = int([a for a in sys.argv[5:] if a.isdigit()][0]) if any(a.isdigit() for a in sys.argv[5:]) else 1
random.seed(seed)
def anneal(sd, iters=120_000_000):
    out = subprocess.run(['/tmp/dig3', str(R), str(C), str(b), mode+('m' if mirror else ''), str(sd), str(iters), '0.22', '0.22', '1000000'],
                         capture_output=True, text=True).stdout.split('\n')
    g = [[None if x == '.' else int(x) for x in ln.split()] for ln in out[1:R+1]]
    return out[0], g
s, X, cells = solve(R, C, b, mode, mirror, fix=False)
t0 = time.time(); sd = seed*1000
while True:
    sd += 1
    head, g = anneal(sd)
    print(head, '%.0fs' % (time.time()-t0), flush=True)
    if head.startswith('SOLVED'): break
    found = False
    for trial in range(40):
        # free a random disc of cells (and its mirror)
        ci, cj = random.choice(cells); rad = random.choice([2.2, 2.6, 3.0, 3.4])
        free = set(c for c in cells if (c[0]-ci)**2 + (c[1]-cj)**2 <= rad*rad)
        if mirror: free |= set((i, C-1-j) for (i, j) in free)
        ass = [X(c, g[c[0]][c[1]]) for c in cells if c not in free]
        s.conf_budget(60000)
        r = s.solve_limited(assumptions=ass)
        if r:
            g = grid_of(s.get_model(), X, cells, R, C, b); found = True; break
    if found: break
assert check(g, R, C, b, mode)
D = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
print('SAT', R, C, b, mode, 'mirror' if mirror else '', '%.0fs' % (time.time()-t0))
for r in g: print(' '.join('.' if x is None else D[x] for x in r))
json.dump(g, open('sol_%d_%d_%d_%s%s.json' % (R, C, b, mode, '_m' if mirror else ''), 'w'))
