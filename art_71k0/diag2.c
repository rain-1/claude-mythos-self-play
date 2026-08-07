/* Atlas 41, part 1b: collect per-pattern window-occupancy MASKS at 4e9.
   For each gap g in {14,15,16,17,18} and each 5-term g-AP wholly in S,
   write record: uint64 n, then two uint64 mask words (bit j of the 128-bit
   little-endian mask = [n+j in S], j = 1..4g-1, bits at j%g==0 left 0).
   Reuses the piece-39/40 segmented full-factorization sieve verbatim.
   gcc -O3 -march=native -fopenmp diag2.c -o diag2 && ./diag2 4000000000    */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <omp.h>

#define SEGLOG 22
#define SEG (1ULL<<SEGLOG)
static inline int bad_mod8(uint64_t p){ uint64_t r = p & 7; return r==3 || r==5; }

int main(int argc, char** argv){
    uint64_t X = argc>1 ? strtoull(argv[1],0,10) : 4000000000ULL;
    uint32_t sq = (uint32_t)sqrt((double)X);
    while ((uint64_t)(sq+1)*(sq+1) <= X) sq++;
    uint8_t* isp = malloc((size_t)sq+1); memset(isp,1,(size_t)sq+1); isp[0]=isp[1]=0;
    for (uint32_t i=2;(uint64_t)i*i<=sq;i++) if(isp[i]) for(uint64_t j=(uint64_t)i*i;j<=sq;j+=i) isp[j]=0;
    uint32_t np=0; for(uint32_t i=2;i<=sq;i++) np+=isp[i];
    uint32_t* primes = malloc(4ULL*np); uint32_t k=0;
    for(uint32_t i=2;i<=sq;i++) if(isp[i]) primes[k++]=i;
    free(isp);
    size_t nbytes = X/8 + 2;
    uint8_t* B = malloc(nbytes);
    if(!B){ fprintf(stderr,"OOM\n"); return 1; }
    memset(B,0,nbytes);
    uint64_t nseg = (X + SEG) / SEG;
    double t0=omp_get_wtime();
    #pragma omp parallel
    {
        uint64_t* rem = malloc(8*SEG); uint8_t* ex = malloc(SEG);
        #pragma omp for schedule(dynamic,1)
        for (uint64_t si=0; si<nseg; si++){
            uint64_t lo = si*SEG, hi = lo+SEG; if (hi > X+1) hi = X+1;
            uint64_t len = hi-lo;
            for (uint64_t i=0;i<len;i++){ rem[i]=lo+i; ex[i]=0; }
            if (lo==0){ ex[0]=1; if(len>1){rem[1]=1;} }
            for (uint32_t pi=0; pi<np; pi++){
                uint64_t p = primes[pi];
                uint64_t st = ((lo+p-1)/p)*p; if (st==0) st = p;
                if (st >= hi) continue;
                int bad = bad_mod8(p);
                for (uint64_t j=st; j<hi; j+=p){
                    uint64_t i = j-lo, r = rem[i]; int v=0;
                    while (r % p == 0){ r /= p; v++; }
                    rem[i]=r;
                    if (bad && (v&1)) ex[i]=1;
                }
            }
            for (uint64_t i=0;i<len;i++)
                if (!ex[i]){
                    uint64_t r = rem[i];
                    if (r>1 && bad_mod8(r)) continue;
                    uint64_t n=lo+i;
                    B[n>>3] |= (uint8_t)(1u<<(n&7));
                }
        }
        free(rem); free(ex);
    }
    fprintf(stderr,"sieve done %.0fs\n",omp_get_wtime()-t0);
    #define INS(n) ((B[(n)>>3] >> ((n)&7)) & 1)
    static const int GSET[] = {14,15,16,17,18};
    for (int gi=0; gi<5; gi++){
        uint64_t g = GSET[gi];
        char fn[64]; snprintf(fn,64,"diag2_g%llu.bin",(unsigned long long)g);
        FILE* f = fopen(fn,"wb");
        uint64_t nmax = X - 4*g, cnt=0;
        for (uint64_t n=1;n<=nmax;n++){
            if (!INS(n)) continue;
            if (!INS(n+g)||!INS(n+2*g)||!INS(n+3*g)||!INS(n+4*g)) continue;
            uint64_t m0=0,m1=0;
            for (uint64_t j=1;j<4*g;j++){
                if (j%g==0) continue;
                if (INS(n+j)){ if (j<64) m0 |= 1ULL<<j; else m1 |= 1ULL<<(j-64); }
            }
            fwrite(&n,8,1,f); fwrite(&m0,8,1,f); fwrite(&m1,8,1,f);
            cnt++;
        }
        fclose(f);
        fprintf(stderr,"g=%llu patterns=%llu\n",(unsigned long long)g,(unsigned long long)cnt);
    }
    fprintf(stderr,"done %.0fs\n",omp_get_wtime()-t0);
    return 0;
}
