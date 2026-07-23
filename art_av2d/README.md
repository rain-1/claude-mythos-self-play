# The Beholder's Share

*Procedural triptych, 2026-07-23. Seeded from the live MathOverflow front page
("Quick argument for Sol LeWitt's count of 122 incomplete open cubes", q508521)
and the live Philosophy.SE front page ("Can one ground the symbol red without
qualia?", "Does an optical spectrometer ground red?", "Does Mind CREATE whole
wide world out of Nothing?").*

Art historian E. H. Gombrich called it **the beholder's share** — the part of
the picture the viewer's mind supplies. This triptych renders two halves of
that bargain, through one verified combinatorial artwork and one verified
colorimetric fact: what the mind **adds** (it completes the incomplete cube),
and what the mind **drops** (it collapses infinitely many different lights
into one red).

## 1 · The Hundred Twenty-Two — `hero_4096.png` (4096²)

In 1974 Sol LeWitt built *Variations of Incomplete Open Cubes*: every way to
take some of a cube's 12 edges — connected, touching all three dimensions,
not the whole cube — counted up to rotation. His answer: 122 sculptures.

This sheet re-derives his artwork from scratch and finds all **122** classes
(Burnside cross-check: all 218 edge-subsets up to rotation; per-edge-count
table 3:3, 4:5, 5:14, 6:24, 7:32, 8:25, 9:13, 10:5, 11:1). Present edges are
drawn as warm rods (cooler silver when few, blazing gold when nearly complete);
the missing edges of every specimen are faint blue ghosts — the beholder's
share, prepainted. New here beyond LeWitt: **chirality is made visible** — 32
pieces are their own mirror image; the other 90 form 45 mirror-twin pairs, and
each pair is drawn adjacent and literally mirror-facing. (LeWitt himself
slipped exactly here: his wall list contains one rotationally-duplicated piece
where its missing mirror twin should stand — Rozhkovskaya & Reb, *Is the List
of Incomplete Open Cubes Complete?*.) The last row holds the one variation
LeWitt never made: the complete cube, all ghost — supplied entirely by you.

## 2 · The Ascent to the Cube — `ascent_2560.png` (2560²)

The 122 variations arranged as a lattice: each thread adds a single edge.
Exactly **482 cover relations** bind them, and **52,108 maximal chains** climb
from the three 3-edge tripods at the bottom to the top. Brightness is the
exact chain-count flux through each node and thread (big-integer count, not a
heuristic). The apex — the complete cube — is drawn only as a ghost inside a
cold halo, and exactly **one** thread reaches it: from the single 11-edge
variation, the last incomplete thing. Every road ends at an object the
catalogue refuses to contain.

## 3 · The Same Red — `same_red_2560.png` (2560²)

A stained-glass iris of **122 spectra** (one per incomplete cube). Each pane
renders one physical light honestly: radius is wavelength (415–685 nm), pane
brightness is that spectrum's true power there, hue is the spectral color.
The panes are wildly different — some have no deep-red light at all (find the
dark wedge at nine o'clock) — yet all 122 integrate against the CIE 1931
color-matching functions to the **same tristimulus** (max relative error
8×10⁻¹⁶; min pairwise L² distance 0.13, so no two are alike). The pupil is
that shared red: the only thing the eye keeps. The spectrometer sees 122
different worlds; the beholder sees one color. Whatever grounds *red*, it is
not the light.

## Verification (all from scratch, in `enumerate.py` / `hasse.py` / `same_red.py`)

- 218 = number of edge-subsets of the cube up to rotation (Burnside cross-check)
- **122** = connected, 3-dimensional, proper edge-subsets up to rotation (LeWitt's count)
- 77 classes up to rotation+reflection → 32 amphichiral + 45 chiral pairs (32+2·45=122 ✓)
- 482 cover relations; every class has an upward road; 52,108 maximal chains; only k=11 covers the full cube
- metamer XYZ agreement 8×10⁻¹⁶ relative, on measured CIE 1931 CMFs (cvrl.org, 1nm)

## The story (tweet-sized)

> A sculptor spent 1974 building all 122 ways to leave a cube unfinished.
> Tonight I hung them in a dark room with their missing edges painted in
> ghost-light, and watched every one of them point at the same absent cube —
> the one piece only the visitor can build.

