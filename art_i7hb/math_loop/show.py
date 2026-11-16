import subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
def cycle(m, n, dels):
    out = subprocess.run([HERE + '/hc', 'cycle', str(m), str(n)] + [f'{r},{c}' for r, c in dels], capture_output=True, text=True).stdout
    if out.startswith('count'): return None
    return [tuple(map(int, l.split())) for l in out.strip().splitlines()]
def ascii(m, n, dels, E):
    g = [[' '] * (2 * n - 1) for _ in range(2 * m - 1)]
    for r in range(m):
        for c in range(n): g[2 * r][2 * c] = 'O' if (r, c) in dels else '+'
    for r, c, r2, c2 in E: g[r + r2][c + c2] = '-' if r == r2 else '|'
    return '\n'.join(''.join(x) for x in g)
if __name__ == '__main__':
    m, n = int(sys.argv[1]), int(sys.argv[2])
    dels = [tuple(map(int, a.split(','))) for a in sys.argv[3:]]
    print(ascii(m, n, set(dels), cycle(m, n, dels)))
