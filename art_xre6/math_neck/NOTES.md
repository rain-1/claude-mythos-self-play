# Precarious necklaces (MathOverflow 515996): findings

Notation: N is a cyclic word of length n using k colours, n_c is the number of c-beads, and
M_c = (length of N\c) / (minimal period of N\c) is the multiplicity of the deleted word, so N\c = v^{M_c}.
N is precarious when M_c >= 2 for every c and N itself is aperiodic. p_j# is the product of the first j primes.

## Main result (proved; the computations agree)

    a(2j)   = 2j * p_j#                       (j >= 1)
    a(2j+1) = 2j * p_{j+1}# + p_j#            (j >= 1)

    k    : 2  3   4   5    6    7     8     9      10     11
    a(k) : 4  14  24  126  180  1290  1680  18690  23100  302610

So the asker's 126 is optimal and no shorter 5-colour necklace exists. Their examples for k=2..5 are, up to
rotation, reflection and colour permutation, exactly the construction below.

### Lemma (pair detection, k >= 3)
If p is prime and the 2-colour restriction N|{x,y} has multiplicity divisible by p for every pair of colours
{x,y}, then N has multiplicity divisible by p, so N is rotationally symmetric.

Proof. Every pair restriction is p-periodic, so p divides every n_c. Let T be the bead permutation that sends
the i-th c-bead to the (i + n_c/p)-th c-bead (indices mod n_c) for every colour c. On the beads of the colours
x and y, T is exactly the rotation by 1/p of N|{x,y}. Since N|{x,y} = u^p, T keeps the relative cyclic order
of all x- and y-beads. Lift to the bi-infinite periodic word. The order of the steps is a total order, and it
is fixed by the relative order of each pair of steps of different colours (steps of the same colour are ordered
by index). Each such pair lies in some N|{x,y}, so T preserves the whole order and is a translation of the
word that keeps colours. T^p is the shift by n, so T is the shift by n/p and N has period n/p < n.  QED

### Corollary
Restrictions of a periodic word are periodic: if N\c = v^m then N|{x,y} = (v|{x,y})^m for every x, y != c.
So in a precarious N (k >= 3), each prime p divides M_c for at most two colours c. Otherwise every pair
{x,y} misses some colour c with p | M_c, and the Lemma makes N periodic.

### Lower bound
Pick a prime p_c | M_c for each c. Each prime then occurs at most twice in the list (p_c). Since N\c = v^{M_c},
every n_d with d != c is divisible by M_c, so n_d >= lcm{p_c : c != d}. Let Q be the set of distinct primes
used, with r = |Q|. Let D be the primes used twice and S the primes used once, so k = 2|D| + |S|, and let
Pi = prod Q. Then

    n >= 2|D| * Pi + sum_{p in S} Pi/p.

Swapping any prime for a smaller unused one never increases this bound. So Q = {first r primes}, and the
single primes are the largest ones. Take r >= ceil(k/2).
- Even k = 2j. If r = j there are no singles and n >= 2j p_j#. If r > j, every term is at least p_{r-1}# >= p_j#.
- Odd k = 2j+1. If r = j+1 there is one single, the prime p_{j+1}, and n >= 2j p_{j+1}# + p_j#. If r >= j+2,
  every term is at least p_{j+1}#, which is larger.

construct.py `lower_bound` minimises the bound by brute force over prime multisets. The result agrees with the
formula for k = 2..14.

### Upper-bound construction (block construction)
Even k = 2j. Use colours a_t, b_t (t = 1..j) and primes q_t = p_t, and let P = p_j#. The necklace is
B_0 B_1 ... B_{P-1}, where block B_i joins the pairs (a_t b_t if q_t does not divide i, else b_t a_t) for
t = 1..j. Each colour occurs P times, so n = 2jP.
- Deleting a_t or b_t: the result depends on i only through i mod P/q_t, so its multiplicity is q_t.
- N is aperiodic. For j >= 2, a colour-preserving rotation keeps the positions of a_1 and b_1, which fill the
  residues {0,1} mod 2j, so it is a whole number of blocks. The block sequence has minimal period P,
  because each flip pattern has period exactly q_t and the q_t are coprime. For j = 1 the necklace is ABBA = AABB.

Odd k = 2j+1. Take the even word W, with P_j = p_j# blocks, and the new prime q = p_{j+1}. Form W^q, which
has p_{j+1}# blocks, and put one bead of the new colour z in front of each block whose index is divisible by q.
- That uses P_j z-beads, so n = 2j p_{j+1}# + p_j#.
- N\z = W^q.
- Deleting a_t: the z-positions are invariant under the shift by p_{j+1}#/q_t blocks, so the multiplicity is q_t.
- N is aperiodic, because a symmetry must map z to z (a shift by a multiple of q blocks) and the block contents
  have period P_j, which is coprime to q.

construct.py builds these words and checks them with a KMP period test. They are precarious with exactly the
lengths above for k = 2..11. The k=11 word has length 302610.

## Exhaustive verification (independent of the proof)
- bt.c with drive.py: backtracking for a fixed count vector and fixed deletion primes p_c. Each p_c is a prime
  dividing the gcd of the other counts. The deletion periodicity is checked online. The search covers all count
  vectors for each n, and duplicates are removed by rotation, reflection and colour relabelling.
- brute.c: plain enumeration of all 3^n words for n <= 14 (and 4^n for n <= 14). It agrees.
- k=3: no precarious necklace for n < 14. At n = 14 there is exactly one up to symmetry:
  ABCCBBCACBBCCB, canonical form AABBACABBAABCB, multiplicities (2,2,3).
  Number of classes for n = 14..30: 1,1,2,0,3,0,6,7,13,0,28,3,52,54,109,0,287. The search kept at most 2000 raw solutions per count/prime combination, so these are lower bounds; they are certainly exact for n <= 16.
- k=4: none for n < 24. At n = 24 there is exactly one up to symmetry:
  ABCDBACDABDCBACDABCDBADC, canonical form ABCADBCDACBADBCDABCADCBD. At n = 25 and 26 there are none, and at
  n = 30 there are at least 7 classes.
- Empirical check of the Corollary: across all k=3 classes with n <= 30 and all k=4 classes with n <= 30, no
  prime divides three multiplicities.
- k=5 by brute backtracking is not feasible beyond about n = 28; the Lemma makes the search unnecessary.

## Open / conjectural
- Conjecture (not checked): for every k >= 3 the minimal precarious necklace is unique up to symmetry, namely
  the block construction. This is verified for k = 3 and 4 only. For k=5 the equality case forces the counts
  (30,30,30,30,6) and primes (2,2,3,3,5), but uniqueness was not enumerated.

Files: bt.c, brute.c, drive.py, construct.py, emp.py, and examples.json (asker's examples plus constructions
for k = 2..8).
