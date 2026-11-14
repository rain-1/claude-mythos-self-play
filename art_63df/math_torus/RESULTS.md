# 25 equal circles on the square flat torus — notes on MO 490278

* The packing in the question has d = 0.2051955…; an answer improves it to
  d² = (13 − 6√3)/61, d = 0.2067585570… (`torus.py` holds its coordinates in ℚ(√3)/122).
* `faces.py`: the contact graph of the improved packing has 25 vertices, 62 edges, degrees
  4⁵ 5¹⁶ 6⁴, and its 37 faces are **24 equilateral triangles and 13 squares** (every 4-face has a
  right angle to 1e-9). So the area equation is the whole algebra:

      24 · (√3/4) d² + 13 d² = 1   ⇒   d² = 1/(13 + 6√3) = (13 − 6√3)/61.

  Equivalently the period (1, 0) is 3 + 2ζ₁₂ steps of length d (|3 + 2ζ₁₂|² = 13 + 6√3): three
  steps east and two at 30°. That is why this packing has a degree-4 minimal polynomial while the
  question's needs degree in the hundreds.
* Search (`torus.py 25 1500 7`): 1,500 random starts (repulsion with growing exponent, then
  sequential LP polish) reached 0.206758557 sixty-seven times, the question's 0.20519553 1,403
  times, 0.205686139 eleven times, and nothing better. Evidence, not proof, that the
  triangle–square packing is optimal for N = 25.
* Remark: a triangle–square tiling of the square torus with t triangles and q squares needs
  t√3/4 + q = 1/d² with (t, q) forced by a Gaussian-like norm from ℤ[ζ₁₂]; N = (t + 2q)/2 = 25
  here. Which N admit such a tiling of the *square* torus (two orthogonal periods of equal
  length in ℤ[ζ₁₂])? 3 + 2ζ₁₂ and i(3 + 2ζ₁₂) is the smallest non-trivial pair I know of.
