/* wythoff.c -- Grundy values of Wythoff's game on an N x N board.
   Two piles (m,n).  A move takes any positive number from one pile, or the SAME
   positive number from both.  G(m,n) = mex of the options' Grundy values.
   The P-positions (G = 0) are the Beatty pairs (floor(k*phi), floor(k*phi^2)).

   One pass with incremental bitsets: the option set of (m,n) is exactly
   (values above it in column n) U (values left of it in row m) U (values up the
   main diagonal), each maintained as a bitset.  O(N^2 * Vmax/64).           */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int N, VW;                     /* VW = words per bitset */

static inline int mex3(const uint64_t *a, const uint64_t *b, const uint64_t *c) {
    for (int w = 0; w < VW; w++) {
        uint64_t u = ~(a[w] | b[w] | c[w]);
        if (u) return w * 64 + __builtin_ctzll(u);
    }
    return VW * 64;
}

int main(int argc, char **argv) {
    N = (argc > 1) ? atoi(argv[1]) : 1024;
    const char *out = (argc > 2) ? argv[2] : "wythoff.bin";
    int VMAX = 4 * N + 64;
    VW = (VMAX + 63) / 64;
    int32_t *G = malloc((size_t)N * N * sizeof(int32_t));
    uint64_t *row = calloc((size_t)N * VW, 8);
    uint64_t *col = calloc((size_t)N * VW, 8);
    uint64_t *dia = calloc((size_t)(2 * N) * VW, 8);
    if (!G || !row || !col || !dia) { fprintf(stderr, "oom\n"); return 1; }
    int gmax = 0;
    for (int m = 0; m < N; m++) {
        uint64_t *rm = row + (size_t)m * VW;
        for (int n = 0; n < N; n++) {
            uint64_t *cn = col + (size_t)n * VW;
            uint64_t *dd = dia + (size_t)(m - n + N) * VW;
            int g = mex3(rm, cn, dd);
            G[(size_t)m * N + n] = g;
            if (g > gmax) gmax = g;
            if (g >= VMAX) { fprintf(stderr, "VMAX overflow at %d %d -> %d\n", m, n, g); return 2; }
            uint64_t bit = 1ULL << (g & 63);
            rm[g >> 6] |= bit; cn[g >> 6] |= bit; dd[g >> 6] |= bit;
        }
    }
    FILE *f = fopen(out, "wb");
    fwrite(G, sizeof(int32_t), (size_t)N * N, f);
    fclose(f);
    fprintf(stderr, "N=%d  max Grundy=%d  (VMAX=%d)\n", N, gmax, VMAX);
    return 0;
}
