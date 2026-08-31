# f(n) census NMAX=8192 — predictions written BEFORE the run (predict-then-confirm)
1. Exactly ONE new record in (4096, 8192]: f = 36 at n = interior count of the
   circle (2x-a)^2+(2y-b)^2 = 4225 (= 5^2 * 13^2, center denominator 2, rim
   r2-odd-odd = 4*(2+1)*(2+1) = 36), r = 32.5, n approx pi*4225/2 - rim-ish
   correction ~ 6630 +- 40.
2. The void stays unique: n = 6 remains the only n <= 8192 with NO circle
   through >= 3 lattice points having exactly n interior points.
3. Stragglers (f(n)=3) stay rare and thin: at most ~3 new values beyond 883
   in (4096, 8192], all with exotic center denominators (>= 30).
4. Parity bound floor(2+sqrt(8n+4)) tight NOWHERE in (4, 8192].
5. Cross-check: f=20 at 968 (=I(20)), f=18 unique at 3312 within 4096 window
   must reproduce identically in the deeper run (same engine, wider RMAX).
