"""Signature-based Moore machine for d(n)=det M_n over Zeckendorf digits.

Complete census d(n) for all n <= F_22 - 1 = 28656 (words of length <= 21,
msd-first, alphabet {0,1}, no '11', leading digit 1).

State of prefix p := (last digit of p, [d(value(p.s)) for ALL valid suffixes
s with |s| <= KSTAR]).  Prefixes restricted to |p| <= 21 - KSTAR so every
signature entry is known.  Then check the map sig -> sig is a well-defined
deterministic transition function, outputs consistent, machine complete.
"""
import pickle
import sys
from functools import lru_cache

KSTAR = int(sys.argv[1]) if len(sys.argv) > 1 else 9
MAXLEN = 21

d = pickle.load(open("dets28656.pkl", "rb"))

# Fibonacci values for digit positions: F[1]=1, F[2]=2, F[3]=3, F[4]=5...
F = [0, 1, 2]
while len(F) < 40:
    F.append(F[-1] + F[-2])


def value(word):
    """word: tuple of 0/1 msd-first; value = sum digit * F[len-i]."""
    m = len(word)
    return sum(F[m - i] for i, dig in enumerate(word) if dig)


@lru_cache(maxsize=None)
def suffixes(last, maxlen):
    """All valid suffix words (tuples) of length 0..maxlen that can follow a
    prefix ending in digit `last` (no '11' anywhere, leading zeros fine)."""
    out = [()]
    frontier = [((), last)]
    for _ in range(maxlen):
        nf = []
        for (w, prev) in frontier:
            for a in (0, 1):
                if prev == 1 and a == 1:
                    continue
                w2 = w + (a,)
                out.append(w2)
                nf.append((w2, a))
        frontier = nf
    return out


# enumerate all valid prefixes (nonempty start with 1), length <= MAXLEN-KSTAR
prefixes = []
frontier = [((1,), 1)]
while frontier:
    nf = []
    for (w, prev) in frontier:
        prefixes.append(w)
        if len(w) < MAXLEN - KSTAR:
            for a in (0, 1):
                if prev == 1 and a == 1:
                    continue
                nf.append((w + (a,), a))
    frontier = nf
print("prefixes:", len(prefixes))


def sig(p):
    last = p[-1]
    entries = []
    for s in suffixes(last, KSTAR):
        v = value(p + s)
        entries.append(d[v])
    return (last, tuple(entries))


sig_of = {p: sig(p) for p in prefixes}
states = {}
for p in prefixes:
    states.setdefault(sig_of[p], []).append(p)
print("distinct states:", len(states))

# transitions: consistent?
sid = {s: i for i, s in enumerate(states)}
trans = {}
conflicts = 0
incomplete = set()
for p in prefixes:
    s = sid[sig_of[p]]
    if len(p) < MAXLEN - KSTAR:
        for a in (0, 1):
            if p[-1] == 1 and a == 1:
                continue
            p2 = p + (a,)
            t = sid[sig_of[p2]]
            if (s, a) in trans and trans[(s, a)] != t:
                conflicts += 1
            trans[(s, a)] = t
# completeness: every reachable state needs both transitions (except 1-after-1)
for s in range(len(states)):
    rep = states[list(states)[s]][0]
    for a in (0, 1):
        if list(states)[s][0] == 1 and a == 1:
            continue
        if (s, a) not in trans:
            incomplete.add((s, a))
print("transition conflicts:", conflicts)
print("incomplete transitions:", len(incomplete))

# outputs: d(value(p)) must be constant on state (it is entry s=() of sig)
out = {}
for sgn, ps in states.items():
    vals = {d[value(p)] for p in ps}
    assert len(vals) == 1, ("output conflict", sgn[0], vals)
    out[sid[sgn]] = vals.pop()

# start transitions: reading first digit 1 -> state of prefix (1,)
start1 = sid[sig_of[(1,)]]

machine = {"KSTAR": KSTAR, "n_states": len(states),
           "trans": trans, "out": out, "start1": start1}
pickle.dump(machine, open(f"machine_k{KSTAR}.pkl", "wb"))


def predict(n):
    from detlib import zeck_digits
    w = zeck_digits(n)
    cur = start1
    for a in w[1:]:
        cur = trans[(cur, a)]
    return out[cur]


# self-test on the whole census
bad = 0
from detlib import zeck_digits  # noqa
for n in range(1, 28657):
    if predict(n) != d[n]:
        bad += 1
print("census disagreements:", bad)
