"""Fit a Zeckendorf-digit automaton for d(n) = det M_n in {-1,0,+1}.

Try 1: does d(n) depend only on the last k Zeckendorf digits (lsd window)?
Try 2: RPNI-style deterministic state merging on the msd-first prefix trie.
"""
import pickle
from detlib import zeck_digits


def suffix_test(d, kmax=14):
    words = {n: tuple(zeck_digits(n)) for n in d}
    for k in range(1, kmax + 1):
        table = {}
        ok = True
        for n, w in words.items():
            key = (tuple([0] * max(0, k - len(w))) + w)[-k:]
            if key in table and table[key] != d[n]:
                ok = False
                break
            table[key] = d[n]
        if ok:
            return k, table
    return None, None


def prefix_trie_merge(d):
    """RPNI-ish: build msd-first trie; merge states greedily if consistent.

    Every node IS a valid Zeckendorf word (a number) except the root; a
    node's output is d(value) when the value is in range, else None.
    Merge = fold node q2 into q1 if outputs compatible and recursively
    children compatible (union of transitions).
    """
    words = sorted(d, key=lambda n: (len(zeck_digits(n)), n))
    # trie: nodes as dicts; use ids
    trans = [{}]           # node -> {digit: node}
    out = [None]           # node -> output or None
    for n in words:
        cur = 0
        for dig in zeck_digits(n):
            if dig not in trans[cur]:
                trans.append({})
                out.append(None)
                trans[cur][dig] = len(trans) - 1
            cur = trans[cur][dig]
        out[cur] = d[n]

    parent = list(range(len(trans)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def compatible(a, b, seen):
        a, b = find(a), find(b)
        if a == b:
            return True
        if (a, b) in seen or (b, a) in seen:
            return True
        seen.add((a, b))
        if out[a] is not None and out[b] is not None and out[a] != out[b]:
            return False
        for dig in (0, 1):
            ta, tb = trans[a].get(dig), trans[b].get(dig)
            if ta is not None and tb is not None:
                if not compatible(ta, tb, seen):
                    return False
        return True

    def merge(a, b):
        a, b = find(a), find(b)
        if a == b:
            return
        parent[b] = a
        if out[a] is None:
            out[a] = out[b]
        for dig in (0, 1):
            ta, tb = trans[a].get(dig), trans[b].get(dig)
            if ta is None and tb is not None:
                trans[a][dig] = tb
            elif ta is not None and tb is not None:
                merge(ta, tb)

    # canonical order: BFS (red-blue would be cleaner; greedy works often)
    order = []
    stack = [0]
    visited = set()
    from collections import deque
    dq = deque([0])
    while dq:
        x = dq.popleft()
        if x in visited:
            continue
        visited.add(x)
        order.append(x)
        for dig in (0, 1):
            if dig in trans[x]:
                dq.append(trans[x][dig])

    reds = []
    for q in order:
        q = find(q)
        merged = False
        for r in reds:
            r = find(r)
            if r == q:
                merged = True
                break
            if compatible(q, r, set()):
                merge(r, q)
                merged = True
                break
        if not merged:
            reds.append(q)
    # compact automaton
    states = sorted({find(q) for q in range(len(trans)) if find(q) in map(find, reds) or True})
    live = {find(0)}
    changed = True
    while changed:
        changed = False
        for s in list(live):
            for dig in (0, 1):
                t = trans[s].get(dig)
                if t is not None:
                    t = find(t)
                    if t not in live:
                        live.add(t)
                        changed = True
    live = sorted(live)
    idx = {s: i for i, s in enumerate(live)}
    A = {"start": idx[find(0)], "out": {}, "trans": {}}
    for s in live:
        A["out"][idx[s]] = out[s]
        for dig in (0, 1):
            t = trans[s].get(dig)
            if t is not None:
                A["trans"][(idx[s], dig)] = idx[find(t)]
    return A


def run_automaton(A, n):
    cur = A["start"]
    for dig in zeck_digits(n):
        key = (cur, dig)
        if key not in A["trans"]:
            return None  # unknown transition
        cur = A["trans"][key]
    return A["out"].get(cur)


if __name__ == "__main__":
    d = pickle.load(open("dets3000.pkl", "rb"))
    k, table = suffix_test(d)
    print("suffix window k:", k)
    A = prefix_trie_merge(d)
    print("merged automaton states:", len(set(A["out"])) and len(A["out"]))
    bad = 0
    for n in d:
        p = run_automaton(A, n)
        if p is not None and p != d[n]:
            bad += 1
    print("training disagreements:", bad)
    pickle.dump(A, open("automaton.pkl", "wb"))
