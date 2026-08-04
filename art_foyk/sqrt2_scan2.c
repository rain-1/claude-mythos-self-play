/* Rescan with full run statistics: counts of maximal equal-gap runs by (l,gap), gap histogram,
   all l>=5 run listings, last-occurrence tracking. */
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
    uint8_t* S = malloc(nb); memset(S, 0xFF, nb);
    S[0] &= ~1;
    uint32_t sq = (uint32_t)sqrt((double)X);
    while ((uint64_t)(sq+1)*(sq+1) <= X) sq++;
    uint8_t* isp = malloc(sq+1); memset(isp,1,sq+1); isp[0]=isp[1]=0;
    for (uint32_t i=2;(uint64_t)i*i<=sq;i++) if(isp[i]) for(uint32_t j=i*i;j<=sq;j+=i) isp[j]=0;
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
                if (is_bad_mod8(p))
                    for (uint64_t j=p;j<=X;j+=p){
                        #pragma omp atomic
                        S[j>>3] &= ~(uint8_t)(1u<<(j&7));
                    }
            }
        }
        free(seg);
    }
    fprintf(stderr,"sieve done\n");
    /* maximal equal-gap runs: count by (l, gap) for gap<=128, l<=12 */
    #define MAXG 129
    uint64_t runcount[13][MAXG]; memset(runcount,0,sizeof runcount);
    uint64_t gaphist[MAXG]; memset(gaphist,0,sizeof gaphist);
    uint64_t bigrun_first[13]; memset(bigrun_first,0,sizeof bigrun_first);
    uint64_t bigrun_last[13]; memset(bigrun_last,0,sizeof bigrun_last);
    uint64_t prev=0, prevgap=0; uint64_t runlen=1;
    uint64_t cnt=0;
    FILE* l5 = fopen("sqrt2_l5runs.txt","w");
    uint64_t l5count=0;
    for (uint64_t n=1;n<=X;n++){
        if (!(S[n>>3] & (1u<<(n&7)))) continue;
        cnt++;
        if (prev){
            uint64_t gap = n-prev;
            if (gap<MAXG) gaphist[gap]++;
            if (gap==prevgap) runlen++;
            else {
                /* close maximal run of runlen terms with gap prevgap */
                if (runlen>=2 && prevgap<MAXG){
                    int l = runlen>12?12:(int)runlen;
                    runcount[l][prevgap]++;
                    if(runlen>=5){
                        if(!bigrun_first[l]) bigrun_first[l]= prev;
                        bigrun_last[l]=prev;
                        if(runlen>=5 && l5count<100000){ fprintf(l5,"%llu %llu %llu\n",(unsigned long long)(prev-(runlen-1)*prevgap),(unsigned long long)prevgap,(unsigned long long)runlen); l5count++; }
                    }
                }
                runlen=2; prevgap=gap;
            }
        }
        prev=n;
    }
    printf("|S| = %llu\n",(unsigned long long)cnt);
    printf("gap histogram (gap: count):\n");
    for(int g=1;g<40;g++) if(gaphist[g]) printf("  %d: %llu\n",g,(unsigned long long)gaphist[g]);
    printf("maximal equal-gap runs by (l, gap):\n");
    for(int l=3;l<=12;l++){
        uint64_t tl=0; for(int g=1;g<MAXG;g++) tl+=runcount[l][g];
        if(!tl) continue;
        printf("l=%d total=%llu :",l,(unsigned long long)tl);
        for(int g=1;g<MAXG;g++) if(runcount[l][g]) printf(" g%d:%llu",g,(unsigned long long)runcount[l][g]);
        printf("\n");
    }
    for(int l=5;l<=12;l++) if(bigrun_first[l]) printf("l=%d first-end=%llu last-end=%llu\n",l,(unsigned long long)bigrun_first[l],(unsigned long long)bigrun_last[l]);
    return 0;
}
