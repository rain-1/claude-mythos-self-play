/* Atlas piece 41, part 2: DEEP WINDOWED HUNT for the silent channels.
   Same membership sieve as piece 40 (segmented full factorization) but NO
   global bitmap: segments are sieved in parallel and consumed strictly in
   order (omp ordered), so the consecutive-member run scan carries across
   segments with O(1) state.  Works for any X1 (RAM ~ threads * 40MB).

   Tracks: maximal equal-gap runs (l>=3, gap<GMAX), first occurrences,
   record run lengths, l>=5 alarms for gaps 14/17/23/24/25, l>=6 alarms,
   |S| checkpoints.  Range-resumable: pass X0 > 0 to start there (the scan
   quietly warms up from X0-1e6 to rebuild run state; results with start <
   X0 are suppressed).  Output files carry the X0-X1 suffix.

   gcc -O3 -march=native -fopenmp hunt17.c -o hunt17
   ./hunt17 X0 X1                                                            */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <omp.h>

#define SEGLOG 22
#define SEG (1ULL<<SEGLOG)
enum { GMAX = 256, LMAX = 12 };

static inline int bad_mod8(uint64_t p){ uint64_t r = p & 7; return r==3 || r==5; }

static uint64_t runcount[LMAX+1][GMAX];
static uint64_t first_n[LMAX+1][GMAX];
static uint64_t Scount = 0;          /* members seen with n >= X0 */
static uint64_t prev=0, gap=0, runlen=1;
static int bestlen = 0;
static FILE *frec, *falarm, *fdens;
static uint64_t X0g;

static inline void close_run(void){
    if (runlen>=3 && gap<GMAX){
        uint64_t start = prev-(runlen-1)*gap;
        if (start >= X0g){
            int l = runlen>LMAX?LMAX:(int)runlen;
            runcount[l][gap]++;
        }
    }
}
static inline void feed(uint64_t n){
    if (prev){
        uint64_t g = n-prev;
        if (g==gap) runlen++;
        else { close_run(); runlen=2; gap=g; }
        if (runlen>=3 && gap<GMAX){
            int l = runlen>LMAX?LMAX:(int)runlen;
            uint64_t start = n-(runlen-1)*gap;
            if (start >= X0g && !first_n[l][gap]){
                first_n[l][gap] = start;
                if (l>=5 && (gap==14||gap==17||gap==23||gap==24||gap==25)){
                    fprintf(falarm,"FIRST l=%d g=%llu start=%llu\n",l,
                        (unsigned long long)gap,(unsigned long long)start);
                    fflush(falarm);
                }
            }
            /* piece 46: log EVERY l>=4 occurrence at the hot gaps
               (l=4 positions are the denominators of the 4->5 hazard) */
            if (start >= X0g && runlen>=4 && (gap==23||gap==24||gap==25)){
                fprintf(falarm,"OCC l=%d g=%llu start=%llu\n",(int)runlen,
                    (unsigned long long)gap,(unsigned long long)start);
                fflush(falarm);
            }
            if ((int)runlen > bestlen && start >= X0g){
                bestlen=runlen;
                fprintf(frec,"RECORD l=%d gap=%llu start=%llu\n",(int)runlen,
                    (unsigned long long)gap,(unsigned long long)start);
                fflush(frec);
            }
            if (runlen>=6 && start >= X0g){
                fprintf(falarm,"L6+! l=%d gap=%llu start=%llu\n",(int)runlen,
                    (unsigned long long)gap,(unsigned long long)start);
                fflush(falarm);
            }
        }
    }
    prev=n;
    if (n >= X0g) Scount++;
}

