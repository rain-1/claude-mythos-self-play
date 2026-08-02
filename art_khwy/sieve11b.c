/* Atlas piece 38: S = { n <= N representable as x^2 + xy + 3y^2 }
   (norm form of O_{Q(sqrt(-11))}, class number 1, ramified prime 11).
   Mark all represented n, then scan consecutive elements of S for
   maximal equal-gap runs; record first occurrence per run length.
   Output: records + residue histogram mod 11 + element count.        */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

int main(int argc, char** argv) {
    int64_t N = (argc > 1) ? atoll(argv[1]) : 1000000000LL;
    uint8_t *bit = calloc((N >> 3) + 2, 1);
    if (!bit) { fprintf(stderr, "alloc fail\n"); return 1; }
    /* Q(x,y) = x^2 + xy + 3y^2 = (x + y/2)^2 + 11 y^2 / 4  >= 11y^2/4 */
    int64_t ymax = (int64_t)(sqrt(4.0 * (double)N / 11.0)) + 2;
    for (int64_t y = 0; y <= ymax; y++) {
        double disc;
        /* x^2 + x*y + (3y^2 - N) <= 0  => x in [(-y - s)/2, (-y + s)/2],
           s = sqrt(y^2 - 4(3y^2 - N)) = sqrt(4N - 11 y^2) */
        double t = 4.0 * (double)N - 11.0 * (double)y * (double)y;
        if (t < 0) break;
        disc = sqrt(t);
        int64_t xlo = (int64_t)ceil((-(double)y - disc) / 2.0) - 1;
        int64_t xhi = (int64_t)floor((-(double)y + disc) / 2.0) + 1;
        for (int64_t x = xlo; x <= xhi; x++) {
            int64_t q = x*x + x*y + 3*y*y;
            if (q >= 1 && q <= N) bit[q >> 3] |= (uint8_t)(1 << (q & 7));
        }
    }
    /* scan: elements of S ascending; run = maximal equal-gap streak */
    int64_t prev = -1, gap = -1, runlen = 1, runstart = -1;
    int64_t first[40]; int64_t firstgap[40];
    for (int i = 0; i < 40; i++) first[i] = -1;
    int64_t count = 0; int64_t res11[11] = {0};
    static int64_t hist[11][512]; /* channel x log-bin */
    int maxrec = 2;
    for (int64_t nn = 1; nn <= N; nn++) {
        if (!(bit[nn >> 3] & (1 << (nn & 7)))) continue;
        count++; res11[nn % 11]++;
        { int b = (int)(48.0 * log10((double)nn)); if (b > 511) b = 511;
          hist[nn % 11][b]++; }
        if (prev >= 0) {
            int64_t g = nn - prev;
            if (g == gap) runlen++;
            else { gap = g; runlen = 2; runstart = prev; }
            /* runlen elements share (runlen-1) equal gaps => AP of length runlen */
            if (runlen < 40 && first[runlen] < 0) {
                first[runlen] = runstart;
                firstgap[runlen] = gap;
                if (runlen > maxrec) maxrec = runlen;
                printf("l=%lld first AP start=%lld gap=%lld end=%lld\n",
                    (long long)runlen, (long long)first[runlen],
                    (long long)firstgap[runlen], (long long)nn);
                fflush(stdout);
            }
        }
        prev = nn;
    }
    printf("N=%lld |S|=%lld density=%.6f\n", (long long)N, (long long)count,
           (double)count / (double)N);
    printf("res mod 11: ");
    for (int i = 0; i < 11; i++) printf("%lld ", (long long)res11[i]);
    printf("\n");
    FILE* f = fopen("hist11.txt", "w");
    for (int i = 0; i < 11; i++) {
        for (int b = 0; b < 512; b++) fprintf(f, "%lld ", (long long)hist[i][b]);
        fprintf(f, "\n");
    }
    fclose(f);
    return 0;
}
