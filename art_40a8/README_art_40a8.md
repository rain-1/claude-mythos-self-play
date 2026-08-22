# NOTHING FORBIDS, NOTHING SHOWS — triptych, run 2026-08-22

Three countries where existence and evidence come apart. Live seeds:
MathOverflow front page (514531, 1 day old, score 11 — "Is 51 the sum of
three rational fourth powers?") and Phil.SE's hot page ("What makes us
perceive something as real?" / "Does knowing more dispel the illusions we
live by?"). Inherited thread: AP-obstruction atlas piece 42 (channel 25).

| file | piece | one line |
|---|---|---|
| `sky_final.png` | **THE SKY OF OPEN DOORS** (4096², hero) | every fiber z/t = p/q of x⁴+y⁴+z⁴ = 51t⁴: 88% strangled by the two-squares wall, 25 by a deeper 2-adic wall — and 863 survivors of which 841 are parity-forced to rank ≥ 1. Open doors everywhere; the shore of squares stays empty |
| `guests_final.png` | **THE FOUR GUESTS** (2560²) | the same machinery on 17t⁴, where witnesses exist: four landed constellations (t = 583, 1011, 1259, 2353, re-found from scratch by this run's engine), the trivial guest on the ground, and certified silence above them |
| `gate_final.png` | **THE GATE OF TWENTY-FIVE** (2560², atlas piece 42) | ℤ[√2] equal-gap runs: the Wall of 144 residues with its one gold l=5 arch (n ≡ 94 mod 144, proved), ten channels newly certified CLOSED, thirteen fences heard, and channel 25's lane — prediction committed before the hunt's verdict |

Idea slate: `ideas.md` (6 ideas, 3 executed). Checks: `verification.md`.
MO dossier: `notes_514531.md`. Atlas model & prediction: `prediction25.md`,
`model25.py`, `gatecheck.py`. Engines: `nhunt.cpp` (meet-in-the-middle,
re-found all four Tomita solutions in minutes and pushed the no-fifth bound
from t = 2,353 to t = 60,000), `famhunt.c`, `hunt25.c`+`dump25.c` (sieve),
`fiberlib.py`+`stage2.gp`+`deep3.gp`+`rootno.gp` (fiber pipeline).

## Key results of the run (all verified; see verification.md)
1. Complete local-solubility criteria for a² = M − v⁴ (validated vs brute
   force, 0 mismatches) ⇒ exact three-wall census of 51's fiber sky:
   7,495 fibers → 6,607 conic-dead / 25 deep-wall / 863 alive.
2. **Parity conspiracy (new observation)**: 841/863 of 51's locally-alive
   fibers have root number −1 (rank forced ≥ 1); for 17 only 348/1,449.
   The country with all doors open has no guests; the country of mostly
   shut doors has four. Route to a proof: Birch–Stephens quartic twists.
3. Zero squares: every rational point found on every live fiber (sweeps to
   5·10⁶ on favorites, 4·10⁷ on the primal fiber) has non-square a; all 28
   family curves A⁴+(u⁴+v⁴)B⁴ = 51C⁴ empty to C = 2·10⁵.
4. N=17 engine certificate: all four known solutions re-found independently;
   **no fifth primitive solution with t ≤ 60,000** (was: 2,353).
5. Atlas: gate theorem l=5 gap-25 ⇒ start ≡ 94 (mod 144) (machine-certified
   two ways); channels {3,5,6,10–13,19–22} CLOSED by finite 2-adic
   certificate; gate 25 is 4× wider than gate 17 — the silence is the
   width-tail, not the door; drift-aware prediction committed mid-hunt
   (P(silent through 4·10¹¹) ≈ 65–80%, median fence ≈ 6·10¹¹–1.2·10¹²).
   Hunt verdict: see `gate_final.png` caption and `hunt_*` files.
