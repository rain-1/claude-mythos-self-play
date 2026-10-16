// Monte Carlo: probability that a stick broken at 5 iid uniform points gives
// 6 pieces forming the edge lengths of a (nondegenerate) tetrahedron.
// Single-threaded. Usage:
//   ./tetra stats N seed [exp]   -> statistics (exp: use normalized iid Exp(1))
//   ./tetra dump  NS NF seed     -> dump NS successes, NF failures (text)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

// edges in order 01,02,03,12,13,23
static const int EV[6][2] = {{0,1},{0,2},{0,3},{1,2},{1,3},{2,3}};
static int eidx[4][4];
static int A[30][6];   // A[k][e] = rank (in sorted order, 0=smallest) of piece on edge e
static int NA = 0;

static void gen_assignments(void) {
    for (int e = 0; e < 6; e++) { eidx[EV[e][0]][EV[e][1]] = e; eidx[EV[e][1]][EV[e][0]] = e; }
    int sig[24][4], ns = 0;
    for (int a = 0; a < 4; a++) for (int b = 0; b < 4; b++) for (int c = 0; c < 4; c++) for (int d = 0; d < 4; d++)
        if (a!=b && a!=c && a!=d && b!=c && b!=d && c!=d) { sig[ns][0]=a; sig[ns][1]=b; sig[ns][2]=c; sig[ns][3]=d; ns++; }
    int p[6] = {0,1,2,3,4,5};
    // iterate all permutations (Heap's algorithm via simple lexicographic next_permutation)
    for (;;) {
        // canonical form: min over sigma of transformed assignment
        int best[6]; int have = 0;
        for (int s = 0; s < 24; s++) {
            int t[6];
            for (int e = 0; e < 6; e++) t[eidx[sig[s][EV[e][0]]][sig[s][EV[e][1]]]] = p[e];
            if (!have || memcmp(t, best, sizeof t) < 0) { memcpy(best, t, sizeof t); have = 1; }
        }
        if (memcmp(best, p, sizeof best) == 0) { memcpy(A[NA], p, sizeof best); NA++; }
        int i = 4; while (i >= 0 && p[i] > p[i+1]) i--;
        if (i < 0) break;
        int j = 5; while (p[j] < p[i]) j--;
        int tmp = p[i]; p[i] = p[j]; p[j] = tmp;
        for (int l = i+1, r = 5; l < r; l++, r--) { tmp = p[l]; p[l] = p[r]; p[r] = tmp; }
    }
    if (NA != 30) { fprintf(stderr, "NA=%d\n", NA); exit(1); }
}

// xoshiro256**
static uint64_t S[4];
static inline uint64_t rotl(uint64_t x, int k) { return (x << k) | (x >> (64 - k)); }
static inline uint64_t nxt(void) {
    uint64_t r = rotl(S[1] * 5, 7) * 9, t = S[1] << 17;
    S[2] ^= S[0]; S[3] ^= S[1]; S[1] ^= S[2]; S[0] ^= S[3]; S[2] ^= t; S[3] = rotl(S[3], 45);
    return r;
}
static inline double unif(void) { return (nxt() >> 11) * 0x1.0p-53; }
static void seed_rng(uint64_t s) {
    for (int i = 0; i < 4; i++) { s += 0x9E3779B97F4A7C15ULL; uint64_t z = s;
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; S[i] = z ^ (z >> 31); }
}

#define CS(a,b) do { if (x[a] > x[b]) { double t_ = x[a]; x[a] = x[b]; x[b] = t_; } } while (0)
static inline void sort5(double *x) { CS(0,1);CS(3,4);CS(2,4);CS(2,3);CS(1,4);CS(0,3);CS(0,2);CS(1,3);CS(1,2); }
static inline void sort6(double *x) { CS(1,2);CS(4,5);CS(0,2);CS(3,5);CS(0,1);CS(3,4);CS(1,4);CS(0,3);CS(2,5);CS(1,3);CS(2,4);CS(2,3); }

static inline int tri(double a, double b, double c) {
    double m = a > b ? (a > c ? a : c) : (b > c ? b : c);
    return a + b + c > 2.0 * m;
}
// returns 36 V^2 (Gram determinant) if valid tetrahedron, else -1
static inline double check(const double *L) {
    if (!tri(L[0], L[1], L[3]) || !tri(L[0], L[2], L[4]) || !tri(L[1], L[2], L[5]) || !tri(L[3], L[4], L[5])) return -1;
    double a = L[0]*L[0], b = L[1]*L[1], c = L[2]*L[2];
    double g12 = 0.5*(a + b - L[3]*L[3]), g13 = 0.5*(a + c - L[4]*L[4]), g23 = 0.5*(b + c - L[5]*L[5]);
    double det = a*(b*c - g23*g23) - g12*(g12*c - g23*g13) + g13*(g12*g23 - b*g13);
    return det > 0 ? det : -1;
}

static int gen_pieces(double *p, int expmode) {
    if (expmode) {
        double s = 0;
        for (int i = 0; i < 6; i++) { double u; do u = unif(); while (u == 0); p[i] = -log(u); s += p[i]; }
        for (int i = 0; i < 6; i++) p[i] /= s;
    } else {
        double x[5]; for (int i = 0; i < 5; i++) x[i] = unif();
        sort5(x);
        p[0] = x[0]; for (int i = 1; i < 5; i++) p[i] = x[i] - x[i-1]; p[5] = 1.0 - x[4];
    }
    return 0;
}

