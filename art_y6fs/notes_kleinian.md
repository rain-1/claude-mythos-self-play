# Notes — Indra's Curve

**Object.** The limit set of the quasi-Fuchsian punctured-torus group with tr a = 1.91+0.05i,
tr b = 1.91−0.05i (complex-conjugate traces ⇒ the picture has a mirror symmetry), built by
"Grandma's recipe" (Mumford–Series–Wright, *Indra's Pearls*, ch. 8): tr ab is the root of the
Markov-type identity tr a·tr b·tr ab = tr²a + tr²b + tr²ab that makes the commutator
parabolic, tr[a,b] = −2. The group is discrete, its limit set is a Jordan curve (a
quasicircle), and the two complementary components are each a punctured torus modulo Γ.

**Certificates (from `kleinian_2560_cert.json`).**
| check | value |
|---|---|
| tr[a,b] | −2 − 6.7e−16 i |
| Markov identity residual | 8.9e−16 |
| det a, det b | 1 to 1e−16 |
| DFS leaf points on the curve | 1 422 662 (2 133 991 words visited) |
| consecutive-point gaps at 5120² | median 0.39 px, p99 1.65 px, max 27.9 px |
| pearls drawn (inside / outside) | 43 192 / 19 480, radii 0.45 px … 198 px / 717 px |

The gap statistics are the machine form of "the DFS in cyclic order [a, B, A, b] with children
[i−1, i, i+1] visits the curve in order": the plotted points are consecutive along a Jordan
curve, so the polygon through them can be filled (inside wash) and its two sides are the two
components of the ordinary set.

**The pearls.** At the parabolic fixed point P₀ of the commutator K = aBAb the K-invariant
circles through P₀ are the horocycles; their tangent direction at P₀ is read off the
circumcircle of (P₀, K(q), K⁻¹(q)). One horoball on each side of the curve is sized to the
largest embedded one (min over curve points z of |z−P₀|²/(2 Re((z−P₀)n̄))), then shrunk
until no image under a word of length ≤ 3 outside ⟨K⟩ meets it (precise invariance,
radii 0.476 inside, 0.475 outside after a 0.55 aesthetic shrink). Every word w of the DFS
draws w(ball); words differing by a power of K give the same ball (deduplicated on a
0.25 px key). A word whose pole lies inside the ball maps it to the *exterior* of a circle,
not a disc — those (195 of them in the outside orbit at the test size) are skipped, which
is why the earliest draft had blue "beach balls" inside the apricot region.

**Hierarchy as palette.** Side of the curve → warm (coral / apricot / lemon / blush) or cool
(aqua / cornflower / lavender / mint); first letter of the word → which of the four; depth
of the word → pigment density (deeper = darker: the small pearls crowding the curve are the
long words). The curve itself is one crisp ink line. Cusps: every pearl touches the curve at
exactly one point — an image of P₀.

**Seed.** Phil.SE 141195, the "dramatic" model of reality: everything is one thing in
disguise. The whole lace is the orbit of one point under two maps; every address (word) shows
the same cusp from somewhere else. MO 514840 (roots of unity without analysis) supplied the
mood of "pure algebra drawing a picture".
