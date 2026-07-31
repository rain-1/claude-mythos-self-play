/* liouville.c — segmented sieve of the Liouville function lambda(n) = (-1)^Omega(n)
 * for 1 <= n <= N (N = 2^30 by default).
 *
 * Output: blocks.i16 — int16 per-block sums of lambda over blocks of BLK=4096,
 * i.e. block b holds sum_{n=b*BLK+1}^{(b+1)*BLK} lambda(n)  (n=0 skipped).
 * The Polya conjecture claims L(x) = sum_{n<=x} lambda(n) <= 0 for x >= 2;
 * the first counterexample is expected at x = 906,150,257 (Tanaka 1980).
 *
 * Method per segment: 64-bit residual array init n; for each sieve prime
 * p <= sqrt(N): divide out all powers of p from multiples, counting parity.
 * Leftover residual > 1 is a single large prime factor -> one more flip.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <omp.h>

#define BLK 4096

int main(int argc, char** argv) {
    uint64_t N = (argc > 1) ? strtoull(argv[1], 0, 10) : (1ULL << 30);
    uint64_t SEG = 1ULL << 22;           /* segment length */
    uint32_t rt = (uint32_t)sqrt((double)N) + 1;

    /* primes up to sqrt(N) by simple sieve */
    uint8_t* comp = calloc(rt + 1, 1);
    uint32_t* primes = malloc(sizeof(uint32_t) * (rt / 8 + 64));
    uint32_t np = 0;
    for (uint32_t i = 2; i <= rt; i++) {
        if (!comp[i]) {
            primes[np++] = i;
            for (uint64_t j = (uint64_t)i * i; j <= rt; j += i) comp[j] = 1;
        }
    }
    free(comp);
    fprintf(stderr, "N=%llu, %u sieve primes <= %u\n",
            (unsigned long long)N, np, rt);

    uint64_t nseg = (N + SEG - 1) / SEG;
    uint64_t nblk = (N + BLK - 1) / BLK;
    int16_t* blocks = malloc(sizeof(int16_t) * nblk);
    memset(blocks, 0, sizeof(int16_t) * nblk);

#pragma omp parallel
    {
        uint64_t* res = malloc(sizeof(uint64_t) * SEG);
        uint8_t* par = malloc(SEG);
#pragma omp for schedule(dynamic)
        for (uint64_t s = 0; s < nseg; s++) {
            uint64_t lo = s * SEG + 1;              /* first n in segment */
            uint64_t hi = lo + SEG - 1; if (hi > N) hi = N;
            uint64_t len = hi - lo + 1;
            for (uint64_t i = 0; i < len; i++) { res[i] = lo + i; par[i] = 0; }
            for (uint32_t k = 0; k < np; k++) {
                uint64_t p = primes[k];
                if (p * p > hi) break;
                uint64_t start = ((lo + p - 1) / p) * p;
                for (uint64_t m = start; m <= hi; m += p) {
                    uint64_t i = m - lo;
                    do { res[i] /= p; par[i] ^= 1; } while (res[i] % p == 0);
                }
            }
            for (uint64_t i = 0; i < len; i++) {
                uint64_t n = lo + i;
                if (n < 2) continue;                 /* lambda(1)=1 counted separately below */
                int8_t lam = ((par[i] ^ (res[i] > 1)) & 1) ? -1 : 1;
                blocks[(n - 1) / BLK] += lam;        /* block by n-1 so block 0 = n in [1,BLK] */
            }
        }
        free(res); free(par);
    }
    blocks[0] += 1;  /* lambda(1) = +1 */

    FILE* f = fopen("blocks.i16", "wb");
    fwrite(blocks, sizeof(int16_t), nblk, f);
    fclose(f);

    /* quick scan: cumulative at block boundaries, global min/max */
    int64_t cum = 0, mn = 0, mx = -1000000;
    uint64_t argmx = 0;
    for (uint64_t b = 0; b < nblk; b++) {
        cum += blocks[b];
        if (cum < mn) mn = cum;
        if (cum > mx) { mx = cum; argmx = b; }
    }
    fprintf(stderr, "done. blocks=%llu  L(N)=%lld  min block-boundary L=%lld  "
            "max block-boundary L=%lld at block %llu (n~%llu)\n",
            (unsigned long long)nblk, (long long)cum, (long long)mn,
            (long long)mx, (unsigned long long)argmx,
            (unsigned long long)(argmx + 1) * BLK);
    return 0;
}
