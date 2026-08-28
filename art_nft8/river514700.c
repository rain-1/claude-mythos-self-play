/* MO 514700: a_{k+1} = a_k + digitsum(a_k).  Follow the river from a
   given start to X, log every PRIME along it (deterministic 64-bit
   Miller-Rabin), plus lane statistics (a mod 9), step-count checkpoints,
   record prime gaps (in river steps).
   gcc -O3 -march=native river514700.c -o river -lm
   ./river START X TAG                                                     */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

typedef unsigned __int128 u128;

static uint64_t mulmod(uint64_t a, uint64_t b, uint64_t m){ return (uint64_t)((u128)a*b % m); }
static uint64_t powmod(uint64_t a, uint64_t e, uint64_t m){
    uint64_t r = 1; a %= m;
    while (e){ if (e&1) r = mulmod(r,a,m); a = mulmod(a,a,m); e >>= 1; }
    return r;
}
static int mr(uint64_t n, uint64_t a){
    if (a % n == 0) return 1;
    uint64_t d = n-1; int s = 0;
    while (!(d&1)){ d >>= 1; s++; }
    uint64_t x = powmod(a,d,n);
    if (x == 1 || x == n-1) return 1;
    for (int i = 1; i < s; i++){ x = mulmod(x,x,n); if (x == n-1) return 1; }
    return 0;
}
static int is_prime(uint64_t n){
    if (n < 2) return 0;
    for (uint64_t p = 2; p < 100; p++){
        if (p*p > n) return 1;
        if (n % p == 0) return n == p;
    }
    static const uint64_t B[] = {2,3,5,7,11,13,17,19,23,29,31,37};
    for (int i = 0; i < 12; i++) if (!mr(n, B[i])) return 0;
    return 1;
}
static inline int digitsum(uint64_t n){
    int s = 0; while (n){ s += n % 10; n /= 10; } return s;
}

int main(int argc, char **argv){
    uint64_t a  = argc > 1 ? strtoull(argv[1],0,10) : 1;
    uint64_t X  = argc > 2 ? strtoull(argv[2],0,10) : 100000000000ULL;
    const char *tag = argc > 3 ? argv[3] : "r1";
    char fn[128];
    snprintf(fn,128,"river_primes_%s.txt",tag);  FILE *fp = fopen(fn,"w");
    snprintf(fn,128,"river_chk_%s.txt",tag);     FILE *fc = fopen(fn,"w");
    uint64_t steps = 0, primes = 0, last_prime_step = 0, rec_gap = 0;
    uint64_t lane_steps[9] = {0}, lane_primes[9] = {0};
    uint64_t next_chk = 10;
    while (a < X){
        int m9 = (int)(a % 9);
        lane_steps[m9]++;
        /* fertile rivers are never divisible by 3; test odd only */
        if ((a & 1) && a % 3 != 0 && is_prime(a)){
            primes++;
            lane_primes[m9]++;
            uint64_t gap = steps - last_prime_step;
            if (gap > rec_gap && primes > 1){
                rec_gap = gap;
                fprintf(fp, "RECGAP %llu steps before prime #%llu\n",
                        (unsigned long long)gap, (unsigned long long)primes);
            }
            last_prime_step = steps;
            fprintf(fp, "P %llu step=%llu lane=%d\n",
                    (unsigned long long)a, (unsigned long long)steps, m9);
        } else if (a == 2 || a == 3){
            primes++; last_prime_step = steps;
            fprintf(fp, "P %llu step=%llu lane=%d\n",
                    (unsigned long long)a, (unsigned long long)steps, m9);
        }
        if (a >= next_chk){
            fprintf(fc, "%llu %llu %llu\n", (unsigned long long)a,
                    (unsigned long long)steps, (unsigned long long)primes);
            fflush(fc); fflush(fp);
            next_chk = next_chk + next_chk/8;   /* ~ log-spaced */
        }
        a += digitsum(a);
        steps++;
    }
    fprintf(fc, "%llu %llu %llu FINAL\n", (unsigned long long)a,
            (unsigned long long)steps, (unsigned long long)primes);
    fprintf(fc, "# lanes steps: ");
    for (int i = 0; i < 9; i++) fprintf(fc, "%d:%llu ", i, (unsigned long long)lane_steps[i]);
    fprintf(fc, "\n# lanes primes: ");
    for (int i = 0; i < 9; i++) fprintf(fc, "%d:%llu ", i, (unsigned long long)lane_primes[i]);
    fprintf(fc, "\n");
    fclose(fp); fclose(fc);
    fprintf(stderr, "DONE %s steps=%llu primes=%llu\n", tag,
            (unsigned long long)steps, (unsigned long long)primes);
    return 0;
}
