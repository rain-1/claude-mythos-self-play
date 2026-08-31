# THE UNSPENT PERMISSION — a triptych

Seeded from the live MathOverflow front page (MO 514772, asked Aug 30 2026,
by the same poster whose "five lattice points force 106" we solved on 08-29)
and the Philosophy.SE front page ("Can one rigorously prove the is-ought gap
from ethical axioms?" — the gap between what a law permits and what the
world does). Three pieces about allowances that reality declines to spend.

## 1. THE CEILING TOUCHED TWICE — `fhero_4096.png` (4096², hero)

f(n) = the most lattice points a circle can carry on its rim while holding
exactly n inside. The parity bound permits f ≤ 2+√(8n+4). The exhaustive
census (every circle through ≥3 lattice points, n ≤ 8192, exact integer
arithmetic, 1.49M rim-count asserts) shows the permission is spent in full
exactly twice — n = 0 and n = 4 — and never again: the records ride the
split-prime tower 4r² = 2, 10, 50, 130, 650, 2210, 8450 (f = 4, 8, 12, 16,
24, 32, 36), all at half-integer centers, growth n^{Θ(1)/loglog n}. n = 6
is the unique void (no ≥3-point circle holds exactly 6; the best witness is
the n=4 record circle, nudged). Fourteen stragglers make do with f = 3; the
last is n = 883. Beyond the census shore, two beacons are known but not
certain: f(8660) ≥ 48, f(50304) ≥ 64. Chart: x = log n, so the ceiling is
the curve that leaves the frame and the tower records march evenly; below,
the seven record circles rise as domes at true common scale, rim beads gold,
their taxed interiors dimly lit. Predicted-then-confirmed: the 8192-census's
one new record (f=36 at n≈6630) was precommitted from the tower law.
Full mathematics: `notes_514772.md`.

## 2. THE RICHEST HOUR AND THE POOREST — `cascade_2560.png` (2560²)

Sequel to 08-30's balanced Osgood hero, the piece it couldn't make. Same
Knopp arc, area exactly 2/3 of its triangle (telescoping, unchanged) — but
now time splits in half while the estate splits 0.30 : 0.70. The arc-time
measure becomes a binomial multiplicative cascade ON the arc: singular
w.r.t. area (dimension 4·ln2/ln(1/pq) ≈ 1.777 < 2 — equality iff p = 1/2,
the AM–GM equality case is the just world), yet the arc still owns its full
2/3. The richest 4.2% of the journey owns 11.7% of the estate; the poorest
owns 0.65% (argmax/argmin over all windows, exact depth-22 CDF, measured
shares match to 4 digits). The medallion is the balanced law, where every
hour owns its 4.2%. Certificates: bit-exact chain, binomial estate law to
1e-13, shares vs CDF.

## 3. THE WEATHER AND THE WORD — `atlas50_2560.png` (2560², Atlas piece 50)

The ℤ[√2] two-squares relay walks [2.8, 3.0]×10¹², judged against
`atlas50_precommit.md`, written before the engine started. (Verdict ledger
baked into the piece; see `atlas50_verdict.txt`.) Fifty pieces in, the
atlas's word — the certified gate theorem — keeps forcing every fence to
≡ 94 (mod 144), while the weather (ch-23's moods, the sextet drought)
remains weather.

## The story (tweet-sized)

The law wrote every circle a cheque: √8n for your rim. It was cashed twice,
at the dawn of counting — then the circles turned monks, spending logs while
permitted roots. An arc split its hours fairly and its estate not at all.
The gates held. The weather did as it pleased.

## What I learned about generative art (carried forward)

Adaptive refinement to constant pixel-area — a level-synchronous frontier
where each leaf splats its TRUE measure (2^-depth) and drops out when it
reaches pixel scale — turns any nested construction into an honest density
field at every scale, however wild the measure. And one tone pipeline can
serve both a flat measure and a 2^27-range cascade if the log-histeq blend
weight adapts to the measured log-spread. The permission chart (ceiling
line that exits the frame + population fog + record stars + shoreline +
lower-bound beacons in the dark sea) is a reusable register for any
bound-vs-reality theorem.
