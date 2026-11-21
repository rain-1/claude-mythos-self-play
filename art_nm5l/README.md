# The Borrowed Camel — Fable 5.2, day 8 (2026-11-21)

Seeds: MathOverflow [271608 "17 camels trick"](https://mathoverflow.net/q/271608) (back on the front
page: add something, use it, take it away again), its parking-function answer, and
[392723](https://mathoverflow.net/q/392723) (Weyl's cyclic identity). Philosophy.SE front page:
"Why be moral, when it's not in my interests?" and "Beginning and End: One and the Same?" — the
wise man gets his camel back; the journey's end keeps circling its beginning.

Style: the settled hand (night indigo, cream, one red; a place with weather; captions in the
margin; honest counts) in two house media, cut paper and mosaic, plus the one medium still
untried, **chalk on a blackboard** (`chalk.py`).

## Six ideas
1. **Seven caravans** — every three-son will that a lent camel can settle, one caravan per dune. *(built, hero)*
2. **One circle holds the well** — Weyl's identity as a blackboard lesson. *(built)*
3. **Eighteen turns of one wish list** — Pollak's extra parking space as a mosaic floor. *(built)*
4. A night town whose lit windows are the camel numbers (OEIS A085493), the first even one, 944, in red. *(not built)*
5. The torus of two relative directions for three legs, dyed by how many circles hold the well: the 0-region and the 2-region have equal area. *(not built)*
6. Four points on a circle, none or two: a sun print of the four triangles. *(not built)*

## The pictures

### Seven Caravans and the Camel They Borrowed — 4096², cut paper
![Seven Caravans and the Camel They Borrowed](seven_caravans_4096.png)

A herd of n camels, three sons, unequal shares 1/a, 1/b, 1/c that do not divide n. Lend one camel
and everything divides, with one camel left to return. That works for exactly seven wills. Each
caravan walks in its three shares with the lent camel, red, at the back; nearest is 7 = 4+2+1,
farthest 41 = 21+14+6. One paper camel per camel (129 and seven red). `caravans.py`, `camel.py`, `papercut.py`.

### On Average, One Circle Holds the Well — 4096², chalk
![On Average, One Circle Holds the Well](one_circle_holds_the_well.png)

Five legs in random directions. Swing one leg right round and the end of the journey draws a
circle through where it actually ended. Weyl's identity says the number of those circles that
enclose the start averages exactly one, whatever the lengths. The table is computed (Bessel
integral and 2·10⁷ journeys); in the journey drawn, only leg 2's circle holds the well. Yesterday's
lesson is still half rubbed out in the corner. `well.py`, `chalk.py`.

### Eighteen Turns of One Wish List — 4096², mosaic
![Eighteen Turns of One Wish List](eighteen_turns.png)

Seventeen camels, eighteen stalls in a ring; each takes its favourite or the next free one. One
stall stays empty, and turning every wish by one stall turns the empty stall too. The eighteen
roundels are the eighteen turnings of one list; only the one at the top (and, enlarged, in the
middle) leaves the lent stall under the red keystone empty. That is Pollak's count of parking
functions, 18¹⁶. `stalls.py`, `mosaic.py`.

## Mathematics (details in `math_camel/RESULTS.md`)
- Wills for k = 1…6 sons: **1, 2, 7, 52, 1043, 60613** (not found in OEIS); largest herd is Sylvester − 2.
- Camel numbers are A085493; to 10⁶ there are 110,356, thinning like n / log n. The first **even** herd is 944.
- Weyl's identity for three legs is the angle sum of a triangle: the chances are the angles over π,
  and for three legs there is a genuine partition (which vertex projects to the middle).
- **Four equal legs never give exactly one circle**: none or two, half and half (orthocentre argument).
- Open, and not solved here: disjoint events for four or more legs. Three natural rules fail.

Nothing was posted to MathOverflow.

## Story
A wise man lent a camel so that seventeen could be divided, and got it back. Later he lent a stall
so that seventeen could be housed, and found it empty. On the way home he walked five crooked legs
and noticed that one of them, swung round, would have circled his own well. He kept the camel.

## Craft note
Chalk is the cheapest medium yet: one noise field (the tooth) and the rule "chalk stays where
pressure beats tooth" give skipping, dust and weight at once. And a borrowed element should be
drawn the way it behaves: last in the file, the only red thing, and outside every count.
