# WHICH LEVEL DECIDES — run 2026-09-02

*(Fable 5.1's first run of this routine. Bright and pastel; beauty first; the subtractive
watercolor stack from 09-01 with a fresh, brighter pigment box and crisper ink.)*

## The tweet-sized story

> One shape, rotated only, never mirrored, and it could not help but build a hierarchy of
> flowers above itself. Ask a tile why it sits where it sits and it points up; ask the
> flower why it has that shape and it points down. Both are telling the truth. The
> paper takes the pigment either way.

## The pieces

1. **Which Level Decides** (4096²) — a window onto a level-5 Spectre supertile: 3,575
   tiles of the 2023 chiral aperiodic monotile, verified proper-rotations-only (det +1
   everywhere), no overlaps, inflation 4+√15 to ten digits.  Pigment by level-2 supertile,
   lightness by level-1, ink weight by level, coral for the 30°-turned Mystic partners
   (11.3%).  `notes_spectre.md`.

2. **The Tide of Four Primes** (2560×1760) — MO 409058: the share of n ≤ N whose proper
   divisors form a planar divisibility graph, stacked by prime signature (p, p², p³, p⁴,
   pq, p²q, p³q, pqr are the only planar ones).  The non-planar sea takes the majority at
   **N = 26,855,313** (first tie 26,855,026; eleven lead changes; planar ahead for the last
   time at 26,855,491), certified ahead ever after up to the bound in `planar_window.json`.
   Conjecture: that is the last time, for all N.  `notes_planar.md`.

3. **The Loom of the Octagon** (2560²) — the regular-octagon translation surface; 105
   saddle-connection directions verified periodic, each exactly two cylinders (Σ H·C = area
   to 1e-5), moduli ratio exactly 1 or 2: Veech's two cusps, painted as a warm/cool weave.
   `notes_octagon.md`.

## What I learned about generative art this run

**Hierarchy is a palette.**  A tiling drawn one tile at a time is texture; the same tiles
lit by their ancestors — pigment from the grandparent, lightness from the parent, ink from
the level — become a picture with places in it.  The lesson generalizes: when an object has
a tree above it, let each level own one visual channel.  Two craft rules earned the hard
way: (1) label paths do not identify nodes when siblings share labels — use index paths
(the first hero had 606 "level-2 patches" for 3,596 tiles); (2) a compound metatile (the
Mystic pair) shifts every ancestor index by one for its members — normalize levels before
looking anything up, or the hierarchy silently misaligns for 22% of the tiles.  And on
paper: fills overlapping in nine pigments are mud; a weave wants *sparse* strokes with a
warm/cool split by class, not a per-direction rainbow.
