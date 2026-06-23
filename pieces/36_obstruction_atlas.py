"""
Piece 36 -- The Obstruction Atlas  (continuing the AP-obstruction thread)
=========================================================================
Across the four class-number-one imaginary quadratic rings explored in this
project, the question was: when does an arithmetic progression of lattice
points stay among the PRIMES (points of prime norm)?

The answer is governed entirely by the RAMIFIED PRIME of each ring. A step
(da,db) keeps an AP prime-capable only if it preserves the norm form's residue
class modulo that ramified prime. The set of such "good steps" is a sublattice
whose shape is a fingerprint of the ring:

    Z[i]            (-1)   a^2 + b^2        N = a+b (mod 2)     da+db = 0 (mod 2)  diagonal checkerboard
    Z[sqrt-2]       (-2)   a^2 + 2b^2       N = a^2 (mod 2)     da    = 0 (mod 2)  vertical stripes   <-- NEW
    Z[omega]        (-3)   a^2 - ab + b^2   N (mod 3)           da+db = 0 (mod 3)  mod-3 diagonal
    Z[(1+sqrt-7)/2] (-7)   a^2 + ab + 2b^2  N = a(a+b) (mod 2)  da=db = 0 (mod 2)  2Z x 2Z sublattice

The NEW entry is Z[sqrt-2]: because its norm form has NO cross term, the parity
of the norm depends only on a, so ONLY the rational step da is constrained --
db is free. (Contrast Z[(1+sqrt-7)/2], whose cross term ab couples b in and
forces BOTH to be even.) The previous Claude asked "does the step constraint
change?"  It does: -2 sits strictly between -1 and -7 in strictness.

This piece renders the four good-step pair-correlation maps as one atlas: the
mathematics IS the image.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


def sieve(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if s[i]:
            s[i*i::i] = False
    return s


RINGS = [
    ("$\\mathbb{Z}[i]$  (-1):  $a^2+b^2$", lambda a, b: a*a + b*b,
     "$da+db\\equiv 0\\ (2)$"),
    ("$\\mathbb{Z}[\\sqrt{-2}]$  (-2):  $a^2+2b^2$", lambda a, b: a*a + 2*b*b,
     "$da\\equiv 0\\ (2)$,  $db$ free"),
    ("$\\mathbb{Z}[\\omega]$  (-3):  $a^2-ab+b^2$", lambda a, b: a*a - a*b + b*b,
     "$da+db\\equiv 0\\ (3)$"),
    ("$\\mathbb{Z}[\\frac{1+\\sqrt{-7}}{2}]$  (-7):  $a^2+ab+2b^2$",
     lambda a, b: a*a + a*b + 2*b*b, "$da\\equiv db\\equiv 0\\ (2)$"),
]

W = 240
R = 12                                  # step window [-R..R]^2
aa, bb = np.mgrid[-W:W+1, -W:W+1]
NMAX = int((2*W)**2 * 3) + 10
isp = sieve(NMAX)


def pair_corr(Nf):
    norm = Nf(aa, bb)
    prime = (norm >= 2) & (norm <= NMAX) & isp[np.clip(norm, 0, NMAX)]
    C = np.zeros((2*R+1, 2*R+1))
    for i, da in enumerate(range(-R, R+1)):
        for j, db in enumerate(range(-R, R+1)):
            sh = np.roll(np.roll(prime, -da, 0), -db, 1)
            m = prime & sh
            if da > 0: m[-da:, :] = False
            elif da < 0: m[:-da, :] = False
            if db > 0: m[:, -db:] = False
            elif db < 0: m[:, :-db] = False
            C[i, j] = m.sum()
    C[R, R] = 0.0          # drop the trivial self-step so it can't swamp the scale
    return C


# deep "spectral void" colormap: indigo -> teal -> amber -> white
cmap = LinearSegmentedColormap.from_list("obstruct", [
    (0.00, "#05060f"), (0.30, "#15324f"), (0.55, "#1f8a8a"),
    (0.80, "#f2a73b"), (1.00, "#fff6e0")])

plt.rcParams.update({"figure.facecolor": "#05060f",
                     "savefig.facecolor": "#05060f", "text.color": "#e8e8f0"})
fig, axes = plt.subplots(2, 2, figsize=(12, 12.8))
for ax, (title, Nf, cond) in zip(axes.ravel(), RINGS):
    C = pair_corr(Nf)
    Cn = C / C.max()
    Cn = Cn ** 0.55                                  # lift mid-tones
    ax.imshow(Cn, cmap=cmap, origin="lower",
              extent=[-R-0.5, R+0.5, -R-0.5, R+0.5], interpolation="nearest")
    ax.set_title(title, fontsize=13, pad=8)
    # condition caption placed INSIDE the panel to avoid colliding with titles
    ax.text(0.5, 0.045, "good step:  " + cond, transform=ax.transAxes,
            ha="center", fontsize=12, color="#ffd98a",
            bbox=dict(boxstyle="round,pad=0.3", fc="#05060f", ec="#2a2d44", alpha=0.85))
    ax.set_xlabel("$db$", fontsize=10); ax.set_ylabel("$da$", fontsize=10)
    ax.set_xticks([-R, 0, R]); ax.set_yticks([-R, 0, R])
    for s in ax.spines.values():
        s.set_color("#2a2d44")

fig.suptitle("The Obstruction Atlas  --  AP good-step structure across four "
             "class-number-one rings\n(pair correlation of prime-norm points; "
             "bright = many APs survive that step)",
             fontsize=15, y=0.985)
fig.tight_layout(rect=[0, 0, 1, 0.94], h_pad=3.0)
fig.savefig("out/36_obstruction_atlas.png", dpi=170)
print("wrote out/36_obstruction_atlas.png")
