/* Atlas piece 41, part 1: DIAGNOSIS at 4e9.
   S = { n : v_p(n) even for every prime p = 3,5 mod 8 } (norms of Z[sqrt2]).
   Rebuild the 4e9 bitmap (piece 39/40 rig, same segmented full-factorization
   sieve => |S| must be 601,376,078 EXACTLY), then for gaps g in GSET:
     - C5(g)  = # of 5-term g-APs wholly in S, n+4g <= X
     - occupancy histogram of the 4g-4 window positions (members among them)
     - per-offset conditional probability  P( n+j in S | 5 posts in S )
     - fence count (occupancy 0) => must reproduce piece-40 W5 numbers at 4e9
   Output: diag17_out.txt (tables), diag17_prof_g<g>.txt (offset profiles).
   gcc -O3 -march=native -fopenmp diag17.c -o diag17 && ./diag17 4000000000 */
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
    fprintf(stderr,"X=%llu sqrt=%u primes=%u\n",(unsigned long long)X,sq,np);

    size_t nbytes = X/8 + 2;
    uint8_t* B = malloc(nbytes);
    if(!B){ fprintf(stderr,"OOM bitmap\n"); return 1; }
    memset(B,0,nbytes);
    uint64_t nseg = (X + SEG) / SEG;
    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        uint64_t* rem = malloc(8*SEG);
        uint8_t*  ex  = malloc(SEG);
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
                    if (r>1 && bad_mod8(r)) continue;
                    uint64_t n=lo+i;
                    B[n>>3] |= (uint8_t)(1u<<(n&7));
                }
            }
        }
        free(rem); free(ex);
    }
    fprintf(stderr,"sieve done %.0fs\n",omp_get_wtime()-t0);
    uint64_t cnt=0;
    #pragma omp parallel for reduction(+:cnt)
    for (uint64_t i=0;i<nbytes;i++) cnt += __builtin_popcount(B[i]);
    printf("X=%llu |S|=%llu\n",(unsigned long long)X,(unsigned long long)cnt);

    #define INS(n) ((B[(n)>>3] >> ((n)&7)) & 1)
    static const int GSET[] = {1,2,8,9,14,15,16,17,18};
    FILE* out = fopen("diag17_out.txt","w");
    fprintf(out,"X=%llu |S|=%llu density=%.6f\n",(unsigned long long)X,
            (unsigned long long)cnt,(double)cnt/(double)X);
    for (int gi=0; gi<(int)(sizeof GSET/sizeof*GSET); gi++){
        uint64_t g = GSET[gi];
        uint64_t C5=0, fence=0;
        uint64_t hist[64]; memset(hist,0,sizeof hist);
        uint64_t prof[80]; memset(prof,0,sizeof prof);   /* offsets 1..4g-1 */
        uint64_t nmax = X - 4*g;
        #pragma omp parallel
        {
            uint64_t lC5=0,lf=0,lh[64],lp[80];
            memset(lh,0,sizeof lh); memset(lp,0,sizeof lp);
            #pragma omp for schedule(static)
            for (uint64_t n=1;n<=nmax;n++){
                if (!INS(n)) continue;
                if (!INS(n+g)||!INS(n+2*g)||!INS(n+3*g)||!INS(n+4*g)) continue;
                lC5++;
                int occ=0;
                for (uint64_t j=1;j<4*g;j++){
                    if (j%g==0) continue;
                    if (INS(n+j)){ occ++; lp[j]++; }
                }
                if (occ<64) lh[occ]++;
                if (occ==0) lf++;
            }
            #pragma omp critical
            { C5+=lC5; fence+=lf;
              for(int i=0;i<64;i++) hist[i]+=lh[i];
              for(int i=0;i<80;i++) prof[i]+=lp[i]; }
        }
        fprintf(out,"g=%llu C5=%llu fences(W5)=%llu\n",
                (unsigned long long)g,(unsigned long long)C5,(unsigned long long)fence);
        fprintf(out,"  occ_hist:");
        for(int i=0;i<40;i++) if(hist[i]) fprintf(out," %d:%llu",i,(unsigned long long)hist[i]);
        fprintf(out,"\n");
        char fn[64]; snprintf(fn,64,"diag17_prof_g%llu.txt",(unsigned long long)g);
        FILE* pf = fopen(fn,"w");
        fprintf(pf,"# offset  count  cond_prob   (C5=%llu, uncond density=%.6f)\n",
                (unsigned long long)C5,(double)cnt/(double)X);
        for (uint64_t j=1;j<4*g;j++){
            if (j%g==0) continue;
            fprintf(pf,"%3llu %llu %.6f\n",(unsigned long long)j,
                    (unsigned long long)prof[j], C5?(double)prof[j]/(double)C5:0.0);
        }
        fclose(pf);
        fflush(out);
        fprintf(stderr,"g=%llu done %.0fs\n",(unsigned long long)g,omp_get_wtime()-t0);
    }
    fclose(out);
    fprintf(stderr,"all done %.0fs\n",omp_get_wtime()-t0);
    return 0;
}
