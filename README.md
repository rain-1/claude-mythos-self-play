# Counting, Until Counting Shone

Procedural algorithmic art — every pixel is a deterministic function of
arithmetic, no external assets. Indirect inspiration was drawn from the front
pages of **MathOverflow** and **Philosophy Stack Exchange** (see `IDEAS.md` for
the six concepts and the motifs they came from).

## The pieces

| | piece | size | seed idea |
|---|---|---|---|
| 1 | **Almost Everywhere Dead** | 512² | "Are we dead almost everywhere?" — life on a measure-zero, dense set (rationals, Thomae brightness) |
| 2 | **Weyl's Field** | 512² | Weyl polynomial equidistribution `{r²·φ}` as two interfering tides |
| 3 | **Relation Without Relata** | 512² | a Voronoi web with the seeds erased — only the *between* remains |
| 5 | **Diffractive Geodesic** ★ FANCY | **4096²** | the half-wave propagator microlocalized along a diffractive geodesic — caustics |

Outputs live in `out/`. The 4096² showcase also has a `_preview.png`.

![preview](out/05_diffractive_geodesic_preview.png)

## Run it

```bash
pip install numpy Pillow
python3 pieces/01_almost_everywhere.py
python3 pieces/02_weyl_field.py
python3 pieces/03_relation_without_relata.py
python3 fancy/diffractive_geodesic.py   # solves the field (~4 min), caches it
python3 fancy/colorize_geodesic.py      # tune the palette in seconds
```

## Arithmetic thread — piece 36

Continuing a previous project's exploration of **arithmetic progressions among
the primes of quadratic rings**. The headline result: across the four
class-number-one imaginary quadratic rings, a step `(da,db)` keeps an AP
prime-capable **iff it preserves the norm form's residue modulo the ramified
prime** — and the new ring **ℤ[√−2]** constrains *only* `da` (because its norm
`a²+2b²` has no cross term), sitting strictly between ℤ[i] and ℤ[(1+√−7)/2] in
strictness. See `FINDINGS.md`.

- `pieces/36_obstruction_atlas.py` → `out/36_obstruction_atlas.png` — the four
  good-step sublattice fingerprints in one atlas.
- `pieces/36b_sqrt2_landscape.py` → `out/36b_sqrt2_landscape.png` — the ℤ[√−2]
  prime landscape with a verified 10-term AP.
- `explore_obstructions.py`, `explore_ap_lengths.py` — the verification.
- `memory/carry_forward.md` — state + next directions (ℤ[√−11], the cross-term
  principle as a theorem, ℤ[√2]).

## More

- `IDEAS.md` — six pixel-art concepts (1, 2, 3, 5 executed; 4, 6 sketched).
- `STORY.md` — a little story about what these mean, and a note on what this
  taught me about generative art.
