"""Machine verification of every ingredient of the two theorems in proofs.md.

Theorem 1 (golden dead zone): det M_n = 0 for n in
  [q_K, q_K + q_{K-5} - 1] u [q_K + q_{K-3}, q_{K+1} - 1].
Theorem 2 (lone voice): per(M_{u_K}) = 1 where u_K = q_K + u_{K-4}.

Run: python3 verify_proofs.py [KMAX]
"""
import sys
from detlib import fibs_upto, det_fib
from permlib import count_pm

KMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 18

Q = fibs_upto(10**9)
Qset = set(Q)


def q(t):
    if t == 0:
        return 1  # convention q_0 = 1 (only used as a lower bound)
    return Q[t - 1]


# u_k: u_1=1, u_2=2, u_3=3, u_4=5, u_k = q_k + u_{k-4}
u = {0: 0, -1: 0, -2: 0, -3: 0, 1: 1, 2: 2, 3: 3, 4: 5}
for k in range(5, KMAX + 6):
    u[k] = q(k) + u[k - 4]

print("== identities ==")
for j in range(2, KMAX + 4):
    assert u[j] + u[j - 2] == q(j + 1) - 1, ("identity", j)
    assert u[j] < q(j + 1), ("u<q", j)
    assert 2 * u[j] <= q(j + 2) - 1, ("2u<=q-1", j)
print(f"u_j + u_(j-2) = q_(j+1)-1,  u_j < q_(j+1),  2u_j <= q_(j+2)-1   "
      f"for j <= {KMAX+3}: OK")

print("== Theorem 1: kernel identity ==")
# 1[s in Q] = 1[s+q_t in Q] + 1[s+q_(t+1) in Q]  for q_(t-2) < s < 2 q_(t+1)
for t in range(2, KMAX + 4):
    for s in range(q(t - 2) + 1, 2 * q(t + 1)):
        assert (s in Qset) == ((s + q(t) in Qset) + (s + q(t + 1) in Qset)), \
            ("kernel identity", t, s)
print(f"kernel identity holds on the full window for t = 2..{KMAX+3}: OK")

# the two Fibonacci-enumeration facts used in its proof
for t in range(2, KMAX + 4):
    win = range(q(t - 2) + 1, 2 * q(t + 1))
    inwin = lambda v: q(t - 2) < v < 2 * q(t + 1)
    inQ = [s for s in win if s in Qset]
    assert inQ == [v for v in (q(t-1), q(t), q(t+1), q(t+2)) if inwin(v)], t
    hit_t = [s for s in win if s + q(t) in Qset]
    assert hit_t == [v for v in (q(t-1), q(t+1)) if inwin(v)], t
    hit_t1 = [s for s in win if s + q(t + 1) in Qset]
    assert hit_t1 == [v for v in (q(t), q(t+2)) if inwin(v)], t
print("window enumerations {q_(t-1),q_t,q_(t+1),q_(t+2)} / {q_(t-1),q_(t+1)}"
      " / {q_t,q_(t+2)}: OK")

print("== Theorem 1: coverage arithmetic ==")
for K in range(7, KMAX + 2):
    # head: t = K-2, a = q_(K-4) covers n in [q_K, q_K + q_(K-5) - 1]
    t, a = K - 2, q(K - 4)
    assert a >= q(t - 2)
    assert a + q(t + 1) <= q(K)                       # covers from block start
    assert 2 * q(t + 1) - 1 - a == q(K) + q(K - 5) - 1  # exactly the head end
    # tail: t = K-1, a = q_(K-3) covers n in [q_K + q_(K-3), q_(K+1) - 1]
    t, a = K - 1, q(K - 3)
    assert a >= q(t - 2)
    assert a + q(t + 1) == q(K) + q(K - 3)             # exactly the tail start
    assert 2 * q(t + 1) - 1 - a >= q(K + 1) - 1        # reaches block end
print(f"head/tail coverage endpoints exact for K = 7..{KMAX+1}: OK")

print("== Theorem 1: spot dets in dead zone ==")
import random
random.seed(5)
cnt = 0
for K in range(7, min(KMAX + 1, 20)):
    for _ in range(3):
        m = random.randint(0, q(K - 5) - 1)
        assert det_fib(q(K) + m) == 0, ("head", K, m)
        m = random.randint(q(K - 3), q(K - 1) - 1)
        assert det_fib(q(K) + m) == 0, ("tail", K, m)
        cnt += 2
print(f"{cnt} random dead-zone determinants all 0: OK")

print("== Theorem 2: structural lemmas ==")
for K in range(7, KMAX + 1):
    n = u[K]
    # Step 1: q_(K+2) out of range for every row
    assert q(K + 2) - 1 > n + 0 and q(K + 2) > 2 * n, ("2n", K)
    # partner arithmetic: q_(K+1) - u_K = u_(K-2) + 1
    assert q(K + 1) - u[K] == u[K - 2] + 1
    # B-internal sums below q_K
    assert 2 * u[K - 2] < q(K)
    # strip <-> B sums: only q_K available
    assert q(K + 1) - u[K - 2] > n     # B rows cannot reach strip via q_(K+1)
print(f"forcing inequalities for K = 7..{KMAX}: OK")

print("== Theorem 2: pi* and parity of pair-sum indices ==")


def pistar(K):
    """The segment-reflection involution on [1, u_K]."""
    perm = {}
    j = K
    while u[j] > 0:
        lo, hi = u[j - 2] + 1, u[j]
        for i in range(lo, hi + 1):
            perm[i] = q(j + 1) - i
        j -= 2
    return perm


for K in range(2, KMAX + 1):
    p = pistar(K)
    n = u[K]
    assert sorted(p) == list(range(1, n + 1))
    assert sorted(p.values()) == list(range(1, n + 1))
    for i, jv in p.items():
        s = i + jv
        assert s in Qset, ("pi* invalid", K, i)
        t = Q.index(s) + 1
        assert (t - (K + 1)) % 2 == 0, ("parity", K, i, s)
    # crossing killer: no pair of pi*_(K-2) sums to q_(K-2)
    if K >= 4:
        p2 = pistar(K - 2)
        assert all(i + jv != q(K - 2) for i, jv in p2.items()), K
print(f"pi*_K valid, pair-sum indices = K+1 mod 2, and q_(K-2) never a "
      f"pi*_(K-2) pair-sum, K <= {KMAX}: OK")

print("== Theorem 2: per(M_(u_K)) = 1 directly ==")
for K in range(1, min(KMAX, 19) + 1):
    assert count_pm(u[K]) == 1, ("per", K, u[K])
print(f"per = 1 verified by independent DP for K = 1..{min(KMAX,19)}: OK")

print("== corollary: det sign = sign(pi*) ==")
import pickle
try:
    d = pickle.load(open('dets75024.pkl', 'rb'))
except FileNotFoundError:
    d = {}


def perm_sign(p):
    n = len(p)
    seen = set()
    sgn = 1
    for i in p:
        if i in seen:
            continue
        l, jv = 0, i
        while jv not in seen:
            seen.add(jv)
            jv = p[jv]
            l += 1
        if l % 2 == 0:
            sgn = -sgn
    return sgn


ok = 0
for K in range(1, KMAX + 1):
    if u[K] in d and d[u[K]] != 0:
        assert d[u[K]] == perm_sign(pistar(K)), ("sign", K)
        ok += 1
print(f"det M_(u_K) = sign(pi*_K) for {ok} values of K in census: OK")
print()
print("ALL CHECKS PASSED")
