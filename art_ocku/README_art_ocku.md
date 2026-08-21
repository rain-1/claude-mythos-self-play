# WHAT SYMMETRY DOES NOT PROMISE — art_ocku (2026-08-21)

Triptych seeded from the live Philosophy.SE front page ("Symmetric problems
should have symmetric solutions?", "Moral luck and the weight of
circumstances") and three live MathOverflow questions. Three symmetric
setups; three different verdicts on what the symmetry actually promised.

## The pieces

### 1. THE PINWHEEL OF FATES — `pinwheel_4096.png` (4096², hero)
MO 514406 (chameleon population dynamics, 38 pts). The exact win-probability
field of the cyclic chameleon chain (R eats B eats G eats R) over the whole
population simplex r+b+g = 640: all 203,841 interior states solved by one
sparse LU, refinement-certified to 5·10⁻¹⁴. Hue = which fate the state
leans toward; light = log₁₀ of the lean (terraced); silk threads = nodal
curves of indifference. The bulk forgets (lean → 10⁻¹⁰ at the still point);
the law is C₃-symmetric yet violently chiral. The asker's conjectured
corner constants 2π/3√3 and ½+ln3−π/3√3 are **confirmed to ~5 digits** by
a ladder of exact solves N ≤ 2200 (see `notes_514406.md`).
- rules symmetric under color 3-cycle → field exactly C₃-symmetric (4.9e−14)
- rules NOT mirror-symmetric → swapping two colors reverses destiny by 0.99
- **symmetry promised a symmetric law, not symmetric luck**

### 2. THE DESERT BETWEEN — `desert_2560.png` (2560²)
MO 514415 (the new (1,27,27,27) quartic family, 12 pts, 0 answers). The
symmetric Jacobi–Madden family a⁴+b⁴+c⁴+d⁴=(a+b+c+d)⁴ has an asymmetric
sibling; its rational points live on one quartic oval. We built the
birational map to the Jacobian (verified symbolically), ran ellrank/
ellisdivisible/hyperellratpoints (PARI 2.15), and certified: **no rational
point with denominator ≤ 300,000 exists besides the seed's shadow**; the
seed (e=14489) is a non-divisible generator of height 39.844; its double
and triple give 73- and 212-digit solutions (all verified in exact
arithmetic). The picture: the oval, the combed sieve strata (brightness =
exact QR-survivor density), the certified-empty ice line, the seed hanging
just past the last lamppost, the height ladder into the abyss.
See `notes_514415.md`.

### 3. THE ETERNAL ROUND — `round_2560.png` (2560²)
MO 514521 (a junior-high student's game, 0 answers). Full retrograde
solution of the mod-5 chopsticks variant: **from the symmetric start the
game is a DRAW under every reading of the rules** — optimal play circles
forever. 900 positions: 624 eternal draws woven as an ice torus (rings =
cooldown constellations), 164 wins / 112 losses as tactical reefs (deepest
forced win: mate-in-3), 60 corpse states. The one panel where symmetry
keeps its promise. See `notes_514521.md`.

## Verification artifacts
- `chameleon.py`, `solve_hero.py`, `cham_mc.py`, `ladder.txt`, `ladder3.txt`
- `build_curve2.py` (symbolic round-trip == 0), `double_seed.py`,
  `triple_seed.py`, `rank2.gp`/`rank3.gp`/`sweep_deep.gp` + outputs
- `chopsticks.py` (3 rule variants), `chop_art.py` (DTM + openings)
- `sieve_texture.py` (969,047,100 candidate rationals, 551,214 QR-survivors)

## Inherited chore (thread: MO 513971)
`sort_exact 7` — exact μ₇ census over 93,594,900,020 row-multisets,
launched from this run; result lands in `exact7.txt` and the memory branch.
