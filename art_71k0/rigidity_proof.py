"""Finite proofs for atlas piece 41 (gap-17 fences in Z[sqrt2]):

LEMMA 1 (rigidity). Every 5-term AP n, n+17, ..., n+68 wholly in
S = {m : v_p(m) even for all p = 3,5 mod 8} has n = 14 (mod 16) and
n = 2 (mod 9).

LEMMA 2 (camps). For a window slot j = 6 (mod 8) (so v_2(n+j) = 2), let
c = ((j+14)/4) mod 8. The 2-part condition for n+j in S holds iff
(n = 14 mod 32 and c in {1,7}) or (n = 30 mod 32 and c in {3,5}).
With the 3-adic freeze of j = 22, 46, the alive camps are exactly
{14, 54} (n = 14 mod 32) and {6, 30, 38, 62} (n = 30 mod 32)."""

def ok_mod2k(r, k):
    M = 1 << k
    for t in range(5):
        m = (r + 17*t) % M
        if m == 0: continue                      # v2 >= k: not determined
        v = (m & -m).bit_length() - 1
        if v <= k - 3:                           # odd part determined mod 8
            if (m >> v) % 8 not in (1, 7): return False
    return True

for k in [4, 5, 6, 7, 8]:
    allowed = [r for r in range(1 << k) if ok_mod2k(r, k)]
    proj = sorted(set(r % 16 for r in allowed))
    print(f"mod 2^{k}: allowed {len(allowed)}, projection mod 16 = {proj}")
    assert proj == [14]

def ok_mod27(r):
    for t in range(5):
        m = (r + 17*t) % 27
        if m % 3 == 0 and m % 9 != 0: return False    # v3 = 1 exactly
    return True

allowed = [r for r in range(27) if ok_mod27(r)]
print("mod 27:", allowed, "projection mod 9 =", sorted(set(r % 9 for r in allowed)))
assert sorted(set(r % 9 for r in allowed)) == [2]

# camps
for parity, camp in [(0, {14, 22, 46, 54}), (1, {6, 30, 38, 62})]:
    for j in range(6, 68, 8):
        if j % 17 == 0: continue
        c = ((j + 14)//4) % 8
        alive_even = c in (1, 7)                 # t even, n = 14 mod 32
        member = (j in camp)
        if parity == 0: assert alive_even == member, (j, c)
        else:           assert (c in (3, 5)) == member, (j, c)
# 3-adic freeze of 22, 46 given n = 2 mod 9
for j in (22, 46):
    m9 = (2 + j) % 9
    assert m9 % 3 == 0 and m9 != 0               # v3(n+j) = 1 exactly
print("LEMMA 2 (camps) verified: {14,54} vs {6,30,38,62}, 22/46 frozen by 3")
print("ALL PROOFS PASS")
