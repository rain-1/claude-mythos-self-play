/* MO 514772 census engine: f(n) = max # lattice points ON a circle whose
   interior contains EXACTLY n lattice points, computed exactly for all
   n <= NMAX by exhaustive enumeration of translation classes of circles
   through >= 3 lattice points with circumradius <= RMAX.

   Correctness: any circle with >= 3 lattice points and interior count
   n <= NMAX has r <= sqrt(n/pi) + 1/sqrt(2)  (unit squares centered at
   interior lattice points cover D(c, r - 1/sqrt(2))), so RMAX =
   sqrt(NMAX/pi) + 0.7072 covers everything.

   Phase 1: enumerate all pairs (b,c) of lattice points near the origin;
   circle through (0,0),b,c keyed by the translation-invariant key
   (A, -G mod 2A, -F mod 2A, G*G+F*F); hash-dedupe WITH multiplicity.
   A class with k rim points is generated exactly k*C(k-1,2) times
   (anchor choice * pair choice), so k is recovered from the multiplicity
   and later ASSERTED against the direct rim count.

   Phase 2: exact interior/on counts (integer arithmetic) for every class
   with k >= 4; maintain best[n] = max k and a witness circle per n.

   Phase 3: for n <= NMAX not covered by any k>=4 class, sweep k=3
   classes to determine whether f(n)=3 (or n is missed entirely).

   Output: one line per n: "F n k A G F num" (witness; r^2 = num/(4A^2)),
   k=0 if no circle with >=3 rim points has exactly n interior.
   gcc -O3 -march=native fcensus.c -o fcensus -lm ; ./fcensus RMAX NMAX  */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

static int64_t g64(int64_t a, int64_t b){ while(b){int64_t t=a%b;a=b;b=t;} return a<0?-a:a; }

typedef struct { int64_t A,G,F,num; uint32_t mult; } Circ;

static uint64_t *H1, *H2; static uint32_t *HI; static size_t HN;
static Circ *cs; static size_t ncirc, ccap;

static inline void insert(uint64_t k1, uint64_t k2){
    uint64_t h = k1*0x9E3779B97F4A7C15ULL ^ k2*0xC2B2AE3D27D4EB4FULL;
    h ^= h>>29; h *= 0xBF58476D1CE4E5B9ULL; h ^= h>>32;
    size_t i = h & (HN-1);
    for(;;){
        if(!H1[i] && !H2[i]){
            H1[i]=k1; H2[i]=k2;
            if(ncirc==ccap){ ccap<<=1; cs=realloc(cs,ccap*sizeof(Circ)); }
            HI[i]=(uint32_t)ncirc; ncirc++;
            return;
        }
        if(H1[i]==k1 && H2[i]==k2){ cs[HI[i]].mult++; return; }
        i = (i+1) & (HN-1);
    }
}

/* exact rim/interior count for class t; returns rim in *onp, interior in
   *inp (interior counted fully; caller decides NMAX cut) */
static void count_circle(const Circ *c, int *onp, long *inp){
    int64_t A=c->A, G=c->G, F=c->F;
    double cxf = -G/(2.0*A), cyf = -F/(2.0*A);
    double r = sqrt((double)c->num)/(2.0*A);
    int x0=(int)ceil(cxf-r-1e-9), x1=(int)floor(cxf+r+1e-9);
    int y0=(int)ceil(cyf-r-1e-9), y1=(int)floor(cyf+r+1e-9);
    int on=0; long in=0;
    for(int x=x0;x<=x1;x++){
        int64_t xx = A*(int64_t)x*x + G*x;
        for(int y=y0;y<=y1;y++){
            int64_t v = xx + A*(int64_t)y*y + F*y;
            if(v<0) in++; else if(v==0) on++;
        }
    }
    *onp=on; *inp=in;
}

