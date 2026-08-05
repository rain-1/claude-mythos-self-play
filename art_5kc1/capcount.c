/* Piece 40 analysis: X=4e9 census + per-gap statistics:
   C_l(g) = # n: n, n+g, .., n+(l-1)g ALL in S   (members allowed between; l=3,4,5)
   W_l(g) = # sliding windows of l consecutive members with all gaps == g (l=4,5)
   for g = 1..64.  Same sieve as sqrt2_deep.c.
   gcc -O3 -march=native -fopenmp capcount.c -o capcount */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <omp.h>
#define SEG (1ULL<<22)
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
    uint8_t* B = malloc(nbytes); memset(B,0,nbytes);
    uint64_t nseg = (X + SEG) / SEG;
    #pragma omp parallel
    {
        uint64_t* rem = malloc(8*SEG); uint8_t* ex = malloc(SEG);
        #pragma omp for schedule(dynamic,1)
        for (uint64_t si=0; si<nseg; si++){
            uint64_t lo = si*SEG, hi = lo+SEG; if (hi>X+1) hi=X+1;
            uint64_t len = hi-lo;
            for (uint64_t i=0;i<len;i++){ rem[i]=lo+i; ex[i]=0; }
            if (lo==0){ ex[0]=1; }
            for (uint32_t pi=0; pi<np; pi++){
                uint64_t p = primes[pi];
                int bad = bad_mod8(p);
                uint64_t st = ((lo+p-1)/p)*p; if (st==0) st=p;
                for (uint64_t j=st; j<hi; j+=p){
                    uint64_t i=j-lo, r=rem[i]; int v=0;
                    while (r%p==0){ r/=p; v++; }
                    rem[i]=r;
                    if (bad && (v&1)) ex[i]=1;
                }
            }
            for (uint64_t i=0;i<len;i++) if(!ex[i]){
                uint64_t r=rem[i];
                if (r>1 && bad_mod8(r)) continue;
                uint64_t n=lo+i; if(!n) continue;
                B[n>>3] |= (uint8_t)(1u<<(n&7));
            }
        }
        free(rem); free(ex);
    }
    fprintf(stderr,"sieve done\n");
    enum { GM = 65 };
    /* C_l(g): sliding AND over bitmap with shifts g..4g */
    static uint64_t C3[GM], C4[GM], C5[GM];
    #pragma omp parallel for schedule(dynamic,1)
    for (int g=1; g<GM; g++){
        uint64_t c3=0,c4=0,c5=0;
        for (uint64_t n=1; n+4*(uint64_t)g<=X; n++){
            if (!(B[n>>3]&(1u<<(n&7)))) continue;
            uint64_t a=n+g,b=n+2*g,c=n+3*g,d=n+4*g;
            if (!(B[a>>3]&(1u<<(a&7)))) continue;
            if (!(B[b>>3]&(1u<<(b&7)))) continue;
            c3++;
            if (!(B[c>>3]&(1u<<(c&7)))) continue;
            c4++;
            if (!(B[d>>3]&(1u<<(d&7)))) continue;
            c5++;
        }
        C3[g]=c3; C4[g]=c4; C5[g]=c5;
    }
    fprintf(stderr,"AP counts done\n");
    /* W_l(g): consecutive-member equal-gap sliding windows */
    static uint64_t W3[GM], W4[GM], W5[GM];
    memset(W3,0,sizeof W3); memset(W4,0,sizeof W4); memset(W5,0,sizeof W5);
    uint64_t prev=0; uint64_t g1=0,g2=0,g3=0,g4=0; /* last gaps, g1 most recent */
    FILE* rp = fopen("l5_positions.txt","w");
    for (uint64_t n=1;n<=X;n++){
        if (!(B[n>>3]&(1u<<(n&7)))) continue;
        if (prev){
            uint64_t g=n-prev;
            if (g<GM){
                if (g1==g) W3[g]++;                       /* 3 members, 2 gaps */
                if (g2==g && g1==g) W4[g]++;              /* 4 members, 3 gaps */
                if (g3==g && g2==g && g1==g){ W5[g]++;    /* 5 members, 4 gaps */
                    fprintf(rp,"%llu %llu\n",(unsigned long long)g,(unsigned long long)(n-4*g)); }
            }
            g4=g3; g3=g2; g2=g1; g1=g;
        }
        prev=n;
    }
    fclose(rp);
    uint64_t tot=0;
    for (uint64_t n=1;n<=X;n++) if (B[n>>3]&(1u<<(n&7))) tot++;
    printf("X=%llu |S|=%llu\n",(unsigned long long)X,(unsigned long long)tot);
    FILE* f=fopen("capcount_out.txt","w");
    for (int g=1;g<GM;g++)
        fprintf(f,"g=%d C3=%llu C4=%llu C5=%llu W3=%llu W4=%llu W5=%llu\n",g,
            (unsigned long long)C3[g],(unsigned long long)C4[g],(unsigned long long)C5[g],
            (unsigned long long)W3[g],(unsigned long long)W4[g],(unsigned long long)W5[g]);
    fclose(f);
    printf("done\n");
    return 0;
}
