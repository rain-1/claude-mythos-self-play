/* Atlas piece 40: deep census of S = { n : v_p(n) even for all p = 3,5 mod 8 }
   (absolute norms of Z[sqrt2]) via segmented FULL-FACTORIZATION sieve.
   Membership needs v_p parity for every bad prime; per segment we divide out all
   primes <= sqrt(X) from rem[], counting parities; leftover rem is 1 or a single
   prime > sqrt(X) (a p*q leftover with p,q > sqrt(X) would exceed X) -> test mod 8.
   Then a serial pass scans equal-gap runs of CONSECUTIVE members, all gaps,
   maximal-run per-gap counts for l>=3, first-occurrence table, and records.
   gcc -O3 -march=native -fopenmp sqrt2_deep.c -o sqrt2_deep
   ./sqrt2_deep X_MAX  (bitmap of X/8 bytes allocated; 3.2e10 -> 4 GB)          */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <omp.h>

#define SEGLOG 22
#define SEG (1ULL<<SEGLOG)          /* 4M per segment */

static inline int bad_mod8(uint64_t p){ uint64_t r = p & 7; return r==3 || r==5; }

int main(int argc, char** argv){
    uint64_t X = argc>1 ? strtoull(argv[1],0,10) : 32000000000ULL;
    uint32_t sq = (uint32_t)sqrt((double)X);
    while ((uint64_t)(sq+1)*(sq+1) <= X) sq++;
    /* primes to sq */
    uint8_t* isp = malloc((size_t)sq+1); memset(isp,1,(size_t)sq+1); isp[0]=isp[1]=0;
    for (uint32_t i=2;(uint64_t)i*i<=sq;i++) if(isp[i]) for(uint64_t j=(uint64_t)i*i;j<=sq;j+=i) isp[j]=0;
    uint32_t np=0; for(uint32_t i=2;i<=sq;i++) np+=isp[i];
    uint32_t* primes = malloc(4ULL*np); uint32_t k=0;
    for(uint32_t i=2;i<=sq;i++) if(isp[i]) primes[k++]=i;
    free(isp);
    fprintf(stderr,"X=%llu sqrt=%u primes=%u\n",(unsigned long long)X,sq,np);

    size_t nbytes = X/8 + 2;
    uint8_t* B = malloc(nbytes);              /* global membership bitmap */
    if(!B){ fprintf(stderr,"OOM bitmap\n"); return 1; }
    memset(B,0,nbytes);

    uint64_t nseg = (X + SEG) / SEG;
    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        uint64_t* rem = malloc(8*SEG);
        uint8_t*  ex  = malloc(SEG);          /* excluded flag */
        #pragma omp for schedule(dynamic,1)
        for (uint64_t si=0; si<nseg; si++){
            uint64_t lo = si*SEG;             /* segment covers [lo, hi) */
            uint64_t hi = lo+SEG; if (hi > X+1) hi = X+1;
            uint64_t len = hi-lo;
            for (uint64_t i=0;i<len;i++){ rem[i]=lo+i; ex[i]=0; }
            if (lo==0){ ex[0]=1; if(len>1){rem[1]=1;} }   /* n=0 excluded */
            for (uint32_t pi=0; pi<np; pi++){
                uint64_t p = primes[pi];
                if (p*p >= hi && p >= hi) break;
                int bad = bad_mod8(p);
                uint64_t st = ((lo+p-1)/p)*p; if (st==0) st = p;
                for (uint64_t j=st; j<hi; j+=p){
                    uint64_t i = j-lo;
                    uint64_t r = rem[i]; int v=0;
                    while (r % p == 0){ r /= p; v++; }
                    rem[i]=r;
                    if (bad && (v&1)) ex[i]=1;
                }
            }
            for (uint64_t i=0;i<len;i++){
                if (!ex[i]){
                    uint64_t r = rem[i];
                    if (r>1 && bad_mod8(r)) continue;   /* lone big bad prime */
                    uint64_t n=lo+i;
                    B[n>>3] |= (uint8_t)(1u<<(n&7));
                }
            }
            if ((si & 127)==0){
                #pragma omp critical
                fprintf(stderr,"seg %llu/%llu  %.0fs\n",(unsigned long long)si,
                        (unsigned long long)nseg, omp_get_wtime()-t0);
            }
        }
        free(rem); free(ex);
    }
    fprintf(stderr,"sieve done %.0fs\n",omp_get_wtime()-t0);

    /* serial run scan */
    enum { GMAX = 256, LMAX = 12 };
    static uint64_t runcount[LMAX+1][GMAX];   /* maximal runs of exactly l terms, gap g */
    static uint64_t first_n[LMAX+1][GMAX];    /* first (start) occurrence of an l-run (incl. as part of longer) */
    memset(runcount,0,sizeof runcount); memset(first_n,0,sizeof first_n);
    uint64_t cnt=0, prev=0, gap=0, runlen=1, ck=1000000;
    FILE* rec = fopen("deep_records.txt","w");
    FILE* dens = fopen("deep_density.txt","w");
    FILE* fr14 = fopen("deep_g14_17.txt","w");
    int bestlen=0;
    uint64_t* W = (uint64_t*)B;
    uint64_t nwords = nbytes/8;
    for (uint64_t wi=0; wi<nwords; wi++){
        uint64_t w = W[wi];
        while (w){
        uint64_t n = wi*64 + (uint64_t)__builtin_ctzll(w);
        w &= w-1;
        if (n==0 || n>X) continue;
        cnt++;
        if (prev){
            uint64_t g = n-prev;
            if (g==gap) runlen++;
            else {
                /* close maximal run of runlen terms, gap 'gap' */
                if (runlen>=3 && gap<GMAX){
                    int l = runlen>LMAX?LMAX:(int)runlen;
                    runcount[l][gap]++;
                }
                runlen=2; gap=g;
            }
            if (runlen>=3 && gap<GMAX && !first_n[runlen>LMAX?LMAX:runlen][gap]){
                int l = runlen>LMAX?LMAX:(int)runlen;
                first_n[l][gap] = n-(runlen-1)*gap;
                if (l>=5 && (gap==14||gap==17)){
                    fprintf(fr14,"FIRST l=%d g=%llu start=%llu\n",l,(unsigned long long)gap,
                            (unsigned long long)first_n[l][gap]); fflush(fr14);
                }
            }
            if ((int)runlen > bestlen){
                bestlen=runlen;
                fprintf(rec,"RECORD l=%d gap=%llu start=%llu\n",(int)runlen,
                    (unsigned long long)gap,(unsigned long long)(n-(runlen-1)*gap));
                fflush(rec);
            }
            if (runlen>=6 && gap<GMAX){
                fprintf(rec,"L6+! l=%d gap=%llu start=%llu\n",(int)runlen,
                    (unsigned long long)gap,(unsigned long long)(n-(runlen-1)*gap));
                fflush(rec);
            }
        }
        prev=n;
        if (cnt==ck){ fprintf(dens,"%llu %llu\n",(unsigned long long)n,(unsigned long long)cnt); ck*=2; }
        }
    }
    if (runlen>=3 && gap<GMAX){ int l=runlen>LMAX?LMAX:(int)runlen; runcount[l][gap]++; }
    printf("X=%llu |S|=%llu\n",(unsigned long long)X,(unsigned long long)cnt);
    /* checkpoint counts for certificate vs piece 39 */
    FILE* rg = fopen("deep_rungap.txt","w");
    for (int l=3;l<=LMAX;l++) for (int g=1;g<GMAX;g++)
        if (runcount[l][g] || first_n[l][g])
            fprintf(rg,"l=%d g=%d maximal_runs=%llu first_start=%llu\n",l,g,
                (unsigned long long)runcount[l][g],(unsigned long long)first_n[l][g]);
    fclose(rg); fclose(rec); fclose(dens); fclose(fr14);
    fprintf(stderr,"all done %.0fs\n",omp_get_wtime()-t0);
    return 0;
}
