"""Exact optimal strategy for 'permutation Wordle' (MO 497111): guess permutations, told the set of positions where
guess and secret agree. Minimise the expected number of guesses (the final, all-correct guess counts)."""
import itertools, functools, sys, json
n=int(sys.argv[1]); P=list(itertools.permutations(range(n))); N=len(P)
def fb(g,s): return sum(1<<i for i in range(n) if g[i]==s[i])
FB=[[fb(P[g],P[s]) for s in range(N)] for g in range(N)]
FULL=(1<<n)-1
@functools.lru_cache(maxsize=None)
def E(S):          # S: frozenset of candidate secret indices; returns (total guesses summed over S, best guess)
    if len(S)==1: return (1, next(iter(S)))
    best=(10**9,None)
    for g in range(N):
        parts={}
        for s in S: parts.setdefault(FB[g][s],[]).append(s)
        if len(parts)==1 and FULL not in parts: continue      # no information
        tot=len(S)                                             # this guess counted for every secret
        for f,ss in parts.items():
            if f==FULL: continue
            tot+=E(frozenset(ss))[0]
            if tot>=best[0]: break
        if tot<best[0]: best=(tot,g)
    return best
S=frozenset(range(N)); tot,g=E(S)
print('n=%d  optimal expected guesses = %d/%d = %.6f'%(n,tot,N,tot/N))
games={}
for s in range(N):
    T=S; seq=[]
    while True:
        g=E(T)[1]; seq.append((P[g],FB[g][s]))
        if FB[g][s]==FULL: break
        T=frozenset(x for x in T if FB[g][x]==FB[g][s])
    games[''.join(map(str,P[s]))]=[[list(p),f] for p,f in seq]
json.dump(games,open('games_n%d.json'%n,'w'))
from collections import Counter; print(Counter(len(v) for v in games.values()))
