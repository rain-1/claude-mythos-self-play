#!/usr/bin/env python3
"""MO 514521: the schoolyard game mod 5, retrograde analysis.

State: (m, o, mcd, ocd) with m,o ordered pairs in {0..4}^2 (hands of the
player TO MOVE and the opponent), mcd/ocd = split-cooldown flags.
Moves of the player to move:
  attack: pick own hand a!=0, opponent hand b!=0 -> b' = (b+a) mod 5.
          If opponent becomes (0,0), mover WINS immediately.
  split : if allowed (variant-dependent), replace (m1,m2) by any (s1,s2) in
          Z5^2 with s1+s2 == m1+m2 (mod 5) and multiset {s1,s2} != {m1,m2}.
After the move, turn passes; mover's new cooldown: 1 if they just split else 0.

Outcome labels from the mover's perspective: 1=WIN, -1=LOSS, 0=DRAW (cycle).
Standard retrograde BFS on the loopy game graph.

Variants:
  A (as stated): split has 1-turn cooldown; split may create/revive 0 hands
    (including suicide to (0,0) -> immediate loss? both hands 0 = lose:
    we treat a split that leaves the mover at (0,0) as an immediate loss for
    the mover; a rational player just won't take it).
  B: no cooldown at all.
  C: cooldown, and split components must be nonzero (no revival, no suicide).
"""
import sys
from collections import deque
from itertools import product

def solve(variant):
    def split_targets(m, allow_zero):
        s = (m[0]+m[1]) % 5
        out = []
        for s1 in range(5):
            s2 = (s - s1) % 5
            if not allow_zero and (s1==0 or s2==0): continue
            if {s1,s2} == {m[0],m[1]} or sorted((s1,s2)) == sorted(m): continue
            out.append((s1,s2))
        # dedupe unordered
        return sorted(set(tuple(sorted(t)) for t in out))

    allow_zero = variant in ('A','B')
    use_cd     = variant in ('A','C')

    # state space: m,o as sorted pairs (hands unordered), cds
    hands = [tuple(sorted(h)) for h in product(range(5),repeat=2)]
    hands = sorted(set(hands))
    states = []
    for m in hands:
        for o in hands:
            for mcd in ((0,1) if use_cd else (0,)):
                for ocd in ((0,1) if use_cd else (0,)):
                    states.append((m,o,mcd,ocd))
    sidx = {s:i for i,s in enumerate(states)}

    succ = [[] for _ in states]        # successor state indices (mover -> opponent to move)
    winmove = [False]*len(states)      # has an immediately-winning move
    losemove_only = None
    for i,(m,o,mcd,ocd) in enumerate(states):
        if m == (0,0):                 # mover already dead (shouldn't be reachable as to-move, but label)
            continue
        # attacks
        for ai in set(a for a in m if a):
            for j in range(2):
                if o[j] == 0: continue
                nb = list(o); nb[j] = (o[j]+ai) % 5
                nbt = tuple(sorted(nb))
                if nbt == (0,0):
                    winmove[i] = True
                    continue
                ns = (nbt, m, (ocd if use_cd else 0), 0)
                succ[i].append(sidx[ns])
        # splits
        can_split = (mcd == 0) if use_cd else True
        if can_split:
            for t in split_targets(m, allow_zero):
                if t == (0,0):
                    continue   # suicide: mover loses instantly; never optimal, skip
                ns = (o, t, (ocd if use_cd else 0), (1 if use_cd else 0))
                succ[i].append(sidx[ns])
        succ[i] = sorted(set(succ[i]))

    # retrograde: value from mover's perspective
    N = len(states)
    val = [0]*N          # 0 unknown/draw
    deg = [0]*N
    q = deque()
    for i,(m,o,mcd,ocd) in enumerate(states):
        if m == (0,0):
            val[i] = -1   # mover has lost
            q.append(i)
            continue
        if winmove[i]:
            val[i] = 1
            q.append(i)
            continue
        deg[i] = len(succ[i])
        if deg[i] == 0:
            val[i] = -1   # no moves at all (can't happen here, but safe)
            q.append(i)
    # build predecessor lists
    pred = [[] for _ in range(N)]
    for i in range(N):
        if val[i] != 0 and not winmove[i] and states[i][0] != (0,0):
            pass
        for j in succ[i]:
            pred[j].append(i)
    # BFS
    while q:
        j = q.popleft()
        for i in pred[j]:
            if val[i] != 0: continue
            if val[j] == -1:
                val[i] = 1; q.append(i)
            else:               # val[j] == 1: one winning reply consumed
                deg[i] -= 1
                if deg[i] == 0:
                    val[i] = -1; q.append(i)
    return states, sidx, val, succ, winmove

if __name__ == "__main__":
    for variant in ('A','B','C'):
        states, sidx, val, succ, winmove = solve(variant)
        start = sidx[((1,1),(1,1),0,0)] if variant in ('A','C') else sidx[((1,1),(1,1),0,0)]
        v = val[start]
        n_win = sum(1 for x in val if x==1); n_loss = sum(1 for x in val if x==-1)
        n_draw = len(val) - n_win - n_loss
        verdict = {1:'FIRST PLAYER WINS', -1:'SECOND PLAYER WINS', 0:'DRAW (optimal play cycles forever)'}[v]
        print(f"variant {variant}: start ((1,1),(1,1)) -> {verdict}")
        print(f"   state space {len(states)}; W/L/D = {n_win}/{n_loss}/{n_draw}")