int main(int argc, char **argv) {
    gen_assignments();
    if (argc < 2) return 1;
    if (!strcmp(argv[1], "list")) {
        for (int k = 0; k < 30; k++) { printf("%2d:", k); for (int e = 0; e < 6; e++) printf(" %d", A[k][e]); printf("\n"); }
        return 0;
    }
    if (!strcmp(argv[1], "stats")) {
        long long N = atoll(argv[2]); seed_rng(strtoull(argv[3], 0, 10));
        int expmode = argc > 4 && !strcmp(argv[4], "exp");
        long long succ = 0, prepass = 0, hist[31] = {0}, okk[30] = {0};
        int ncex[30] = {0}; double cex[30][3][6];
        for (long long n = 0; n < N; n++) {
            double s[6]; gen_pieces(s, expmode); sort6(s);
            double m1 = s[4] + s[1], m2 = s[3] + s[2];
            if ((m1 < m2 ? m1 : m2) <= s[5]) continue;  // necessary condition (two faces on longest edge)
            prepass++;
            int nv = 0, ok[30];
            for (int k = 0; k < 30; k++) {
                double L[6]; for (int e = 0; e < 6; e++) L[e] = s[A[k][e]];
                ok[k] = check(L) > 0; nv += ok[k];
            }
            hist[nv]++;
            if (nv) {
                succ++;
                for (int k = 0; k < 30; k++) {
                    okk[k] += ok[k];
                    if (!ok[k] && ncex[k] < 3) { memcpy(cex[k][ncex[k]], s, sizeof s); ncex[k]++; }
                }
            }
        }
        printf("N %lld\nsucc %lld\nprepass %lld\n", N, succ, prepass);
        printf("hist"); for (int i = 0; i <= 30; i++) printf(" %lld", hist[i]); printf("\n");
        for (int k = 0; k < 30; k++) {
            printf("assign %d ranks", k); for (int e = 0; e < 6; e++) printf(" %d", A[k][e]);
            printf(" ok %lld", okk[k]);
            for (int c = 0; c < ncex[k]; c++) { printf(" cex"); for (int i = 0; i < 6; i++) printf(" %.17g", cex[k][c][i]); }
            printf("\n");
        }
        return 0;
    }
    if (!strcmp(argv[1], "dump")) {
        int NS = atoi(argv[2]), NF = atoi(argv[3]); seed_rng(strtoull(argv[4], 0, 10));
        int gs = 0, gf = 0;
        while (gs < NS || gf < NF) {
            double p[6]; gen_pieces(p, 0);
            int id[6] = {0,1,2,3,4,5};
            for (int i = 1; i < 6; i++) for (int j = i; j > 0 && p[id[j]] < p[id[j-1]]; j--) { int t = id[j]; id[j] = id[j-1]; id[j-1] = t; }
            int nv = 0, bk = -1; double bv = -1;
            for (int k = 0; k < 30; k++) {
                double L[6]; for (int e = 0; e < 6; e++) L[e] = p[id[A[k][e]]];
                double d = check(L);
                if (d > 0) { nv++; if (d > bv) { bv = d; bk = k; } }
            }
            if (nv && gs < NS) {
                printf("S"); for (int i = 0; i < 6; i++) printf(" %.17g", p[i]);
                for (int e = 0; e < 6; e++) printf(" %d", id[A[bk][e]]);
                printf(" %d %.17g\n", nv, sqrt(bv / 36.0)); gs++;
            } else if (!nv && gf < NF) {
                printf("F"); for (int i = 0; i < 6; i++) printf(" %.17g", p[i]); printf("\n"); gf++;
            }
        }
        return 0;
    }
    if (!strcmp(argv[1], "masks")) {   // histogram of 30-bit validity masks among successes
        long long N = atoll(argv[2]); seed_rng(strtoull(argv[3], 0, 10));
        const int HS = 1 << 22; uint32_t *key = calloc(HS, 4); long long *cnt = calloc(HS, 8);
        for (long long n = 0; n < N; n++) {
            double s[6]; gen_pieces(s, 0); sort6(s);
            double m1 = s[4] + s[1], m2 = s[3] + s[2];
            if ((m1 < m2 ? m1 : m2) <= s[5]) continue;
            uint32_t m = 0;
            for (int k = 0; k < 30; k++) { double L[6]; for (int e = 0; e < 6; e++) L[e] = s[A[k][e]]; if (check(L) > 0) m |= 1u << k; }
            if (!m) continue;
            uint32_t h = (m * 2654435761u) >> 10;
            while (key[h] && key[h] != m) h = (h + 1) & (HS - 1);
            key[h] = m; cnt[h]++;
        }
        for (int i = 0; i < HS; i++) if (key[i]) printf("%u %lld\n", key[i], cnt[i]);
        return 0;
    }
    if (!strcmp(argv[1], "single")) {  // first example (sorted pieces) where assignment k is the ONLY valid one
        long long N = atoll(argv[2]); seed_rng(strtoull(argv[3], 0, 10));
        int found[30] = {0};
        for (long long n = 0; n < N; n++) {
            double s[6]; gen_pieces(s, 0); sort6(s);
            double m1 = s[4] + s[1], m2 = s[3] + s[2];
            if ((m1 < m2 ? m1 : m2) <= s[5]) continue;
            int nv = 0, last = -1;
            for (int k = 0; k < 30; k++) { double L[6]; for (int e = 0; e < 6; e++) L[e] = s[A[k][e]]; if (check(L) > 0) { nv++; last = k; } }
            if (nv == 1 && !found[last]) { found[last] = 1; printf("only %d:", last); for (int i = 0; i < 6; i++) printf(" %.17g", s[i]); printf("\n"); fflush(stdout); }
        }
        return 0;
    }
    return 1;
}
