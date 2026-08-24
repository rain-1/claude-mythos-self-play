/* MO 514605: Collatz total-stopping-time record census, both conventions.
   Convention F (A006877 "delay"): n -> 3n+1 (odd), n -> n/2 (even).
   Convention S (poster's shortcut): n -> (3n+1)/2 (odd), n -> n/2 (even).
   If a trajectory makes o odd-steps and its shortcut length is s, then
   delay = s + o (each odd shortcut step hides one halving).

   Memo tables below M=2^30: Tf[i] = delay(i), Od[i] = odd steps of i.
   (Ts = Tf - Od.)  Build in blocks (all of [0,B) done before [B,2B) starts;
   within a block, iterate until the value drops below the block base).
   Scan phase [M,N): iterate (u64 with overflow check -> u128) until < M.

   Per chunk of 2^26, log block-local left-to-right maxima for BOTH
   conventions; a python merge produces the global record lists.

   gcc -O3 -march=native -fopenmp collatz.c -o collatz
   ./collatz N outprefix                                                    */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>

#define MLOG 30
#define M (1ULL<<MLOG)
static uint16_t *Tf, *Od;

/* iterate x (shortcut) until x < limit; add steps to *s (shortcut) and *o. */
static inline uint64_t descend(uint64_t x, uint64_t limit, uint32_t *s, uint32_t *o){
    uint32_t ss=*s, oo=*o;
    while (x >= limit){
        if (x & 1){
            if (x > 6148914691236517203ULL){           /* 3x+1 would pass 2^64 */
                __uint128_t y = x;
                while (y >= limit){
                    if (y & 1){ y = (3*y+1)>>1; ss++; oo++; }
                    else { y >>= 1; ss++; }
                }
                x = (uint64_t)y; break;
            }
            x = (3*x+1)>>1; ss++; oo++;
        } else { x >>= 1; ss++; }
    }
    *s=ss; *o=oo; return x;
}

int main(int argc, char **argv){
    uint64_t N = argc>1 ? strtoull(argv[1],0,10) : 100000000000ULL;
    const char *pref = argc>2 ? argv[2] : "collatz";
    uint64_t N0 = argc>3 ? strtoull(argv[3],0,10) : 0;   /* scan resume point */
    char fn[256];
    snprintf(fn,256,"%s_cand.txt",pref);
    FILE *fc = fopen(fn,"w");
    snprintf(fn,256,"%s_prog.txt",pref);
    FILE *fp = fopen(fn,"w");

    Tf = malloc(2*M); Od = malloc(2*M);
    if (!Tf || !Od){ fprintf(stderr,"alloc fail\n"); return 1; }
    Tf[0]=0; Od[0]=0; Tf[1]=0; Od[1]=0;
    double t0 = omp_get_wtime();

    /* ---- build memo tables in blocks ---- */
    const uint64_t B = 1ULL<<24;
    for (uint64_t base=2; base<M; base = (base<B?B:base+B)){
        uint64_t hi = (base<B? B : base+B); if (hi>M) hi=M;
        #pragma omp parallel for schedule(dynamic, 65536)
        for (uint64_t n=base; n<hi; n++){
            uint32_t s=0,o=0;
            uint64_t x = descend(n, base, &s, &o);   /* below base => memoised */
            Tf[n] = (uint16_t)(s + o + Tf[x] );
            Od[n] = (uint16_t)(o + Od[x]);
        }
    }
    fprintf(fp,"# tables built %.1fs\n", omp_get_wtime()-t0); fflush(fp);

    /* ---- records below M: sequential scan of the tables ---- */
    if (N0 == 0) {
        uint32_t bf=0, bs=0;
        for (uint64_t n=1; n<M && n<=N; n++){
            uint32_t tf = Tf[n], ts = Tf[n]-Od[n];
            if (tf > bf){ bf=tf; fprintf(fc,"F %llu %u\n",(unsigned long long)n,tf); }
            if (ts > bs){ bs=ts; fprintf(fc,"S %llu %u\n",(unsigned long long)n,ts); }
        }
        fflush(fc);
    }
    fprintf(fp,"# low records done %.1fs\n", omp_get_wtime()-t0); fflush(fp);

    /* ---- scan phase [M,N) in ordered chunks; per-chunk local maxima ---- */
    const uint64_t C = 1ULL<<26;
    uint64_t S0 = N0 > M ? N0 : M;
    uint64_t nch = (N > S0) ? (N - S0 + C - 1)/C : 0;
    #pragma omp parallel
    {
        char line[128]; (void)line;
        #pragma omp for ordered schedule(dynamic,1)
        for (uint64_t ci=0; ci<nch; ci++){
            uint64_t lo = S0 + ci*C, hi = lo + C; if (hi>N) hi=N;
            /* local left-to-right maxima (seeded 0 => superset of global) */
            enum {CAP=4096};
            uint64_t nf[CAP], ns[CAP]; uint32_t vf[CAP], vs[CAP];
            int kf=0, ks=0; uint32_t bf=0, bs=0;
            for (uint64_t n=lo; n<hi; n++){
                uint32_t s=0,o=0;
                uint64_t x = descend(n, M, &s, &o);
                uint32_t tf = s + o + Tf[x];
                uint32_t ts = s + Tf[x] - Od[x];
                if (tf > bf && kf<CAP){ bf=tf; nf[kf]=n; vf[kf]=tf; kf++; }
                if (ts > bs && ks<CAP){ bs=ts; ns[ks]=n; vs[ks]=ts; ks++; }
            }
            #pragma omp ordered
            {
                for (int i=0;i<kf;i++) fprintf(fc,"F %llu %u\n",(unsigned long long)nf[i],vf[i]);
                for (int i=0;i<ks;i++) fprintf(fc,"S %llu %u\n",(unsigned long long)ns[i],vs[i]);
                fflush(fc);
                if ((ci & 63)==0){
                    double el = omp_get_wtime()-t0;
                    fprintf(fp,"chunk %llu/%llu %.0fs ETA %.0f min\n",
                        (unsigned long long)ci,(unsigned long long)nch, el,
                        el*((double)nch/(ci+1)-1.0)/60.0);
                    fflush(fp);
                }
            }
        }
    }
    fprintf(fp,"# ALLDONE N=%llu %.1fs\n",(unsigned long long)N, omp_get_wtime()-t0);
    fclose(fc); fclose(fp);
    return 0;
}
