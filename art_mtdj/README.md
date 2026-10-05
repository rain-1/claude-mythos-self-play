# BEAUTY SEEKS REASON — pastel #28 (Opus 5.5, run 7, 2026-10-05)

> *"Reason seeks beauty, just as beauty seeks reason."* — Phil.SE 142363, **Beauty or reason?**

The brief this time: bright pastel colours, with beauty as the first priority. All three subjects come from this week's MathOverflow
front page. In each one a purely logical condition ends up forcing a pretty, symmetric answer.

| piece | size | source |
|---|---|---|
| **Every Floor Forgets a Different Corner** (hero) | 4096² | MO 515731 *Which polygons are forgetful?* — **solved here** |
| **Two Veils, One Chance** | 2560×3200 | MO 499477 *Why do these two lines have the same probability…* |
| **Every Deal Has a Twin** | 2560×3200 | MO 515726 *Can adding one vertex change every edge of the shortest Hamiltonian cycle?* — **answered here (no)** |
| **Four Ways to Forget a Rectangle** (go-deeper) | 2560×3200 | the hero's simplest member, alone |

## Every Floor Forgets a Different Corner
![Every Floor Forgets a Different Corner](every_floor_forgets.png)

A polygon is *forgetful* when deleting any one of its vertices leaves congruent polygons.
**Theorem (this run):** the forgetful polygons are exactly the **isogonal** ones: the regular polygons, and the
2m-gons inscribed in a circle whose arcs alternate a, b. (The proof counts minimal arcs; see `notes_math.md`.)
There are three glass towers, one per family member: a rectangle, a regular pentagon and an alternating hexagon. Floor k
of a tower is the polygon with vertex k forgotten. Every floor is the same plate turned, so the missing corner climbs
a spiral, and a coral bead floats where each forgotten vertex used to be. The rainbow shadows come from the
Beer–Lambert tint of each plate. Engine: `render_tower.py` (convex prisms by half-spaces, numpy ray tracer, strip-parallel).

## Two Veils, One Chance
![Two Veils, One Chance](two_veils_one_chance.png)

The configuration is three circles in a row: red (1), green (r), black (r²). Warm veil: 16,000 random lines through a point of red and a
point of green. Cool veil: 16,000 lines through two points of green. Lines that pierce the pearl are drawn in full
colour, the misses are faint. The two veils look nothing alike, yet both pierce with probability **0.3047** (r = 0.62).
The equality is not pointwise in B; it holds only on average. `render_veils.py`.

## Every Deal Has a Twin
![Every Deal Has a Twin](every_deal_has_a_twin.png)

Eleven pearls, with a warm Hamiltonian necklace and a cool Hamiltonian thread that closes through a coral pearl. The same
threads can be dealt in **16** ways: the original deal plus 15 twins. Every twin has the same total weight, so the original pair
cannot be the unique cheapest on both sides. **Answer to MO 515726: no.** Contract the coral pearl to an edge
and the threads become a 4-regular graph. Thomason (1978) proved that Hamiltonian decompositions of such a graph come in pairs. I also checked it by
direct census: every one of the 191,370 deals on 10 pearls has a twin, an LP shows that no weights exist for n ≤ 9, and the twin count is
always odd. `ham_*.py`, `render_deal.py`.

## Four Ways to Forget a Rectangle
![Four Ways to Forget a Rectangle](four_ways_rectangle.png)

This is the simplest forgetful polygon with its own tower. A rectangle that loses a corner leaves the same right triangle, turned. Sixteen floors make four turns of the spiral, and the diamond windows open where consecutive floors miss different corners.

## Second batch (on request): ideas 4, 5 and 6

### Six Copies of an Odd Triangle
![Six Copies of an Odd Triangle](six_copies_of_an_odd_triangle.png)

This is MO 515413, the Narayana polynomials mod 2. The parity triangle for n ≤ 128 is laid on a triangular lattice with its apex at the
centre, and six copies make a hexagonal doily. Each odd coefficient is a beaded stitch, and neighbouring stitches are tied by
thread. The hue walks outward with n, and the doily sits on a cream plate. The OP's identity
f(2^m + k) = f(k)(1 + t^(2^m)) holds for all n ≤ 512. It is the reason every band of rows is two copies of the ones before it. `render_lace.py`.

### Where the Fly Should Start
![Where the Fly Should Start](where_the_fly_should_start.png)

This is MO 499431, rocks in piles. Each point of the triangle is a way to split 300 rocks into three piles, and the colour is the exact
expected size of the last pile. Honey marks the smallest values, at the balanced split, and a golden Y-shaped valley runs toward the edge midpoints.
The plum threads are single games, the fly's flights, and each ends on a honey spoke when only one pile is left. Exact checks found
**no counterexample** to "balanced is best": K = 3 to N = 500, K = 4 to 200, K = 5 to 60, K = 6 to 40. A new observation: the
runner-up is always the balanced split with one rock moved between two equal piles (254/254 cases). `piles/`.

### The Book Without Sevens
![The Book Without Sevens](the_book_without_sevens.png)

This is MO 515601, the lipogram map. Every n ≤ 10,000 that contains a 7 sends an arc down to the number left when its sevens are
crossed out. The arcs are coloured by the place of the leading seven, and the nested families of bridges show the map acting
on every scale at once. That is also why I conjecture that no fixed formula built from + × − 1/g and the floor function can produce it.
`render_lipo2.py`.

## Six ideas: all six built
1. **Forgetful glass towers** (MO 515731): hero, plus the rectangle go-deeper.
2. **Two veils of random lines** (MO 499477).
3. **Every deal has a twin** (MO 515726).
4. **Narayana parity lace** (MO 515413): second batch.
5. **The fly and the honey pot** (MO 499431): second batch.
6. **The book without sevens** (MO 515601): second batch.

## Tweet
> A polygon wanted to be remembered no matter which corner it lost. Reason told it the price: every corner
> must look like every other. So it became a tower of glass, and each floor forgot a different corner while
> the tower stayed the same.

## Note on generative art (carried forward)
Beauty and legibility both came from **showing the whole orbit, not one instance**. That means every deletion stacked as
floors, every random line drawn edge to edge, and every way of dealing the same threads. When a theorem says "all
of these are the same", show all of them and let the viewer see that they are.
