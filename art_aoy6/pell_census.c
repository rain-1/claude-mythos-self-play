/* pell_census.c — census of the continued fraction of sqrt(d) for all
 * squarefree nonsquare d <= N.
 *
 * For each d: period P of the CF of sqrt(d), regulator R = ln(eps) where
 * eps = x + y*sqrt(d) is the fundamental solution of x^2 - d y^2 = +-1
 * (fundamental unit of Z[sqrt d]), computed as the sum of logs of the
 * complete quotients over one period:
 *      R = sum_{i=1..P} ln( (m_i + sqrt d)/q_i ).
 * Norm of eps is (-1)^P: negative Pell x^2 - d y^2 = -1 is solvable
 * iff P is odd. (Both facts verified externally against exact bigint
 * convergents for d <= 2000 — see verify_pell.py.)
 *
 * Flags per d: bit0 squarefree, bit1 eligible (no prime factor == 3 mod 4),
 * bit2 processed (squarefree nonsquare).
 *
 * Tripwire: the loop asserts the algebraic invariant q | d - m^2 at every
 * step, and that the period closes (q returns to 1) within CAP steps.
 *
 * Output: flags.u8 [N+1], period.u32 [N+1], reg.f32 [N+1]
 * Usage: ./pell_census N outdir nthreads
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <omp.h>

static void die(const char *msg){ fprintf(stderr,"FATAL: %s\n",msg); exit(1); }

int main(int argc, char **argv){
    if(argc<4) die("usage: pell_census N outdir nthreads");
    int64_t N = atoll(argv[1]);
    const char *outdir = argv[2];
    int nth = atoi(argv[3]);
    omp_set_num_threads(nth);

    uint8_t *flags = calloc(N+1,1);
    uint32_t *period = calloc(N+1,sizeof(uint32_t));
    float *reg = calloc(N+1,sizeof(float));
    if(!flags||!period||!reg) die("alloc");

    /* --- sieve: squarefree + smallest-prime 3mod4 marking --- */
    /* prime sieve to N (bitset) */
    int64_t nb = N/2+1; /* odd numbers only */
    uint8_t *comp = calloc((nb>>3)+2,1); /* comp[i] -> 2i+1 composite */
    for(int64_t i=1; (2*i+1)*(2*i+1)<=N; i++){
        if(!(comp[i>>3]>>(i&7)&1)){
            int64_t p=2*i+1;
            for(int64_t j=(p*p-1)/2; j<nb; j+=p) comp[j>>3]|=1<<(j&7);
        }
    }
    /* squarefree marking: multiples of p^2 for all primes p; and of 4 */
    for(int64_t d=4; d<=N; d+=4) flags[d]|=1; /* temp: bit0 = NOT squarefree */
    for(int64_t i=1; (2*i+1)*(2*i+1)<=N; i++){
        if(!(comp[i>>3]>>(i&7)&1)){
            int64_t p=2*i+1, pp=p*p;
            for(int64_t j=pp;j<=N;j+=pp) flags[j]|=1;
        }
    }
    /* eligible marking: bit1 = HAS a prime factor 3 mod 4 (temp) */
    for(int64_t i=1; 2*i+1<=N; i++){
        if(!(comp[i>>3]>>(i&7)&1)){
            int64_t p=2*i+1;
            if((p&3)==3) for(int64_t j=p;j<=N;j+=p) flags[j]|=2;
        }
    }
    free(comp);
    /* invert temps: bit0 squarefree, bit1 eligible */
    for(int64_t d=1;d<=N;d++){
        uint8_t f=flags[d];
        flags[d] = (uint8_t)(((f&1)?0:1) | ((f&2)?0:2));
    }

    fprintf(stderr,"sieves done\n");

    /* --- CF census --- */
    const int64_t CAP = 1000000;
    int64_t nproc_total=0; double t0=omp_get_wtime();
    int abort_flag=0;
#pragma omp parallel for schedule(dynamic,4096) reduction(+:nproc_total)
    for(int64_t d=2; d<=N; d++){
        if(abort_flag) continue;
        if(!(flags[d]&1)) continue;
        int64_t a0 = (int64_t)sqrtl((long double)d);
        while(a0*a0>d) a0--;
        while((a0+1)*(a0+1)<=d) a0++;
        if(a0*a0==d) continue; /* square (only d=1 among squarefree, but safe) */
        double sq = sqrt((double)d);
        int64_t m=0,q=1,a=a0;
        double R=0.0;
        int64_t P=0;
        for(;;){
            m = a*q - m;
            int64_t num = d - m*m;
            if(num % q){
#pragma omp critical
                { fprintf(stderr,"TRIPWIRE q|d-m^2 failed d=%lld\n",(long long)d); abort_flag=1; }
                break;
            }
            q = num / q;
            a = (a0 + m)/q;
            P++;
            R += log((m + sq)/q);
            if(q==1) break;
            if(P>=CAP){
#pragma omp critical
                { fprintf(stderr,"TRIPWIRE period cap d=%lld\n",(long long)d); abort_flag=1; }
                break;
            }
        }
        period[d]=(uint32_t)P;
        reg[d]=(float)R;
        flags[d]|=4;
        nproc_total++;
    }
    if(abort_flag) die("tripwire fired");
    fprintf(stderr,"census done: %lld d processed in %.1fs\n",
            (long long)nproc_total, omp_get_wtime()-t0);

    char path[512]; FILE *f;
    snprintf(path,512,"%s/flags.u8",outdir); f=fopen(path,"wb"); fwrite(flags,1,N+1,f); fclose(f);
    snprintf(path,512,"%s/period.u32",outdir); f=fopen(path,"wb"); fwrite(period,4,N+1,f); fclose(f);
    snprintf(path,512,"%s/reg.f32",outdir); f=fopen(path,"wb"); fwrite(reg,4,N+1,f); fclose(f);
    fprintf(stderr,"written to %s\n",outdir);
    return 0;
}
