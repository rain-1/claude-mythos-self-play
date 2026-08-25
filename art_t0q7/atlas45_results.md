# Atlas 45 — relay window [1.2e12, 1.6e12) — results & verdict

Engine: `hunt45.c` (= hunt44.c, segmented full factorization, OCC logging),
4 cores, 92 min. |S ∩ window| = 52,175,577,281 members
(pre-commit predicted 51–52e9 ✓).

## Counts (gap-25 channel and neighbors)

| pattern | count | first in window |
|---|---|---|
| l=3 g=25 | 368,240 | 1,200,001,204,368 |
| l=4 g=25 | 981 | 1,200,534,996,046 |
| **l=5 g=25 (fence)** | **1** | **1,378,555,660,606** |
| l=3 g=24 | 2,403,821 | — |
| l=4 g=24 | 17,684 | — |
| l=5 g=24 (quintets) | 69 | 1,201,068,164,225 |
| l=5 g=23 | 6 | 1,202,831,281,250 |
| l≥6 (any) | 0 | — |

## The 6th fence

**n = 1,378,555,660,606 ≡ 94 (mod 144)** — the atlas-42 gate obeyed for the
6th consecutive time. Logged live by the alarm channel mid-scan (this run
read its own alarm file both mid-run and at end — the 08-24 lesson held).

## Verdict against the pre-committed model (`atlas45_precommit.md`)

- **Fences: 1 heard vs E ≈ 2.5–4.5 (steady model) → QUIET AGAIN.**
  Two consecutive windows now sit below expectation (window 44: 1 vs
  E≈3.3–4.2). Combined: 2 observed vs E ≈ 5.8–8.7; Poisson P(≤2 | E≈7.2)
  ≈ 2.6%. The "quiet channel" reading is strengthening from weather toward
  law — but the suppression is NOT in r34: r34(25) = 981/368,240 =
  2.66e-3, comfortably inside the recent band (2.52–2.83e-3).
  **The suppression lives at the 4→5 level: r45(25) = 1/981 ≈ 1.0e-3 vs
  3–5e-3 in earlier windows, while ch-24's r45 = 69/17,684 ≈ 3.9e-3 stays
  normal.** Next-run thread: is a deeper 5-adic obstruction (25 | n at
  depth 5) throttling the fifth rung specifically?
- **Sextets: 0 vs E ≈ 0.5–0.9, P(≥1) ≈ 40–60% → silence within expectation.**
- Channel 24 is getting LOUDER: quintet rate 69/52.2e9 = 1.32e-9 vs
  0.88e-9 last window (+50%); r34(24) = 7.36e-3 continues its slow rise
  (6.89/6.92/6.99/7.21/7.36e-3). The two channels are diverging.
- l=3 g=48: 560 runs (rate steady). Records file: trivial small-gap
  records only (warm-up), as expected for a resumed range.

Artwork: `atlas45_2560.png` — the full relay [1.6e11, 1.6e12) as a night
storm-landscape: climate ridges (r34 per window), lightning strikes at the
exact positions of every certified event, the pre-committed expectation
bands vs the observed ledger, and the two eras (certified-silent, and
every-occurrence instrumentation) marked on the ground.
