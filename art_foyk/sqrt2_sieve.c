/* Atlas piece 39: S = { n <= X : v_p(n) even for all primes p = 3,5 mod 8 }  (norms of Z[sqrt2], up to sign)
   Bit sieve + equal-gap consecutive-run records.  gcc -O3 -fopenmp sqrt2_sieve.c -o sqrt2_sieve */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <omp.h>

static inline int is_bad_mod8(uint64_t p){ uint64_t r = p & 7; return r==3 || r==5; }

int main(int argc, char** argv){
    uint64_t X = argc>1 ? strtoull(argv[1],0,10) : 4000000000ULL;
    uint64_t nb = X/8 + 2;
    uint8_t* S = malloc(nb); memset(S, 0xFF, nb);   /* S[n]=1 means in S (candidate) */
    S[0] &= ~1;  /* n=0 out */
    uint32_t sq = (uint32_t)sqrt((double)X);
    while ((uint64_t)(sq+1)*(sq+1) <= X) sq++;
    /* small prime sieve to sq */
    uint8_t* isp = malloc(sq+1); memset(isp,1,sq+1); isp[0]=isp[1]=0;
    for (uint32_t i=2;(uint64_t)i*i<=sq;i++) if(isp[i]) for(uint32_t j=i*i;j<=sq;j+=i) isp[j]=0;

    /* Step 1: bad primes p <= sq: exclude n with odd v_p */
    #pragma omp parallel for schedule(dynamic,1)
    for (uint32_t p=3;p<=sq;p+=2){
        if(!isp[p] || !is_bad_mod8(p)) continue;
        for (uint64_t j=p;j<=X;j+=p){
            uint64_t n=j; int v=0;
            do { n/=p; v++; } while (n%p==0);
            if (v & 1){
                #pragma omp atomic
                S[j>>3] &= ~(uint8_t)(1u<<(j&7));
            }
        }
    }
    fprintf(stderr,"step1 done\n");
    /* Step 2: bad primes p in (sq, X]: all multiples excluded.
       Segmented prime sieve over (sq, X], for each bad prime clear multiples. */
    uint64_t SEG = 1u<<24;
    #pragma omp parallel
    {
        uint8_t* seg = malloc(SEG);
        #pragma omp for schedule(dynamic,1)
        for (uint64_t lo = (uint64_t)sq+1; lo <= X; lo += SEG){
            uint64_t hi = lo+SEG-1; if (hi>X) hi=X;
            uint64_t len = hi-lo+1;
            memset(seg,1,len);
            for (uint32_t p=2;p<=sq;p++){
                if(!isp[p]) continue;
                uint64_t st = ((lo+p-1)/p)*p; if (st < (uint64_t)p*p) st = (uint64_t)p*p;
                for (uint64_t j=st;j<=hi;j+=p) seg[j-lo]=0;
            }
            for (uint64_t i=0;i<len;i++) if(seg[i]){
                uint64_t p = lo+i;
                if (is_bad_mod8(p)){
                    for (uint64_t j=p;j<=X;j+=p){
                        #pragma omp atomic
                        S[j>>3] &= ~(uint8_t)(1u<<(j&7));
                    }
                }
            }
        }
        free(seg);
    }
    fprintf(stderr,"step2 done\n");
    /* scan: membership count, density checkpoints, equal-gap run records */
    uint64_t cnt=0;
    uint64_t prev=0, prevgap=0, runlen=1;  /* runlen = number of equal gaps in current run + 1 elements */
    int bestlen=0;
    /* mod 8 histogram */
    uint64_t mod8[8]; memset(mod8,0,sizeof mod8);
    FILE* rec = fopen("sqrt2_records.txt","w");
    FILE* dens = fopen("sqrt2_density.txt","w");
    uint64_t next_ckpt = 1000000;
    for (uint64_t n=1;n<=X;n++){
        if (S[n>>3] & (1u<<(n&7))){
            cnt++; mod8[n&7]++;
            if (prev){
                uint64_t gap = n-prev;
                if (gap==prevgap) runlen++;
                else { runlen=2; prevgap=gap; }
                /* runlen elements share equal gap chain: number of terms = runlen (elements), gaps = runlen-1 */
                if ((int)runlen > bestlen){
                    bestlen = runlen;
                    fprintf(rec,"RECORD l=%d (terms) gap=%llu last=%llu first=%llu\n",
                        (int)runlen,(unsigned long long)prevgap,(unsigned long long)n,
                        (unsigned long long)(n-(runlen-1)*prevgap));
                    fflush(rec);
                }
            }
            prev=n;
        }
        if (n==next_ckpt){
            fprintf(dens,"%llu %llu\n",(unsigned long long)n,(unsigned long long)cnt);
            next_ckpt = (uint64_t)(next_ckpt*1.2589254117941673); /* 10^(1/10) steps */
            if (next_ckpt<=n) next_ckpt=n+1;
        }
    }
    fprintf(dens,"%llu %llu\n",(unsigned long long)X,(unsigned long long)cnt);
    printf("X=%llu |S|=%llu\n",(unsigned long long)X,(unsigned long long)cnt);
    for(int r=0;r<8;r++) printf("mod8[%d]=%llu\n",r,(unsigned long long)mod8[r]);
    fclose(rec); fclose(dens);
    return 0;
}
