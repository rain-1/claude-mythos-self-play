"""analyze_erdos.py — structure of the discrepancy-2 sequences found by SAT.
For each solution: agreement with the Dirichlet character mod 3 on n not divisible by 3, complete
multiplicativity defect (fraction of pairs (m,n), mn ≤ N, with x_{mn} ≠ x_m x_n), ledger-value histogram,
and the 'brink' fraction (cells at ±2)."""
import sys, json, glob, numpy as np

def chi3(n):
    r = n % 3
    return 1 if r == 1 else (-1 if r == 2 else 0)

rows = []
for f in sorted(glob.glob('cache/erdos_*.json'), key=lambda f: json.load(open(f))['N']):
    d = json.load(open(f)); x = np.array(d['x']); N = len(x)
    n = np.arange(1, N + 1)
    m3 = n % 3 != 0
    c = np.array([chi3(k) for k in n])
    agree = (x[m3] == c[m3]).mean(); agree = max(agree, 1 - agree)   # up to the global sign
    # multiplicativity defect
    bad = tot = 0
    for a in range(2, N + 1):
        for b in range(2, N // a + 1):
            tot += 1; bad += (x[a * b - 1] != x[a - 1] * x[b - 1])
    # ledgers
    vals = np.concatenate([np.cumsum(x[dd - 1::dd]) for dd in range(1, N + 1)])
    hist = np.bincount(vals + 2, minlength=5)
    # x_{3m} vs x_m
    m = np.arange(1, N // 3 + 1)
    same3 = (x[3 * m - 1] == x[m - 1]).mean()
    rows.append(dict(file=f, N=N, solver=d.get('solver'), seconds=round(d.get('seconds', 0), 1), chi3_agreement=round(float(agree), 4),
                     mult_defect=round(bad / tot, 4), pairs=tot, x3m_eq_xm=round(float(same3), 4),
                     ledger_hist=hist.tolist(), brink_frac=round(float((hist[0] + hist[4]) / hist.sum()), 4)))
    print('%-32s N=%5d %-10s %7.1fs  chi3 agree %.3f  mult defect %.3f  x_{3m}=x_m %.3f  hist %s  brink %.3f' % (
        f, N, d.get('solver'), d.get('seconds', 0), agree, bad / tot, same3, hist.tolist(), (hist[0] + hist[4]) / hist.sum()))
json.dump(rows, open('erdos_analysis.json', 'w'), indent=1)
