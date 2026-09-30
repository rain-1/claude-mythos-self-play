// cloud.c — where can the centre of mass of a Ferris wheel land?
// Enumerate every hanging of the divisors on the wheel (n pinned at position 0,
// the other k-1 permuted by Heap's algorithm: one swap per step, O(1) update of the sum)
// and histogram the centre of mass  sum_j d_{pi(j)} zeta^j  on a G x G grid of [-R,R]^2.
// usage: cloud G R out.bin d_1 ... d_k      (d_k = n goes to position 0)
// With RANDOM=1 env var and SAMPLES=m: Monte-Carlo instead of exhaustive (large k).
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <string.h>

static inline uint64_t rng(uint64_t *s){ *s ^= *s << 13; *s ^= *s >> 7; *s ^= *s << 17; return *s; }

int main(int argc, char **argv){
    int G = atoi(argv[1]); double R = atof(argv[2]); const char *out = argv[3];
    int k = argc - 4; double d[256]; for (int i = 0; i < k; i++) d[i] = atof(argv[4 + i]);
    double cx[256], cy[256];
    for (int j = 0; j < k; j++){ cx[j] = cos(2*M_PI*j/k); cy[j] = sin(2*M_PI*j/k); }
    float *H = calloc((size_t)G*G, sizeof(float));
    double sc = G / (2*R);
    // position 0 holds d[k-1] (= n); positions 1..k-1 hold a permutation of d[0..k-2]
    int m = k - 1; double a[256]; for (int i = 0; i < m; i++) a[i] = d[i];
    double X = d[k-1]*cx[0], Y = d[k-1]*cy[0];
    for (int i = 0; i < m; i++){ X += a[i]*cx[i+1]; Y += a[i]*cy[i+1]; }
    uint64_t count = 0, outside = 0;
    #define HIT() do { int ix = (int)((X + R)*sc), iy = (int)((Y + R)*sc); \
        if (ix >= 0 && ix < G && iy >= 0 && iy < G) H[(size_t)iy*G + ix] += 1.f; else outside++; count++; } while(0)
    char *rs = getenv("RANDOM");
    if (rs && atoi(rs)){
        uint64_t S = strtoull(getenv("SAMPLES"), 0, 10), s = 88172645463325252ULL;
        for (uint64_t t = 0; t < S; t++){
            // random transposition walk: fast mixing enough per sample? do full shuffle every 64 steps
            if ((t & 63) == 0){
                for (int i = m-1; i > 0; i--){ int j = rng(&s) % (i+1); double tmp=a[i]; a[i]=a[j]; a[j]=tmp; }
                X = d[k-1]; Y = 0; for (int i = 0; i < m; i++){ X += a[i]*cx[i+1]; Y += a[i]*cy[i+1]; }
            } else {
                int i = rng(&s) % m, j = rng(&s) % m; if (i == j) j = (j + 1) % m;
                double da = a[i] - a[j];
                X += da*(cx[j+1] - cx[i+1]); Y += da*(cy[j+1] - cy[i+1]);
                double tmp = a[i]; a[i] = a[j]; a[j] = tmp;
            }
            HIT();
        }
    } else {
        int c[256]; memset(c, 0, sizeof c);
        HIT();
        int i = 0;
        while (i < m){
            if (c[i] < i){
                int j = (i % 2 == 0) ? 0 : c[i];
                double da = a[i] - a[j];        // swap a[i], a[j]
                X += da*(cx[j+1] - cx[i+1]); Y += da*(cy[j+1] - cy[i+1]);
                double tmp = a[i]; a[i] = a[j]; a[j] = tmp;
                HIT();
                c[i]++; i = 0;
            } else { c[i] = 0; i++; }
        }
    }
    FILE *f = fopen(out, "wb"); fwrite(H, sizeof(float), (size_t)G*G, f); fclose(f);
    fprintf(stderr, "count %llu outside %llu\n", (unsigned long long)count, (unsigned long long)outside);
    return 0;
}