int main(int argc, char** argv){
    uint64_t X0 = argc>1 ? strtoull(argv[1],0,10) : 0;
    uint64_t X1 = argc>2 ? strtoull(argv[2],0,10) : 160000000000ULL;
    X0g = X0;
    uint64_t start_at = X0 > 1000000 ? X0 - 1000000 : 0;
    uint32_t sq = (uint32_t)sqrt((double)X1);
    while ((uint64_t)(sq+1)*(sq+1) <= X1) sq++;
    uint8_t* isp = malloc((size_t)sq+1); memset(isp,1,(size_t)sq+1); isp[0]=isp[1]=0;
    for (uint32_t i=2;(uint64_t)i*i<=sq;i++) if(isp[i]) for(uint64_t j=(uint64_t)i*i;j<=sq;j+=i) isp[j]=0;
    uint32_t np=0; for(uint32_t i=2;i<=sq;i++) np+=isp[i];
    uint32_t* primes = malloc(4ULL*np); uint32_t k=0;
    for(uint32_t i=2;i<=sq;i++) if(isp[i]) primes[k++]=i;
    free(isp);
    fprintf(stderr,"range [%llu,%llu) sqrt=%u primes=%u\n",
            (unsigned long long)X0,(unsigned long long)X1,sq,np);
    char fn[96];
    snprintf(fn,96,"hunt_records_%llu_%llu.txt",(unsigned long long)X0,(unsigned long long)X1);
    frec = fopen(fn,"w");
    snprintf(fn,96,"hunt_alarms_%llu_%llu.txt",(unsigned long long)X0,(unsigned long long)X1);
    falarm = fopen(fn,"w");
    snprintf(fn,96,"hunt_density_%llu_%llu.txt",(unsigned long long)X0,(unsigned long long)X1);
    fdens = fopen(fn,"w");
    memset(runcount,0,sizeof runcount); memset(first_n,0,sizeof first_n);

    uint64_t seg0 = start_at >> SEGLOG;
    uint64_t nseg = (X1 + SEG) >> SEGLOG;
    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        uint64_t* rem = malloc(8*SEG);
        uint8_t*  ex  = malloc(SEG);
        uint8_t*  memb = malloc(SEG/8);
        #pragma omp for ordered schedule(dynamic,1)
        for (uint64_t si=seg0; si<nseg; si++){
            uint64_t lo = si*SEG, hi = lo+SEG; if (hi > X1) hi = X1;
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
            memset(memb,0,SEG/8);
            for (uint64_t i=0;i<len;i++){
                if (!ex[i]){
                    uint64_t r = rem[i];
                    if (r>1 && bad_mod8(r)) continue;
                    memb[i>>3] |= (uint8_t)(1u<<(i&7));
                }
            }
            #pragma omp ordered
            {
                for (uint64_t i=0;i<len;i++)
                    if (memb[i>>3] & (1u<<(i&7))){
                        uint64_t n = lo+i;
                        if (n >= start_at && n >= 1) feed(n);
                    }
                if ((si & 511)==0){
                    double el = omp_get_wtime()-t0;
                    double frac = (double)(si-seg0+1)/(double)(nseg-seg0);
                    fprintf(stderr,"seg %llu/%llu  %.0fs  ETA %.0f min\n",
                        (unsigned long long)(si-seg0),(unsigned long long)(nseg-seg0),
                        el, el*(1.0/frac-1.0)/60.0);
                    fprintf(fdens,"%llu %llu\n",(unsigned long long)(lo+len),
                            (unsigned long long)Scount); fflush(fdens);
                }
            }
        }
        free(rem); free(ex); free(memb);
    }
    close_run();
    snprintf(fn,96,"hunt_rungap_%llu_%llu.txt",(unsigned long long)X0,(unsigned long long)X1);
    FILE* rg = fopen(fn,"w");
    fprintf(rg,"# range [%llu,%llu) |S∩range|=%llu\n",
            (unsigned long long)X0,(unsigned long long)X1,(unsigned long long)Scount);
    for (int l=3;l<=LMAX;l++) for (int g=1;g<GMAX;g++)
        if (runcount[l][g] || first_n[l][g])
            fprintf(rg,"l=%d g=%d maximal_runs=%llu first_start=%llu\n",l,g,
                (unsigned long long)runcount[l][g],(unsigned long long)first_n[l][g]);
    fclose(rg); fclose(frec); fclose(falarm); fclose(fdens);
    fprintf(stderr,"ALLDONE %.0fs |S|=%llu\n",omp_get_wtime()-t0,(unsigned long long)Scount);
    return 0;
}
