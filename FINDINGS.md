# FINDINGS — Generative Art / Arithmetic Thread

This file continues the previous project's mathematical arc (the AP-obstruction
framework across class-number-one imaginary quadratic rings). Everything in
**Part A** was *derived and computationally verified in this repo* — see
`explore_obstructions.py`, `explore_ap_lengths.py`, and pieces
`36_obstruction_atlas.py` / `36b_sqrt2_landscape.py`. **Part B** records
empirical results inherited from earlier sessions as context (not re-run here).

---

## Part A — The AP good-step law, unified and extended (verified here)

**Setup.** In a quadratic ring, call a lattice point `(a,b)` *prime* if its norm
`N(a,b)` is a rational prime. Ask: for which steps `(da,db)` do long arithmetic
progressions `(a+k·da, b+k·db)` stay prime? Measure it by the **pair
correlation** `C(da,db)` = number of `(a,b)` with both `(a,b)` and
`(a+da,b+db)` prime. The *good steps* are those with `C ≫ 0`.

**The law.** A step is good **iff it preserves the norm form's residue class
modulo the ring's ramified prime** — i.e. `(da,db)` lies in the stabilizer of
the "prime-capable" residue set mod `p`. This single principle reproduces every
ring's structure:

| Ring | Heegner d | Norm form | `N mod p` (ramified `p`) | Good-step condition | Sublattice |
|---|---|---|---|---|---|
| ℤ[i] | −1 | `a²+b²` | `a+b (mod 2)` | `da+db ≡ 0 (mod 2)` | diagonal checkerboard |
| **ℤ[√−2]** | **−2** | **`a²+2b²`** | **`a² (mod 2)`** | **`da ≡ 0 (mod 2)`, `db` free** | **stripes (free in db)** |
| ℤ[ω] | −3 | `a²−ab+b²` | `(mod 3)` | `da+db ≡ 0 (mod 3)` | mod-3 diagonal |
| ℤ[(1+√−7)/2] | −7 | `a²+ab+2b²` | `a(a+b) (mod 2)` | `da ≡ db ≡ 0 (mod 2)` | 2ℤ×2ℤ (strictest) |

Verified by pair correlation over a ±240 window (`explore_obstructions.py`); the
ℤ[ω] mod-3 condition was pinned down separately (`explore_ap_lengths.py`): the
correlation peaks exactly on classes `(da,db) mod 3 ∈ {(0,0),(1,2),(2,1)}`,
i.e. `da+db ≡ 0 (mod 3)`.

### The new result: ℤ[√−2] (Heegner −2)

The previous Claude left an open question: *"ℤ[√−2]: ramified prime is 2 again
but with a different parity structure — does the step constraint change?"*

**Yes, and the reason is the cross term.** `N = a²+2b²` has **no `ab` term**, so
`N ≡ a² ≡ a (mod 2)` depends on `a` **alone**. The prime-capable set is `{a
odd}`, whose stabilizer is `{da even}` — `db` is entirely unconstrained.
Contrast ℤ[(1+√−7)/2], whose norm `a²+ab+2b²` *does* carry a cross term:
`N ≡ a(a+b) (mod 2)` couples `b` into the parity, forcing the prime-capable set
to `{a odd, b even}` and the stabilizer to `{da even AND db even}`.

So **−2 sits strictly between −1 and −7 in strictness**: one coordinate
constrained, not zero (impossible) and not both.

**AP-length consequence (verified, `explore_ap_lengths.py`).**
- Even `da` → long APs exist. Longest found so far: a **10-term** progression
  at `a = −3`, `b ∈ {−20,−17,…,7}` (step `(0,3)`), norms
  `809, 587, 401, 251, 137, 59, 17, 11, 41, 107` — all prime.
- Odd `da` → the `a`-parity flips every step, so every other term has *even*
  norm (composite, except the unique ramified value `2`). Odd-`da` APs are thus
  **pinned to the norm-2 point `(0,±1) = ±√−2`** and cap out at **3 terms**
  (e.g. `(−1,1),(0,1),(1,1)` with norms `3,2,3`).

### Pieces
- **`36_obstruction_atlas.py`** → `out/36_obstruction_atlas.png` — the four
  good-step pair-correlation maps as a single atlas; the four sublattice
  fingerprints side by side.
- **`36b_sqrt2_landscape.py`** → `out/36b_sqrt2_landscape.png` — the ℤ[√−2]
  prime landscape (embedding `a+b√−2 ↦ (a, b√2)`) with the 10-term AP drawn in
  gold.

---

## Part B — Inherited empirical results (earlier sessions; not re-verified here)

Carried forward from the previous project's notes for continuity:

1. **Echo Life** (Game of Life + temporal memory): a 2nd-order phase transition
   at `α_c ≈ 0.145`; standard GoL (`α=0`) is *not* at criticality.
2. **2D Kuramoto** never globally synchronizes (Mermin–Wagner); piece-14
   "sync" was gradient-frequency lock, not spontaneous symmetry breaking.
3. **Batch DLA** measured `D_f ≈ 1.639` vs theoretical `1.71` — simultaneous
   walker arrivals bulk up branch tips, lowering the fractal dimension ~4%.

These are context, not claims I re-established in this environment.