int main(int argc, char**argv){
    double RMAX = argc>1 ? atof(argv[1]) : 36.85;
    long NMAX = argc>2 ? atol(argv[2]) : 4096;
    double D = 2*RMAX; int DI = (int)floor(D);
    int np=0, cap=(2*DI+1)*(2*DI+1);
    int *px = malloc(cap*4), *py = malloc(cap*4);
    for(int x=-DI;x<=DI;x++) for(int y=-DI;y<=DI;y++)
        if((x||y) && (double)x*x+(double)y*y <= D*D){ px[np]=x; py[np]=y; np++; }
    fprintf(stderr,"RMAX=%g NMAX=%ld points=%d\n", RMAX, NMAX, np);

    HN = RMAX>40 ? (1ULL<<28) : (1ULL<<27);
    H1 = calloc(HN,8); H2 = calloc(HN,8); HI = calloc(HN,4);
    if(!H1||!H2||!HI){fprintf(stderr,"alloc fail\n");return 1;}
    ccap=1<<22; cs = malloc(ccap*sizeof(Circ)); ncirc=0;

    double R2q = RMAX*RMAX;
    for(int i=0;i<np;i++){
        int64_t bx=px[i], by=py[i], nb=bx*bx+by*by;
        for(int j=i+1;j<np;j++){
            int64_t cx=px[j], cy=py[j];
            int64_t dx=cx-bx, dy=cy-by;
            if((double)dx*dx+(double)dy*dy > D*D) continue;
            int64_t A = bx*cy - by*cx;
            if(!A) continue;
            int64_t nc = cx*cx+cy*cy;
            int64_t G = -nb*cy + nc*by;
            int64_t F =  nb*cx - nc*bx;
            if(A<0){A=-A;G=-G;F=-F;}
            int64_t g = g64(g64(A,G),F);
            A/=g; G/=g; F/=g;
            int64_t num = G*G + F*F;
            if((double)num > R2q*4.0*A*A) continue;
            int64_t twoA = 2*A;
            int64_t gm = (-G) % twoA; if(gm<0) gm += twoA;
            int64_t fm = (-F) % twoA; if(fm<0) fm += twoA;
            uint64_t k1 = ((uint64_t)A<<30) | ((uint64_t)gm<<15) | (uint64_t)fm;
            uint64_t k2 = (uint64_t)num;
            /* pack guard: A < 2^14 required by the key packing */
            if(A >= (1<<14)){ fprintf(stderr,"KEYPACK OVERFLOW A=%lld\n",(long long)A); return 2; }
            cs[ncirc].A=A; cs[ncirc].G=G; cs[ncirc].F=F; cs[ncirc].num=num; cs[ncirc].mult=0;
            insert(k1,k2);
        }
        if((i&1023)==0) fprintf(stderr,"\rphase1 %d/%d classes=%zu", i, np, ncirc);
    }
    free(H1); free(H2); free(HI);
    fprintf(stderr,"\nunique classes: %zu\n", ncirc);

    /* mult -> k: mult = k*(k-1)*(k-2)/2 + ... wait: mult counts pair
       insertions; the FIRST insertion also counts. total generations of a
       class = k * C(k-1,2); mult field counted generations-1, so
       gens = mult+1. Solve k(k-1)(k-2)/2 = gens. */
    long *kof = malloc(ncirc*sizeof(long));
    long kmaxseen=0;
    for(size_t t=0;t<ncirc;t++){
        uint64_t gens = (uint64_t)cs[t].mult + 1;
        /* k ~ cbrt(2*gens) */
        long k = (long)floor(cbrt(2.0*gens)+0.5);
        while(k*(k-1)*(k-2)/2 < (long)gens) k++;
        while(k>3 && (uint64_t)(k*(k-1)*(k-2)/2) > gens) k--;
        if((uint64_t)(k*(k-1)*(k-2)/2) != gens){
            fprintf(stderr,"MULT MISMATCH t=%zu gens=%llu\n", t,(unsigned long long)gens);
            return 3;
        }
        kof[t]=k; if(k>kmaxseen) kmaxseen=k;
    }
    fprintf(stderr,"kmax from multiplicity: %ld\n", kmaxseen);

    uint32_t *pop = calloc((NMAX+1)*65, sizeof(uint32_t));
    int *best = calloc(NMAX+1, sizeof(int));
    long *wit = malloc((NMAX+1)*sizeof(long));      /* witness index */
    for(long n=0;n<=NMAX;n++) wit[n]=-1;
    double rcut = sqrt((double)NMAX/M_PI)+0.7072;   /* classes beyond can't have n<=NMAX */

    size_t did=0, asserted=0;
    for(size_t t=0;t<ncirc;t++){
        if(kof[t] < 4) continue;
        double r = sqrt((double)cs[t].num)/(2.0*cs[t].A);
        if(r > rcut) continue;
        int on; long in;
        count_circle(&cs[t], &on, &in);
        if(on != kof[t]){
            fprintf(stderr,"RIM ASSERT FAIL t=%zu on=%d kmult=%ld A=%lld G=%lld F=%lld num=%lld\n",
                t,on,kof[t],(long long)cs[t].A,(long long)cs[t].G,(long long)cs[t].F,(long long)cs[t].num);
            return 4;
        }
        asserted++;
        if(in <= NMAX){
            if(on > best[in]){ best[in]=on; wit[in]=(long)t; }
            if(on<=64) pop[in*65+on]++;
        }
        did++;
        if((did&65535)==0) fprintf(stderr,"\rphase2 %zu", did);
    }
    fprintf(stderr,"\nphase2 classes counted: %zu (rim asserts passed: %zu)\n", did, asserted);

    long uncovered=0;
    for(long n=0;n<=NMAX;n++) if(!best[n]) uncovered++;
    fprintf(stderr,"uncovered n after k>=4: %ld\n", uncovered);

    if(uncovered){
        long maxunc=0;
        for(long n=0;n<=NMAX;n++) if(!best[n]) maxunc=n;
        double rcut2 = sqrt((double)maxunc/M_PI)+0.7072;
        fprintf(stderr,"phase3 rcut2=%g (max uncovered n=%ld)\n", rcut2, maxunc);
        /* prefix count of uncovered n, for interval pruning */
        long *upre = malloc((NMAX+2)*sizeof(long));
        upre[0]=0;
        for(long n=0;n<=NMAX;n++) upre[n+1]=upre[n]+(best[n]?0:1);
        for(size_t t=0;t<ncirc && uncovered;t++){
            if(kof[t] != 3) continue;
            double r = sqrt((double)cs[t].num)/(2.0*cs[t].A);
            if(r > rcut2) continue;
            /* class interior count lies in [pi(r-c)^2, pi(r+c)^2]; skip if
               no uncovered n in that window */
            double c0=0.70711;
            long nlo = (long)floor(M_PI*(r>c0?(r-c0)*(r-c0):0))- 2; if(nlo<0)nlo=0;
            long nhi = (long)ceil(M_PI*(r+c0)*(r+c0))+2; if(nhi>NMAX)nhi=NMAX;
            if(nlo>NMAX) continue;
            if(upre[nhi+1]-upre[nlo]==0) continue;
            int on; long in;
            count_circle(&cs[t], &on, &in);
            if(on != 3){ fprintf(stderr,"RIM3 ASSERT FAIL t=%zu on=%d\n",t,on); return 5; }
            if(in <= NMAX && !best[in]){
                best[in]=3; wit[in]=(long)t; uncovered--;
                for(long m=in+1;m<=NMAX+1;m++) upre[m]--;   /* keep prefix valid */
            }
            if((t&1048575)==0) fprintf(stderr,"\rphase3 %zu uncovered=%ld", t, uncovered);
        }
        fprintf(stderr,"\nuncovered n after k=3 sweep: %ld\n", uncovered);
    }

    for(long n=0;n<=NMAX;n++){
        if(wit[n]>=0){
            Circ *c=&cs[wit[n]];
            printf("F %ld %d %lld %lld %lld %lld\n", n, best[n],
                (long long)c->A,(long long)c->G,(long long)c->F,(long long)c->num);
        } else printf("F %ld 0 0 0 0 0\n", n);
    }
    for(long n=0;n<=NMAX;n++) for(int k=4;k<=64;k++)
        if(pop[n*65+k]) printf("P %ld %d %u\n", n, k, pop[n*65+k]);
    return 0;
}
