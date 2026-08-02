"""Exhaustive local lemma check for the triple-flip parity conservation.

At a generic triple-concurrence event of lines i,j,k the three mutual
crossings x=v_ij, y=v_ik, z=v_jk pass through a common point. On each
line the two relevant crossings are order-adjacent at the event; each
line is either MATCHED (pair occupies matching positions -> the pair
edge is an edge of the forced graph) or STRADDLING (pair straddles two
matching pairs -> each pair vertex connects to an outer stub on that
line). The flip swaps the two pair vertices on all three lines at once.

For every straddle pattern (2^3) and every left-right assignment of the
pair vertices on each line (2^3) we compute the induced stub-matching
before (M1) and after (M2) and check the parity lemma quantity
   delta = m + cycles(M1 u M2)   (m = number of stub pairs)
is EVEN, which by the chord-diagram parity lemma means the number of
cycles of the global graph changes by an even amount regardless of how
the outside connects the stubs.  Internal closed loops that appear on
both sides cancel; a loop appearing on ONE side only would flip parity
-- we check none arises.
"""
from itertools import product

def build(straddle, leftright):
    """Return (paths, loops): paths = dict stub->stub through the gadget,
    loops = number of internal closed cycles.
    Vertices x,y,z; per line the pair and its edges:
      line i: pair (x,y); line j: pair (x,z); line k: pair (y,z).
    If matched: internal edge between the pair.
    If straddling: with pair order (L,R) (left vertex L), edges
      (aL, L) and (R, bL)   [aL = left outer stub, bL = right outer stub]
    After the flip the pair order reverses: (R,L): edges (aL,R),(L,bL)."""
    E = []
    pairs = {'i': ('x','y'), 'j': ('x','z'), 'k': ('y','z')}
    for ln in 'ijk':
        u, v = pairs[ln]
        if leftright[ln]: u, v = v, u          # who is left
        if straddle[ln]:
            E.append((f'a{ln}', u)); E.append((v, f'b{ln}'))
        else:
            E.append((u, v))
    # trace paths/loops in the gadget graph (stubs have degree 1, xyz degree 2)
    adj = {}
    for u, v in E:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    stubs = [w for w in adj if w[0] in 'ab']
    for w in ('x','y','z'):
        assert len(adj.get(w, [])) == 2, "internal vertex degree must be 2"
    seen_e = set()
    match = {}
    for s in stubs:
        if s in match: continue
        prev, cur = None, s
        while True:
            nxts = [w for w in adj[cur] if w != prev] if prev is not None else adj[cur]
            if cur != s and cur[0] in 'ab':
                match[s] = cur; match[cur] = s
                break
            nxt = nxts[0]
            prev, cur = cur, nxt
    # count internal loops (cycles among x,y,z not reachable from stubs)
    visited = set()
    for s in stubs:
        prev, cur = None, s
        visited.add(s)
        while cur[0] not in 'ab' or cur == s:
            nxts = [w for w in adj[cur] if w != prev] if prev is not None else adj[cur]
            prev, cur = cur, nxts[0]
            visited.add(cur)
            if cur[0] in 'ab': break
    loops = 0
    for w in ('x','y','z'):
        if w in adj and w not in visited:
            # trace the loop
            loop = {w}; prev, cur = None, w
            while True:
                nxts = [u for u in adj[cur] if u != prev] if prev is not None else [adj[cur][0]]
                prev, cur = cur, nxts[0]
                if cur == w: break
                loop.add(cur)
            visited |= loop
            loops += 1
    return match, loops

def cycles_of_union(M1, M2, points):
    seen = set(); c = 0
    for p in points:
        if p in seen: continue
        c += 1
        cur, use1 = p, True
        while cur not in seen:
            seen.add(cur)
            cur = (M1 if use1 else M2)[cur]
            use1 = not use1
    return c

bad = 0; checked = 0
for svals in product([0,1], repeat=3):
    straddle = dict(zip('ijk', svals))
    for lrvals in product([0,1], repeat=3):
        leftright = dict(zip('ijk', lrvals))
        M1, loops1 = build(straddle, leftright)
        # after flip: left-right reverses on every line
        flipped = {ln: 1 - leftright[ln] for ln in 'ijk'}
        M2, loops2 = build(straddle, flipped)
        pts = sorted(M1)
        assert sorted(M2) == pts
        m = len(pts) // 2
        if m == 0:
            delta = (loops2 - loops1) % 2
        else:
            delta = (m + cycles_of_union(M1, M2, pts) + (loops2 - loops1)) % 2
        checked += 1
        status = "OK " if delta == 0 else "BAD"
        if delta != 0: bad += 1
        print(f"straddle={svals} leftright={lrvals} m={m} "
              f"loops {loops1}->{loops2} parity-delta={delta} {status}")
print(f"\n{checked} configurations checked, {bad} parity violations")
