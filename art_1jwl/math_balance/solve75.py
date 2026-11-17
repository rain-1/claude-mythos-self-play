# full sign vector for a balanced split of 1^8..n^8 given the odd weights on the minority pan
import sys, json, numpy as np
n = int(sys.argv[1]); minority = [int(a) for a in sys.argv[2:]]
k = 8
odd = [i for i in range(1, n+1, 2)]; even = [i for i in range(2, n+1, 2)]
so = sum(i**k for i in odd) - 2*sum(i**k for i in minority)
ne = len(even); na = ne//2
def sums(idx):
    s = np.zeros(1, np.int64)
    for i in idx: s = np.concatenate([s + i**k, s - i**k])
    return s
A = sums(even[:na]); B = sums(even[na:])
order = np.argsort(A); As = A[order]
need = -so - B
pos = np.searchsorted(As, need); pos = np.clip(pos, 0, len(As)-1)
hit = np.nonzero(As[pos] == need)[0]
assert len(hit), "no exact solution with this minority set"
b = int(hit[0]); a = int(order[pos[b]])
def signs(code, idx):   # concatenate order: last added term is the top bit
    out = {}
    for j, i in enumerate(idx): out[i] = +1 if ((code >> j) & 1) == 0 else -1
    return out
sg = {i: (-1 if i in minority else 1) for i in odd}
sg.update(signs(a, even[:na])); sg.update(signs(b, even[na:]))
tot = sum(sg[i]*i**k for i in range(1, n+1)); assert tot == 0, tot
left = [i for i in range(1, n+1) if sg[i] > 0]; right = [i for i in range(1, n+1) if sg[i] < 0]
print("left ", left); print("right", right); print("each pan:", sum(i**k for i in left))
json.dump(dict(n=n, k=k, left=left, right=right, pan=str(sum(i**k for i in left))), open('balance%d.json' % n, 'w'))
