/* Gaussian prime moats: sieve Gaussian primes with |z| <= R, then BFS the
   step-ladder of reachability from 1+i: for each squared step bound k in
   the ladder, the set of primes reachable from 1+i by hops of squared
   length <= k. Records, per prime, the MINIMAL ladder k that reaches it
   (discovery class), plus per-k component size / farthest point / whether
   the component touches the shore |z| ~ R (censored).

   Symmetry: the Gaussian primes are symmetric under conjugation and units,
   so full-plane reachability == quadrant reachability with reflecting
   steps at the axes (folding a plane path never lengthens a hop).
   We BFS on the closed quadrant a,b >= 0.

   Gaussian prime (a,b), a,b>0: a^2+b^2 prime. On axes: |a| prime and
   |a| == 3 (mod 4).

   Output:
     moat_summary.txt   one line per k: k size farthest_r2 fa fb censored
     moat_bins.bin      NK x B x B uint32 counts of primes by discovery
                        class, binned to B x B over [0,R]^2 (B=2048)
   gcc -O3 -march=native moats.c -o moats -lm ; ./moats R              */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

static const int KLADDER[] = {2, 4, 8, 16, 26, 36};
enum { NK = 6, B = 2048 };

static uint8_t *psieve;                 /* odd-number prime bitset to N */
static inline int isprime(uint64_t n){
    if (n < 2) return 0;
    if (n == 2) return 1;
    if (!(n & 1)) return 0;
    return (psieve[n >> 4] >> ((n >> 1) & 7)) & 1;
}

