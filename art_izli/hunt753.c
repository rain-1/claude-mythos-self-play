/* MO 514753: search integer solutions of 2x^3+2y^3+2z^3 = xyz + 1.
   For every pair |x|,|y| <= B (x <= y), solve 2z^3 - (xy) z + (2x^3+2y^3-1) = 0
   for integer z.  By S3 symmetry this covers every solution whose two
   smallest-|.| coordinates are <= B.
   Pair sieve: solvability tables mod M1=819 (9*7*13) and M2=512.
   gcc -O3 -march=native -fopenmp hunt753.c -o hunt753 -lm ; ./hunt753 B     */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#ifdef _OPENMP
#include <omp.h>
#endif

#define M1 819
#define M2 512
static unsigned char T1[M1][M1];   /* T1[c][t]: exists z mod M1 with 2z^3-cz == t */
static unsigned char T2[M2][M2];

static void build(void){
    for (int c=0;c<M1;c++) for (int z=0; z<M1; z++){
        int v = (int)(((2LL*z*z*z - (long long)c*z) % M1 + M1) % M1);
        T1[c][v] = 1;
    }
    for (int c=0;c<M2;c++) for (int z=0; z<M2; z++){
        int v = (int)(((2LL*z*z*z - (long long)c*z) % M2 + M2) % M2);
        T2[c][v] = 1;
    }
}

typedef __int128 i128;
static inline int check_exact(long long x, long long y){
    /* solve 2z^3 - (xy) z + (2x^3+2y^3-1) = 0 over Z */
    long long p = x*y;
    i128 q = (i128)2*x*x*x + (i128)2*y*y*y - 1;
    /* real roots of 2t^3 - p t + q: try Newton from a few starts + rounding */
    double pd = (double)p, qd = (double)(long long)(q > (i128)9e18 ? 0 : (long long)q);
    if (q > (i128)9e18 || q < -(i128)9e18) qd = (double)x*x*x*2 + (double)y*y*y*2 - 1;
    int found = 0;
    double guesses[6];
    int ng = 0;
    /* roots bounded by ~ sqrt(|p|/2)+cbrt(|q|/2)+2 */
    double R = sqrt(fabs(pd)/2.0) + cbrt(fabs(qd)/2.0) + 2.0;
    for (int k=0;k<6;k++) guesses[ng++] = -R + 2.0*R*k/5.0;
    for (int g=0; g<ng; g++){
        double t = guesses[g];
        for (int it=0; it<80; it++){
            double f = 2*t*t*t - pd*t + qd;
            double df = 6*t*t - pd;
            if (fabs(df) < 1e-9) { t += 1.0; continue; }
            double step = f/df;
            t -= step;
            if (fabs(step) < 1e-7) break;
        }
        long long z0 = llround(t);
        for (long long z = z0-2; z <= z0+2; z++){
            i128 v = (i128)2*z*z*z - (i128)p*z + q;
            if (v == 0){
                printf("SOLUTION x=%lld y=%lld z=%lld\n", x, y, z);
                fflush(stdout);
                found = 1;
            }
        }
    }
    return found;
}

int main(int argc, char **argv){
    long long B = argc>1 ? atoll(argv[1]) : 100000;
    build();
    long long hits = 0, survivors = 0;
    #pragma omp parallel for schedule(dynamic, 64) reduction(+:hits,survivors)
    for (long long x = -B; x <= B; x++){
        int xm1 = (int)((x % M1 + M1) % M1);
        int xm2 = (int)(x & (M2-1));
        int k1 = (int)(((1 - 2LL*xm1*xm1*xm1) % M1 + 5LL*M1) % M1);
        int k2 = (int)((1 - 2LL*xm2*xm2*xm2) & (M2-1));
        int c1 = (int)((xm1 * (long long)((x % M1 + M1) % M1)) % M1); /* placeholder */
        for (long long y = x; y <= B; y++){
            int ym1 = (int)((y % M1 + M1) % M1);
            int ym2 = (int)(y & (M2-1));
            int cc1 = (int)((long long)xm1*ym1 % M1);
            int tt1 = (int)(((k1 - 2LL*ym1*ym1*ym1) % M1 + 5LL*M1) % M1);
            if (!T1[cc1][tt1]) continue;
            int cc2 = (xm2*ym2) & (M2-1);
            int tt2 = (k2 - 2*ym2*ym2*ym2) & (M2-1);
            if (!T2[cc2][tt2]) continue;
            survivors++;
            if (check_exact(x, y)) hits++;
        }
    }
    (void)c1;
    printf("DONE B=%lld survivors=%lld solutions=%lld\n", B, survivors, hits);
    return 0;
}
