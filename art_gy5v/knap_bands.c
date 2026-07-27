// Band-count mode: run DP, then count reachable values per fine log10-distance bin.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

static inline int getbit(const uint64_t* b, long long i) { return (b[i>>6] >> (i&63)) & 1ULL; }

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: knap_bands L n out.txt [bins_per_decade=28]\n"); return 1; }
    long long L = atoll(argv[1]);
    int n = atoi(argv[2]);
    int bpd = argc > 4 ? atoi(argv[4]) : 28;
    long long W = (L + 63) / 64;
    uint64_t *bits = (uint64_t*)calloc(W, 8);
    if (!bits) { fprintf(stderr, "alloc fail\n"); return 2; }
    bits[0] = 1ULL;
    for (int k = 2; k <= n; k++) {
        long long w = L / k;
        long long wq = w >> 6; int wr = (int)(w & 63);
        if (wr == 0) { for (long long i = wq; i < W; i++) bits[i] |= bits[i - wq]; }
        else {
            bits[wq] |= bits[0] << wr;
            for (long long i = wq + 1; i < W; i++)
                bits[i] |= (bits[i - wq] << wr) | (bits[i - wq - 1] >> (64 - wr));
        }
    }
    int nb = (int)(log10((double)L)*bpd) + 2;
    long long *cnt = calloc(nb, 8), *tot = calloc(nb, 8);
    // precompute bin thresholds: bin j covers d in [10^(j/bpd), 10^((j+1)/bpd))
    long long *edge = malloc((nb+1)*8);
    for (int j = 0; j <= nb; j++) {
        double e = pow(10.0, (double)j/bpd);
        edge[j] = (long long)e;
    }
    int j = 0;
    for (long long d = 1; d < L; d++) {
        while (j+1 <= nb && d >= edge[j+1]) j++;
        if (j >= nb) break;
        tot[j]++;
        if (getbit(bits, L - d)) cnt[j]++;
    }
    FILE* f = fopen(argv[3], "w");
    fprintf(f, "# n=%d L=%lld bpd=%d\n", n, L, bpd);
    for (int q = 0; q < nb; q++) fprintf(f, "%d %lld %lld\n", q, cnt[q], tot[q]);
    fclose(f);
    return 0;
}
