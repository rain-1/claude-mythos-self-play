"""Uniqueness for ALL n by a finite check (independent of hc.cpp).

Sweep the m-row strip column by column.  After each column the state of the count is a vector
{frontier state: number of partial solutions}, and we only keep min(count, 2) -- addition
capped at 2 is still a semiring, so 'exactly one cycle' can be read from capped vectors.
Letters are columns (a set of deleted rows).  If the set of capped vectors reachable by a
family of words is finite and every one of them finishes with exactly one cycle, the whole
infinite family has a unique Hamiltonian cycle.
"""
import sys
from collections import defaultdict
CAP = 2
def canon(t):
    mp = {0: 0}; out = []
    for x in t:
        if x not in mp: mp[x] = len(mp)
        out.append(mp[x])
    return tuple(out)

DONE = ('done',)
def step(vec, m, deleted):
    """vec: frozenset of (state, capped count); process one column."""
    cur = dict(vec)
    for r in range(m):
        nxt = defaultdict(int)
        for st, n in cur.items():
            if st == DONE:
                if r in deleted: nxt[DONE] += n
                continue
            a = st[r]; b = st[m]; s = list(st)
            if r in deleted:
                if a == 0 and b == 0: nxt[st] += n
                continue
            last = (r == m - 1)
            if a == 0 and b == 0:
                if not last:
                    x = max(st) + 1; s[r] = x; s[m] = x; nxt[canon(s)] += n
            elif a == 0 or b == 0:
                x = a or b
                s[r] = x; s[m] = 0; nxt[canon(s)] += n
                if not last:
                    s[r] = 0; s[m] = x; nxt[canon(s)] += n
            elif a != b:
                s[r] = 0; s[m] = 0
                s = [a if x == b else x for x in s]; nxt[canon(s)] += n
            else:
                s[r] = 0; s[m] = 0
                if not any(s): nxt[DONE] += n          # the cycle closes; nothing else may be open
        cur = {k: min(v, CAP) for k, v in nxt.items()}
    return frozenset(cur.items())

def start(m): return frozenset({((0,) * (m + 1), 1)})
def finish(vec): return dict(vec).get(DONE, 0)
def run(vec, m, word, letters):
    for ch in word: vec = step(vec, m, letters[ch])
    return vec

if __name__ == '__main__':
    m = 3
    letters = {'E': set(), 'T': {0}, 'B': {2}, 'M': {1}}
    # sanity against hc.cpp / the table
    for w in ['EE', 'EEE', 'EEEE', 'EETEE', 'EEBEE', 'EEMEE']:
        print(w, finish(run(start(m), m, w, letters)))
    # reachable capped vectors after (EE X)^j, X in {T,B}
    v0 = start(m); R = {v0}; frontier = [v0]
    while frontier:
        new = []
        for v in frontier:
            for X in 'TB':
                w = run(v, m, 'EE' + X, letters)
                if w not in R: R.add(w); new.append(w)
        frontier = new
    print('reachable capped vectors after (EE{T,B})^j, j>=0:', len(R))
    for tail in ['EE', '', 'T', 'B', 'E', 'EET', 'TEE', 'BEE']:
        res = sorted(set(finish(run(v, m, tail, letters)) for v in R if v != v0))
        print(f'  tail {tail!r:6}: cycle counts (capped at 2) over all j>=1 and all choices: {res}')
    # n = 3k+1 with k+1 deletions: (EEB)^k B
    v = start(m); out = []
    for k in range(1, 8):
        v = run(v, m, 'EEB', letters); out.append(finish(run(v, m, 'B', letters)))
    print("tail 'B' after (EEB)^k, k=1..7:", out, '(the capped vector is already periodic at k=1)')
