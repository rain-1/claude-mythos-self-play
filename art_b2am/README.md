# The Negation of the Negation

*A triptych. Run of 2026-07-17 · branch `claude/zen-meitner-b2amu4`.*

Seeded from the live front pages. **Philosophy.SE** was saturated with Hegel and
Marxism — *"Negation of Negation and Spiral Ascent," "the law of qualitative
change," "the wave-like progress diagram," "quantity → quality."* **MathOverflow**
offered, among others, the functional-equation map `f(x)+f(1/x)=1/2` and the
chirality of the snub polyhedra.

The dialectical thread wanted a mathematical body. It found one in the
**automatic sequences** — the sequences that are fixed points of a *complement*-based
substitution. They are the literal arithmetic of *"the negation of the negation":*
apply negation twice at every scale and the seed returns, transformed and larger.
Three of them, each shown in the lens where it is most alive.

## The three panels

**THE FOLD** — *geometry* — `hero_the_fold.png` (4096²)
The regular **paperfolding sequence**: fold a strip in half, and in half again,
forever; unfold. Its turn sequence obeys `s → s, 1, complement(reverse(s))` — the
new half is the *negation of the reversed* old half. Drawn on the plane (90° turns)
this is the **Heighway dragon**: one unit-step curve that coils, **spirals**
(the live "spiral ascent"), and fills the plane. Order k=19 (524 288 segments),
rotated 70° so the lattice weave reads as an organic mezzotint; colored by arc-time
through a shared dusk ramp.

**THE SHATTERING** — *analysis* — `companion_the_shattering.png` (2560²)
The **Thue–Morse** diffraction measure, as a ridgeline waterfall. At the bottom
(k=1) a single smooth cosine — an *absolutely continuous* density. Each doubling
splits every peak; by the top (k=13) it is a self-similar spray of spikes. The
Thue–Morse crystal has **no Bragg peaks at all** — a purely *singular-continuous*
spectrum, an order you cannot resolve into pure tones. Quantity (levels) becomes
quality (a new kind of measure): the *law of qualitative change*, drawn.

**THE TILING** — *arithmetic* — `companion_the_tiling.png` (2560²)
The dragon is a **number system**. In base `b = −1+i` with digits `{0,1}` — a
canonical number system — every Gaussian integer has a unique finite expansion,
and the fractional tile `T = {Σ dₖ b⁻ᵏ}` is the **twindragon**. Its ℤ[i]-translates
pave the plane with no gaps and no overlaps, each tile one address. The boundary
between neighboring tiles is exactly the fold of the hero: the same object, seen as
*territory* instead of *path*.

## Verified (`verify_all.py`)
- Thue–Morse fixed point `t[2n]=t[n], t[2n+1]=1−t[n]`; every block's 2nd half is the negation of its 1st.
- **Woods–Robbins**: `∏ ((2n+1)/(2n+2))^((−1)^tₙ) = 1/√2`, to `1.2e−13`.
- Generating function `Σ(−1)^tₙ xⁿ = ∏(1−x^{2ᵏ})`.
- **Prouhet–Tarry–Escott**: the Thue–Morse signs split `{0…2ᵏ−1}` into two sets with *equal power sums* through degree k−1.
- Diffraction density `wₖ(θ) = ∏_{j<k} 2sin²(π2ʲθ)` is a probability measure (`∫wₖdθ = 1`).
- Paperfolding recursion `2nd half = −reverse(1st half)`.
- Base `−1+i`, digits `{0,1}`: unique finite expansion of every Gaussian integer.

## Files
`hero_dragon.py`, `companion_diffraction.py`, `companion_tiling.py`,
`tm_common.py` (shared), `make_contact.py`, `verify_all.py`, `contact_sheet.png`.

## Story
> A strip of paper is folded, and folded again — each crease the reversal of the
> last, each generation the negation of the one before. Unfold it: a dragon. It
> never repeats and never escapes itself; it is its own opposite at every scale,
> and out of that quarrel it fills a whole plane. The same refusal to settle,
> heard as sound, is a spectrum with no clear notes; counted as arithmetic, it is
> a perfect balance; laid flat, it is a floor that tiles forever. Progress, the
> old dialecticians said, is not a circle and not a line but a spiral — you return
> to where you began, one turn higher. Here is the spiral, drawn by a sheet of
> paper that could not stop disagreeing with itself.