int main(int argc, char **argv){
    int R = argc > 1 ? atoi(argv[1]) : 25000;
    uint64_t N = (uint64_t)R * R;       /* max norm on the quadrant grid */
    /* ---- odd sieve to N ---- */
    size_t sb = N / 16 + 1;
    psieve = malloc(sb);
    memset(psieve, 0xFF, sb);
    psieve[0] &= ~1;                     /* 1 is not prime */
    for (uint64_t i = 3; i * i <= N; i += 2)
        if ((psieve[i >> 4] >> ((i >> 1) & 7)) & 1)
            for (uint64_t j = i * i; j <= N; j += 2 * i)
                psieve[j >> 4] &= ~(1u << ((j >> 1) & 7));
    fprintf(stderr, "sieve to %llu done\n", (unsigned long long)N);

    /* ---- Gaussian prime bitmap on quadrant grid (R+1)^2 ---- */
    int W = R + 1;
    size_t gb = ((size_t)W * W + 7) / 8;
    uint8_t *gp = calloc(gb, 1);
    uint8_t *seen = calloc(gb, 1);
    #define GIDX(a,b) ((size_t)(b) * W + (a))
    #define GET(arr,i) ((arr[(i) >> 3] >> ((i) & 7)) & 1)
    #define SET(arr,i) (arr[(i) >> 3] |= 1u << ((i) & 7))
    long nprimes = 0;
    for (int b = 0; b <= R; b++){
        uint64_t bb = (uint64_t)b * b;
        for (int a = 0; a <= R; a++){
            uint64_t n2 = (uint64_t)a * a + bb;
            if (n2 > N) break;
            int is;
            if (a == 0)      is = isprime(b) && (b & 3) == 3;
            else if (b == 0) is = isprime(a) && (a & 3) == 3;
            else             is = isprime(n2);
            if (is){ SET(gp, GIDX(a,b)); nprimes++; }
        }
    }
    fprintf(stderr, "gaussian primes in quadrant: %ld\n", nprimes);

    /* ---- discovery-class array (one byte per grid cell; 255 = unreached) */
    uint8_t *cls = malloc((size_t)W * W);
    memset(cls, 255, (size_t)W * W);

    /* ---- BFS ladder ---- */
    int (*queue)[2] = malloc(sizeof(int[2]) * 70000000);
    long qh = 0, qt = 0;
    FILE *fs = fopen("moat_summary.txt", "w");
    /* seed: 1+i */
    SET(seen, GIDX(1,1)); cls[GIDX(1,1)] = 0;
    queue[qt][0] = 1; queue[qt][1] = 1; qt++;
    long shore2 = (long)(R - 6) * (R - 6);
    for (int ki = 0; ki < NK; ki++){
        int K = KLADDER[ki], md = (int)floor(sqrt((double)K));
        /* offsets with 0 < dx^2+dy^2 <= K (dx,dy can be negative) */
        int offs[200][2], noff = 0;
        for (int dx = -md; dx <= md; dx++)
            for (int dy = -md; dy <= md; dy++)
                if ((dx || dy) && dx * dx + dy * dy <= K){
                    offs[noff][0] = dx; offs[noff][1] = dy; noff++;
                }
        /* frontier = everything reached so far: rescan queue from 0 */
        qh = 0;
        long size = 0; long far2 = 0; int fa = 1, fb = 1; int censored = 0;
        /* count current reached set */
        for (long t = 0; t < qt; t++){
            long a = queue[t][0], b = queue[t][1];
            long r2 = a * a + b * b;
            size++;
            if (r2 > far2){ far2 = r2; fa = (int)a; fb = (int)b; }
            if (r2 >= shore2) censored = 1;
        }
        while (qh < qt){
            int a = queue[qh][0], b = queue[qh][1]; qh++;
            for (int o = 0; o < noff; o++){
                int na = a + offs[o][0], nb = b + offs[o][1];
                if (na < 0) na = -na;            /* reflect at axes */
                if (nb < 0) nb = -nb;
                if (na > R || nb > R) continue;
                size_t gi = GIDX(na, nb);
                if (!GET(gp, gi) || GET(seen, gi)) continue;
                SET(seen, gi);
                cls[gi] = (uint8_t)ki;
                queue[qt][0] = na; queue[qt][1] = nb; qt++;
                long r2 = (long)na * na + (long)nb * nb;
                size++;
                if (r2 > far2){ far2 = r2; fa = na; fb = nb; }
                if (r2 >= shore2) censored = 1;
            }
        }
        fprintf(fs, "k=%d size=%ld far2=%ld far=(%d,%d) censored=%d\n",
                K, size, far2, fa, fb, censored);
        fflush(fs);
        fprintf(stderr, "k=%d size=%ld far=%.1f censored=%d\n",
                K, size, sqrt((double)far2), censored);
    }
    fclose(fs);

    /* ---- bins: NK+1 classes (ladder classes + unreached primes) ---- */
    uint32_t *bins = calloc((size_t)(NK + 1) * B * B, 4);
    double sc = (double)B / W;
    for (int b = 0; b <= R; b++)
        for (int a = 0; a <= R; a++){
            size_t gi = GIDX(a,b);
            if (!GET(gp, gi)) continue;
            int c = cls[gi]; if (c == 255) c = NK;
            int xb = (int)(a * sc), yb = (int)(b * sc);
            if (xb >= B) xb = B - 1;
            if (yb >= B) yb = B - 1;
            bins[((size_t)c * B + yb) * B + xb]++;
        }
    /* exact dump of the core (r <= 600) for artifact-free center render */
    FILE *fc = fopen("moat_core.txt", "w");
    for (int b = 0; b <= 600; b++)
        for (int a = 0; a <= 600; a++){
            if ((long)a*a + (long)b*b > 360000L) continue;
            size_t gi = GIDX(a,b);
            if (!GET(gp, gi)) continue;
            int c = cls[gi]; if (c == 255) c = NK;
            fprintf(fc, "%d %d %d\n", a, b, c);
        }
    fclose(fc);
    FILE *fb2 = fopen("moat_bins.bin", "wb");
    fwrite(bins, 4, (size_t)(NK + 1) * B * B, fb2);
    fclose(fb2);
    fprintf(stderr, "bins written\n");
    return 0;
}
