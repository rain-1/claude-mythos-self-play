# Notes — The Tree and Its Path

**Object.** A spanning tree of the 320×320 grid drawn uniformly at random from all of them
(Wilson's algorithm: start loop-erased random walks from every vertex in turn, attach where
they first hit the growing tree — exact uniform sampling, no Markov-chain mixing), and the
Peano curve that winds between the tree and its planar dual, extracted as the 0.5-contour of
the thickened tree (one closed contour of 3 146 285 points: the dual is also a tree).

**Certificates.**
| quantity | measured (bulk, 8 cells from the boundary) | exact (Burton–Pemantle 1993, Z²) |
|---|---|---|
| P(degree 1) — leaves | 0.29548 | 8/π²·(1−2/π) = 0.294535 |
| P(degree 2) | 0.44498 | 0.446988 |
| P(degree 3) | 0.22337 | 0.222394 |
| P(degree 4) | 0.03617 | 0.036082 |

Branch growth (`ust_extra.py`): by Wilson's construction the branch from any vertex u toward
the root is a loop-erased random walk, so the number of tree steps until the branch first
leaves the ball of radius r around u should scale as r^{5/4} (the LERW growth exponent,
Kenyon; SLE₂). Over 20 000 starts in the central half and radii 3…80 the log-log slope of
the median is **1.238** (prediction 1.25). A first attempt measured the *mean* tree-path
length between two random vertices at distance r and got slope 0.6, then 1.04 with medians —
wrong certificate, not wrong tree: that path is a loop-erased walk on the scale of the whole
box (a 2-D walk explores the box before hitting a point), so r sets nothing.

**The picture.** Every pixel takes the hue of the nearest point of the Peano curve, with the
hue running three times round the pastel cycle along the curve's length — so a patch of one
colour is a stretch of the path, i.e. a subtree: the map is the tree's own partition of the
plane into branches. Lightness falls with depth from the root (the coral bloom). The tree is
drawn in ink with width and density ∝ log(subtree mass) after two Laplacian smoothing passes
on node positions (bent threads, not staircases); the path itself is a faint sepia thread.

**Seed.** Phil.SE 141195, the "organic" model of reality — one organism, every part
connected to every other, growing from one now to the next. The tree is grown by wandering
and forgetting (loop erasure), and it is uniform: no design, and yet exactly 29.45 % of it
is leaves.
