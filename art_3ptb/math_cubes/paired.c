/* Paired-form search:
 *   n = sum_{k=1}^3 [ (A_k x + u_k)^3 - (A_k x + v_k)^3 ],  s_k = u_k - v_k, S_k = u_k + v_k
 * conditions: sum s_k A_k^2 = 0, sum s_k A_k S_k = 0,  n = sum s_k (3 S_k^2 + s_k^2)/4.
 * WLOG A_k > 0. For fixed (A,s) the admissible S form a lattice coset in the plane
 * P = {w.S = 0}, w_k = s_k A_k, with S = s (mod 2); on P, n depends only on
 * phi(S) = S1 A2 - S2 A1 (P cap ker phi = Z A/gcd(A), the x-shift).
 * usage: paired H N  -> for each |n|<=N the min-height rep found: "n h A1 u1 v1 A2 u2 v2 A3 u3 v3"
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
typedef long long ll;
static ll gcdl(ll a, ll b) { if (a < 0) a = -a; if (b < 0) b = -b; while (b) { ll t = a % b; a = b; b = t; } return a; }
static ll egcd(ll a, ll b, ll *x, ll *y) { /* returns g=gcd>=0, a*x+b*y=g */
    if (b == 0) { *x = a >= 0 ? 1 : -1; *y = 0; return a >= 0 ? a : -a; }
    ll x1, y1; ll g = egcd(b, a % b, &x1, &y1); *x = y1; *y = x1 - (a / b) * y1; return g;
}
int N, H;
int *besth; int (*bestrep)[9];
static void consider(ll A[3], ll s[3], ll S[3]) {
    /* compute n and height; try x-shifts S + 2j A0 */
    ll g = gcdl(gcdl(A[0], A[1]), A[2]);
    ll A0[3] = {A[0] / g, A[1] / g, A[2] / g};
    /* shift: S -> S + 2 j A0 ; choose j near minimizing max|S| */
    double num = 0, den = 0; for (int k = 0; k < 3; k++) { num += (double)S[k] * A0[k]; den += (double)A0[k] * A0[k]; }
    ll j0 = (ll)llround(-num / den / 2.0);
    for (ll j = j0 - 2; j <= j0 + 2; j++) {
        ll T[3]; int h = 0;
        for (int k = 0; k < 3; k++) {
            T[k] = S[k] + 2 * j * A0[k];
            ll u = (T[k] + s[k]) / 2, v = (T[k] - s[k]) / 2;
            ll m = A[k]; if (llabs(u) > m) m = llabs(u); if (llabs(v) > m) m = llabs(v);
            if (m > h) h = (int)m;
        }
        if (h > H) continue;
        ll num4 = 0; for (int k = 0; k < 3; k++) num4 += s[k] * (3 * T[k] * T[k] + s[k] * s[k]);
        if (num4 % 4) { fprintf(stderr, "nonint!\n"); exit(1); }
        ll n = num4 / 4;
        if (n < -N || n > N) continue;
        if (h < besth[n + N]) {
            besth[n + N] = h;
            for (int k = 0; k < 3; k++) { bestrep[n + N][3*k] = (int)A[k]; bestrep[n + N][3*k+1] = (int)((T[k] + s[k]) / 2); bestrep[n + N][3*k+2] = (int)((T[k] - s[k]) / 2); }
        }
    }
}
int main(int argc, char **argv) {
    H = atoi(argv[1]); N = atoi(argv[2]);
    besth = malloc(sizeof(int) * (2 * N + 1)); bestrep = malloc(sizeof(int[9]) * (2 * N + 1));
    for (int i = 0; i <= 2 * N; i++) besth[i] = 1 << 30;
    ll A[3], s[3];
    for (A[0] = 1; A[0] <= H; A[0]++) for (A[1] = 1; A[1] <= H; A[1]++) for (A[2] = 1; A[2] <= H; A[2]++) {
        ll a2 = A[2] * A[2];
        for (s[0] = -2 * H; s[0] <= 2 * H; s[0]++) for (s[1] = -2 * H; s[1] <= 2 * H; s[1]++) {
            ll r = -(s[0] * A[0] * A[0] + s[1] * A[1] * A[1]);
            if (r % a2) continue;
            s[2] = r / a2;
            if (s[2] == 0 || llabs(s[2]) > 2 * H) continue;
            /* lattice P = ker w, w = s_k A_k */
            ll w[3] = {s[0] * A[0], s[1] * A[1], s[2] * A[2]};
            ll v1[3], v2[3];
            if (w[0] == 0 && w[1] == 0) { v1[0] = 1; v1[1] = 0; v1[2] = 0; v2[0] = 0; v2[1] = 1; v2[2] = 0; }
            else {
                ll x, y; ll g12 = egcd(w[0], w[1], &x, &y);
                v1[0] = w[1] / g12; v1[1] = -w[0] / g12; v1[2] = 0;
                ll g = gcdl(g12, w[2]);
                v2[0] = x * (w[2] / g); v2[1] = y * (w[2] / g); v2[2] = -g12 / g;
            }
            ll p1 = v1[0] * A[1] - v1[1] * A[0], p2 = v2[0] * A[1] - v2[1] * A[0];
            ll xa, ya; ll gg = egcd(p1, p2, &xa, &ya);
            if (gg == 0) continue;
            for (int a0 = 0; a0 < 2; a0++) for (int b0 = 0; b0 < 2; b0++) {
                ll Sb[3]; int ok = 1;
                for (int k = 0; k < 3; k++) { Sb[k] = a0 * v1[k] + b0 * v2[k]; if (((Sb[k] - s[k]) % 2 + 2) % 2) ok = 0; }
                if (!ok) continue;
                /* phi = phi_b + 2*gg*t; S = Sb + 2 t (xa v1 + ya v2) (+ x-shift) */
                ll dS[3]; for (int k = 0; k < 3; k++) dS[k] = 2 * (xa * v1[k] + ya * v2[k]);
                /* phi range limited by height: |phi| <= |S1|A2+|S2|A1 <= 2H(A1+A2) */
                ll phib = a0 * p1 + b0 * p2;
                ll lim = 2 * H * (A[0] + A[1]) + 2;
                ll tlo = (-lim - phib) / (2 * gg) - 1, thi = (lim - phib) / (2 * gg) + 1;
                for (ll t = tlo; t <= thi; t++) {
                    ll S[3]; for (int k = 0; k < 3; k++) S[k] = Sb[k] + t * dS[k];
                    consider(A, s, S);
                }
            }
        }
    }
    for (int n = -N; n <= N; n++) if (besth[n + N] < (1 << 30)) {
        printf("%d %d", n, besth[n + N]);
        for (int k = 0; k < 9; k++) printf(" %d", bestrep[n + N][k]);
        printf("\n");
    }
    return 0;
}
