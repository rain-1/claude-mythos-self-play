/* MO 514722 census engine: all circles through >=3 lattice points with
   circumradius <= RMAX, exact integer arithmetic, translation-dedup.
   Prints one line per unique circle with on-count >= 5:
       C k A G F num interior      (r^2 = num/(4A^2))
   and aggregates k=3,4 into radius-binned histograms:
       H k bin count min_interior   (bin = floor(r / 0.125))
   gcc -O3 -march=native circles.c -o circles -lm ; ./circles RMAX      */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

static int64_t g64(int64_t a, int64_t b){ while(b){int64_t t=a%b;a=b;b=t;} return a<0?-a:a; }

/* open-addressing hash of 128-bit keys */
static uint64_t *H1, *H2; static size_t HN;      /* HN power of two */
static inline int insert(uint64_t k1, uint64_t k2){
    uint64_t h = k1*0x9E3779B97F4A7C15ULL ^ k2*0xC2B2AE3D27D4EB4FULL;
    h ^= h>>29; h *= 0xBF58476D1CE4E5B9ULL; h ^= h>>32;
    size_t i = h & (HN-1);
    for(;;){
        if(!H1[i] && !H2[i]){ H1[i]=k1; H2[i]=k2; return 1; }
        if(H1[i]==k1 && H2[i]==k2) return 0;
        i = (i+1) & (HN-1);
    }
}

typedef struct { int64_t A,G,F,num; } Circ;

int main(int argc, char**argv){
    double RMAX = argc>1 ? atof(argv[1]) : 32.0;
    double D = 2*RMAX; int DI = (int)floor(D);
    /* candidate points (excluding origin) within D of origin */
    int np=0, cap=(2*DI+1)*(2*DI+1);
    int *px = malloc(cap*4), *py = malloc(cap*4);
    for(int x=-DI;x<=DI;x++) for(int y=-DI;y<=DI;y++)
        if((x||y) && (double)x*x+(double)y*y <= D*D){ px[np]=x; py[np]=y; np++; }
    fprintf(stderr,"RMAX=%g points=%d\n", RMAX, np);

    HN = 1; while(HN < 1ULL<<26) HN<<=1;        /* 67M slots = 1GB */
    HN = 1ULL<<26;
    H1 = calloc(HN,8); H2 = calloc(HN,8);
    if(!H1||!H2){fprintf(stderr,"alloc fail\n");return 1;}

    size_t ncirc=0, ccap=1<<20;
    Circ *cs = malloc(ccap*sizeof(Circ));
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
            /* pack: A<2^14, gm,fm<2^15, num<2^44 */
            uint64_t k1 = ((uint64_t)A<<30) | ((uint64_t)gm<<15) | (uint64_t)fm;
            uint64_t k2 = (uint64_t)num;
            if(insert(k1,k2)){
                if(ncirc==ccap){ ccap<<=1; cs=realloc(cs,ccap*sizeof(Circ)); }
                cs[ncirc].A=A; cs[ncirc].G=G; cs[ncirc].F=F; cs[ncirc].num=num;
                ncirc++;
            }
        }
    }
    free(H1); free(H2);
    fprintf(stderr,"unique circles: %zu\n", ncirc);

    enum{NB=400};
    long hist3[NB]; long hist4[NB]; long mi3[NB], mi4[NB];
    for(int b=0;b<NB;b++){hist3[b]=hist4[b]=0; mi3[b]=mi4[b]=-1;}

    for(size_t t=0;t<ncirc;t++){
        int64_t A=cs[t].A, G=cs[t].G, F=cs[t].F;
        double cxf = -G/(2.0*A), cyf = -F/(2.0*A);
        double r = sqrt((double)cs[t].num)/(2.0*A);
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
        if(on>=5){
            printf("C %d %lld %lld %lld %lld %ld\n", on,(long long)A,
                (long long)G,(long long)F,(long long)cs[t].num, in);
        } else {
            int b=(int)(r/0.125); if(b>=NB)b=NB-1;
            if(on==3){ hist3[b]++; if(mi3[b]<0||in<mi3[b])mi3[b]=in; }
            else if(on==4){ hist4[b]++; if(mi4[b]<0||in<mi4[b])mi4[b]=in; }
        }
    }
    for(int b=0;b<NB;b++){
        if(hist3[b]) printf("H 3 %d %ld %ld\n",b,hist3[b],mi3[b]);
        if(hist4[b]) printf("H 4 %d %ld %ld\n",b,hist4[b],mi4[b]);
    }
    return 0;
}
