// Unbounded knapsack over w_k = L/k (k=2..n). Requires L/n >= 64 (word-shift forward DP).
// Outputs: best (max reachable < L), champion multiset, optional RLE dump of [L-span, L).
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static inline int getbit(const uint64_t* b, long long i) { return (b[i>>6] >> (i&63)) & 1ULL; }

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: knap L n [rle_out span]\n"); return 1; }
    long long L = atoll(argv[1]);
    int n = atoi(argv[2]);
    long long W = (L + 63) / 64;
    uint64_t *bits = (uint64_t*)calloc(W, 8);
    if (!bits) { fprintf(stderr, "alloc fail\n"); return 2; }
    bits[0] = 1ULL;
    for (int k = 2; k <= n; k++) {
        long long w = L / k;
        long long wq = w >> 6; int wr = (int)(w & 63);
        if (wr == 0) {
            for (long long i = wq; i < W; i++) bits[i] |= bits[i - wq];
        } else {
            bits[wq] |= bits[0] << wr;   // i == wq case guard for i-wq-1
            for (long long i = wq + 1; i < W; i++)
                bits[i] |= (bits[i - wq] << wr) | (bits[i - wq - 1] >> (64 - wr));
        }
        fprintf(stderr, "  item %d done\n", k);
    }
    long long best = -1;
    for (long long i = L - 1; i >= 0; i--) if (getbit(bits, i)) { best = i; break; }
    printf("n=%d L=%lld best=%lld gap=%lld\n", n, L, best, L - best);
    // champion reconstruction: repeatedly subtract any item leaving a reachable remainder
    long long v = best;
    printf("champion:");
    while (v > 0) {
        int done = 0;
        for (int k = 2; k <= n; k++) {
            long long w = L / k;
            if (v >= w && getbit(bits, v - w)) { printf(" %d", k); v -= w; done = 1; break; }
        }
        if (!done) { printf(" [STUCK at %lld]", v); break; }
    }
    printf("\n");
    if (argc >= 5) {
        long long span = atoll(argv[4]);
        long long lo = L - span; if (lo < 0) lo = 0;
        FILE* f = fopen(argv[3], "w");
        fprintf(f, "# lo=%lld L=%lld  runs of (value,count) starting at lo\n", lo, L);
        int cur = getbit(bits, lo); long long run = 0;
        fprintf(f, "start %d\n", cur);
        for (long long i = lo; i < L; i++) {
            int b = getbit(bits, i);
            if (b == cur) run++;
            else { fprintf(f, "%lld\n", run); cur = b; run = 1; }
        }
        fprintf(f, "%lld\n", run);
        fclose(f);
    }
    free(bits);
    return 0;
}
