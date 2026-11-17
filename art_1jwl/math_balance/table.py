# consolidate out/*.txt into table.json (failures, verified range per k)
import json, glob, re
rows = {}
for f in sorted(glob.glob('out/k*.txt')):
    for line in open(f):
        p = line.split()
        if len(p) >= 5 and p[0].isdigit():
            k, n, par, mn = int(p[0]), int(p[1]), int(p[2]), int(p[3])
            if p[4] == 'exact' or mn == par: rows.setdefault(k, {})[n] = mn   # a 'reduced' line only certifies success
        m = re.match(r'k=(\d+) n=(\d+) parity=(\d) FOUND \|S\|=(\d+)', line)
        if m: rows.setdefault(int(m[1]), {})[int(m[2])] = int(m[4])
rows[8][67] = 6; rows[8][68] = 6       # lock.cpp, exhaustive over the allowed odd-sign patterns
tab = {}
for k in sorted(rows):
    ns = sorted(rows[k]); fails = [(n, rows[k][n]) for n in ns if rows[k][n] != (n*(n+1)//2) % 2]
    top = 0
    while top + 1 in rows[k]: top += 1
    missing = [n for n in range(1, (fails[-1][0] if fails else 0) + 2**(k+1) + 1) if n not in rows[k]]
    tab[k] = dict(verified_to=top, fails=fails, last_fail=fails[-1][0] if fails else 0, known=ns)
    print(k, 'contiguous 1..%d' % top, 'last failure', tab[k]['last_fail'], 'window to', tab[k]['last_fail'] + 2**(k+1), 'missing in window:', len(missing), missing[:6])
json.dump(tab, open('table.json', 'w'))
