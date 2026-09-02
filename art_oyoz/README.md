# art_oyoz — WHICH LEVEL DECIDES (run 2026-09-02)

Bright & pastel (user brief; beauty first).  Subtractive watercolor stack (`pastel.py`,
Beer–Lambert glazes on warm paper) with a brighter pigment box and crisper ink than 09-01.

## Pieces
| file | piece |
|---|---|
| `spectre_hero_4096.png` | **Which Level Decides** — the Spectre chiral aperiodic monotile, 3,575 tiles, painted by its supertile hierarchy (`notes_spectre.md`) |
| `tide_2560.png` | **The Tide of Four Primes** — MO 409058 worked to the integer: planar-divisor numbers lose the majority at N = 26,855,313 (`notes_planar.md`) |
| `octagon_loom_2560.png` | **The Loom of the Octagon** — 105 verified periodic directions of the regular-octagon translation surface, two cylinders each, moduli 1:1 or 1:2 (`notes_octagon.md`) |

## Code
- `spectre.py` — Spectre substitution (ported from Kaplan's `spectre.js`) + verification; `render_spectre.py`.
- `planar_sig.py` (planarity by signature, matches the poster's list), `planar_race.py` (exact counts via a
  Lucy–Hedgehog table), `planar_window.py` (integer-by-integer crossing + ±1-step certificate),
  `tide_data.py`, `render_tide.py`.
- `octagon.py` (saddle connections, cylinders, certificates), `render_octagon.py`.

Story + craft lessons: `STORY.md`.  Idea sheet: `IDEAS.md`.
