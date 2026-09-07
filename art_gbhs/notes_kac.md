# Kac's ring — the exact solution behind *The Ring That Only Slept*

Mark Kac (1956) built the simplest model in which perfectly reversible dynamics looks
irreversible: N balls on a ring, each white or black, M of the N edges carrying a marker; each
step every ball moves one site clockwise and flips colour when it crosses a marker.

## Closed form (`kac.py`, checked against brute-force stepping for every cell)

Let S(j) be the number of markers on edges 0..j−1, extended by S(j+N) = S(j) + M. The ball at
site i at time t started at site i − t and has crossed exactly S(i) − S(i−t) markers, so

    colour(i, t) = colour₀(i − t) ⊕ parity(S(i) − S(i−t)),     flips(i, t) = S(i) − S(i−t).

So the whole space–time carpet is a *difference pattern* of one integer sequence S: the pixel
(i, t) compares S at the ball's present site with S at its birthplace. In the polar carpet
(angle = site, radius = time) the boundaries where S(i) changes are radial lines through the
markers; the boundaries where S(i−t) changes are the spirals i − t = const. The picture is the
XOR of a fan and a pinwheel — a loom whose warp is the present and whose weft is the past.

## The two theorems the picture shows

* **Recurrence.** flips(i, 2N) = 2M for every i, so colour(i, 2N) = colour₀(i): the ring is
  exactly what it was. With M odd, flips(i, N) = M is odd for every i: at t = N every ball is
  the opposite of what it was (the uniform ring at half radius, coral hairline).
* **Kac's greyness.** G(t) = (white − black)/N. For a *random* marker set of density μ = M/N
  the ensemble average is (1 − 2μ)^t, an exponential decay to grey — the "death". A single
  ring's exact G(t) follows it for the first steps, then wanders near zero with fluctuations
  of order 1/√N (|G| ≤ 0.22 in the middle window for N = 720, M = 37), and returns to −1
  at t = N and to +1 at t = 2N.

Final render: N = 720, M = 37 (μ = 0.0514), seed 7, all-white start. Certificate file
`kac_2560_cert.json`: closed form == brute force (True), recurrence at 2N (True),
anti-recurrence at N (True), G(1..7) = 0.897, 0.803, 0.719, 0.647, 0.586, 0.514, 0.464 vs
(1−2μ)^t = 0.897, 0.805, 0.722, 0.648, 0.581, 0.521, 0.468.

The chart under the ring uses a broken axis: the first 80 steps magnified (the coral exponential
lives there), then the remaining 1360 steps; the spike to −1 at t = N and the return to +1 at
t = 2N are the whole point.

## Why it fits the run

The Philosophy.SE front page asked whether sleep is the cousin of death (141468). Kac's ring
is the mathematical version of the distinction: what looks like dying (the exponential) is a
bijection all the way down, and the ring wakes at 2N with nothing lost. The second panel of the
triptych *Wake* is the pun's middle sense.
