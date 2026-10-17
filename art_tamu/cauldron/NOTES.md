# Permutation Wordle (MO 497111, R. Stanley) — notes

## 1. Literature / what MO says (fetched via SE API 2026-10-17; raw JSON in mo/)
- Question (Stanley, 2025-07): E(n)? asymptotics E(n) ~ cn? Notes the "keep known values, avoid known-wrong values,
  cyclically shift wrong ones" strategy needs <= n guesses. Motivation: Royal Match "Magic Cauldron" event (3<=n<=7).
- Comment (Sam Hopkins): arXiv:2408.00903 (Kutin & Smithline, "Permutation Wordle", 2024) and arXiv:2506.23452
  (A. Hiveley, "Experimenting with Permutation Wordle", 2025). Both abstracts checked on arXiv.
- Answer (jvvk, 2026-10, score 4): RESOLVED by Kutin, Smithline, Vatter, "Permutation Wordle", arXiv:2609.01874
  (Sep 2026; abstract verified on arXiv):
  * CircularShift: guess identity; keep correct entries; rotate the wrong values one step right (cyclically) among
    the wrong positions. It solves w in exactly exc(w)+1 guesses (exc = #{i : w(i) > i}), so #solved in exactly k+1
    rounds = Eulerian number A(n,k), and E(n) = (n+1)/2 (c = 1/2).
  * Thm 10: ANY deterministic strategy solves at most sum_{k<=d} A(n,k) secrets within d+1 rounds, for every d,
    even if guesses are arbitrary words over [n].  Thm 11: same for randomised strategies.  Hence E(n) = (n+1)/2
    exactly, and CircularShift is optimal in the strong (stochastic-dominance) sense.
  * Kutin-Smithline 2024 conjectured this; Hiveley (JIS 29 (2026) 26.1.7 per the answer) proved it for <= 3 rounds
    within a class of CircularShift-derived strategies.
- Black-peg / AB-Mastermind literature (El Ouali-Glazik-Sauerland-Srivastav: O(n log n) queries, worst case,
  black-peg COUNT feedback on permutations) is a weaker-feedback, worst-case variant; not needed here.

## 2. Exact E(6)  (exact.c — C, branch & bound + memo, canonicalised under simultaneous conjugation)
V(S) = |S| + min_g sum_{f != all-correct} V(S_f), guesses = all n! permutations, root guess = identity (WLOG),
lower bound V(S) >= 2|S|-1 (tight iff some candidate splits the rest into singletons).  One core, ~3.5 s:
    class (by #fixed pts of secret wrt identity):  k=4:1  k=3:3  k=2:18  k=1:110  k=0 (265 derangements): 795
    total 2520 / 720  =>  **E(6) = 7/2 exactly**.  Cross-checked with canonicalisation switched off (same 2520).
    Also reproduces E(4)=60/24, E(5)=360/120.  Log: exact6.log.
n=7 (exact7b.c = exact.c with MAXN 7, canonicalisation only for |S|<=200): sub-classes k>=1 done (D6-with-one-spare-position again gives 795 = 3.5*265, so a spare known
position does not help), but the 1854-derangement class did not finish in 60 min (exact7.log). Not needed: theorem.

## 3. Conjecture E(n) = (n+1)/2 — TRUE (KSV 2026)
strategies.py, exact over all n! secrets (strategies.log):
- CircularShift: E = (n+1)/2 for n=1..8; guesses = exc(w)+1 for every w checked; distribution = Eulerian row
  (n=6: 1,57,302,302,57,1; n=8: 1,247,4293,15619,15619,4293,247,1).
- FirstConsistent (lexicographically-first permutation consistent with all info; Stanley-type rule): NOT optimal for
  n>=4: E(4)=31/12, E(5)=31/10, E(6)=863/240, E(7)=20651/5040.  So "consistent + avoid known wrong values"
  alone is not enough; the cyclic-shift structure matters.
- Optimal-solver game trees (games_n4.json, games_n5.json) have round distributions (1,11,11,1), (1,26,66,26,1) =
  Eulerian, consistent with the strong Thm 10.
Lower bound, elementary case d=1 (self-contained): after guess 1 each secret not yet solved is solved in round 2 only
if it equals guess 2 of its feedback class; feedback = fixed set F of v1^{-1}w, F != [n] and |F| != n-1, so at most
2^n-1-n = A(n,1) secrets finish in round 2.  The general bound sum_{k<=d} A(n,k) is KSV Thm 10.

## 4. Files
games_n4.json, games_n5.json (both exist; n=5: 120 games, round counts 1/26/66/26/1), exact.c, exact7b.c,
strategies.py, *.log, mo/*.json.
