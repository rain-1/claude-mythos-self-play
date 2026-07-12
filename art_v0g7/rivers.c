// Rivers of Totient — functional graph of a -> a + phi(a) on [1, N], N = 2^27.
// Chart: x = log2(a) in [0,27] -> [0,R); y = (1 - phi(a)/a) -> [0,R)
//   (odd sky on top: primes at y~0; even sea below y=R/2; parity is conserved).
// Outputs:
//   fog.f32    : 4 channels x R x R float32
//                ch0 structural fog (weight 1/(a*p_keep), all/subsampled edges)
//                ch1 log-mass fog   (same edges, w * log2(1+mass))
//                ch2 river mass     (ALL edges with mass>=16, w = mass/a)
//                ch3 squarefree node dust (same subsample as ch0)
//   rivers.bin : int32 a, int32 next, int64 mass for mass >= RIVER_MIN
//   orbit.txt  : the MO orbit 1,2,3,5,9,15,... while <= N (a, phi, squarefree)
//   stats.txt  : verifications (phi brute-force, parity crossings, locks,
//                exit-mass conservation, in-degree, threshold counts)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <omp.h>

#define N   (1u<<27)
#define R   4096
#define X1  27.0
#define ACUT (1u<<23)        /* below this: keep every edge */
#define RIVER_MIN 64
#define YCROP 0.86

static int32_t *phi;
static uint8_t *sf, *comp;
static int64_t *mass;
static int32_t *primes; static int np=0;

static inline double xpix(double a){ return log2(a)/X1*(R-1); }
static inline double ypix(uint32_t a){ return (1.0 - (double)phi[a]/(double)a)/YCROP*(R-1); }

static inline void bil(float *g, double x, double y, double w){
    if(x<0||y<0||x>R-1.001||y>R-1.001) return;
    int ix=(int)x, iy=(int)y; double fx=x-ix, fy=y-iy;
    float *p=g+(size_t)iy*R+ix;
    p[0]   += (float)(w*(1-fx)*(1-fy));
    p[1]   += (float)(w*fx*(1-fy));
    p[R]   += (float)(w*(1-fx)*fy);
    p[R+1] += (float)(w*fx*fy);
}
static inline void seg(float *g, double x0,double y0,double x1,double y1,double w){
    double dx=x1-x0, dy=y1-y0;
    int n=(int)(fmax(fabs(dx),fabs(dy)))+1; if(n>4096)n=4096;
    double ws=w/n;
    for(int i=0;i<n;i++){ double t=(i+0.5)/n; bil(g,x0+t*dx,y0+t*dy,ws); }
}
static inline uint64_t xs64(uint64_t *s){ uint64_t x=*s; x^=x<<13; x^=x>>7; x^=x<<17; return *s=x; }

static int32_t phi_brute(uint32_t n){
    uint32_t r=n, m=n;
    for(uint32_t p=2;(uint64_t)p*p<=m;p++) if(m%p==0){ r-=r/p; while(m%p==0)m/=p; }
    if(m>1) r-=r/m; return (int32_t)r;
}

int main(void){
    FILE *st=fopen("stats.txt","w");
    phi=malloc(sizeof(int32_t)*((size_t)N+1));
    sf=malloc((size_t)N+1); comp=calloc((size_t)N+1,1);
    primes=malloc(sizeof(int32_t)*7800000);
    phi[1]=1; sf[1]=1;
    for(uint32_t i=2;i<=N;i++){
        if(!comp[i]){ primes[np++]=i; phi[i]=i-1; sf[i]=1; }
        for(int j=0;j<np;j++){
            uint64_t v=(uint64_t)primes[j]*i; if(v>N) break;
            comp[v]=1;
            if(i%primes[j]==0){ phi[v]=phi[i]*primes[j]; sf[v]=0; break; }
            phi[v]=phi[i]*(primes[j]-1); sf[v]=sf[i];
        }
    }
    fprintf(st,"primes up to N: %d\n",np);
    /* verify phi against brute force */
    {   uint64_t s=88172645463325252ULL; int bad=0;
        for(int k=0;k<2000;k++){ uint32_t a=(uint32_t)(xs64(&s)%N)+1;
            if(phi[a]!=phi_brute(a)) bad++; }
        fprintf(st,"phi brute-force check (2000 random): %s\n",bad?"FAIL":"OK");
    }
    /* mass accumulation (ascending a; next > a always) */
    mass=malloc(sizeof(int64_t)*((size_t)N+1));
    for(size_t i=0;i<=N;i++) mass[i]=1;
    int64_t exit_mass=0; uint64_t cross=0; int64_t indeg_max=0; uint32_t argmax=0;
    int64_t *indeg=calloc((size_t)N+1,sizeof(int64_t));
    uint8_t *hin=calloc((size_t)N+1,1);   /* heavy in-degree (preimages with mass>=RIVER_MIN) */
    for(uint32_t a=1;a<=N;a++){
        uint64_t nx=(uint64_t)a+(uint64_t)phi[a];
        if(((a^ (uint32_t)nx)&1u)) cross++;
        if(nx<=N){ mass[nx]+=mass[a]; indeg[nx]++; if(mass[a]>=RIVER_MIN&&hin[nx]<255)hin[nx]++; }
        else exit_mass+=mass[a];
    }
    for(uint32_t a=2;a<=N;a++) if(indeg[a]>indeg_max){indeg_max=indeg[a];argmax=a;}
    fprintf(st,"exit mass = %lld (expect %u) %s\n",(long long)exit_mass,N,
            exit_mass==(int64_t)N?"OK":"FAIL");
    fprintf(st,"parity-crossing edges = %llu (expect 2: 1->2, 2->3)\n",(unsigned long long)cross);
    fprintf(st,"max in-degree = %lld at a=%u\n",(long long)indeg_max,argmax);
    /* locks: 2^k -> 3*2^(k-1) -> 2^(k+1) */
    int lock_ok=1;
    for(int k=2;k<=25;k++){
        uint32_t a=1u<<k;
        uint32_t b=a+phi[a]; uint32_t c=(uint64_t)b+phi[b]<=N? b+phi[b]:0;
        if(b!=3u<<(k-1) || (c && c!=1u<<(k+1))) lock_ok=0;
    }
    fprintf(st,"doubling locks 2^k->3*2^(k-1)->2^(k+1), k=2..25: %s\n",lock_ok?"OK":"FAIL");
    /* threshold counts */
    for(int t=10;t<=20;t+=2){
        int64_t c=0; for(uint32_t a=1;a<=N;a++) if(mass[a]>=(1LL<<t)) c++;
        fprintf(st,"nodes with mass >= 2^%d: %lld\n",t,(long long)c);
    }
    { int64_t c=0; for(uint32_t a=1;a<=N;a++) if(mass[a]>=16) c++;
      fprintf(st,"nodes with mass >= 16 (ch2 edges): %lld\n",(long long)c); }
    free(indeg);
    /* orbit */
    { FILE *f=fopen("orbit.txt","w"); uint64_t a=1;
      while(a<=N){ fprintf(f,"%llu %d %d %lld\n",(unsigned long long)a,phi[a],sf[a],(long long)mass[a]); a+=(uint64_t)phi[a]; }
      fclose(f); }
    { FILE *f=fopen("confl.txt","w"); int64_t c=0;
      for(uint32_t a=1;a<=N;a++) if(hin[a]>=2){ fprintf(f,"%u %lld %d %d\n",a,(long long)mass[a],hin[a],a&1); c++; }
      fclose(f); fprintf(st,"confluences (>=2 heavy tributaries): %lld\n",(long long)c); }
    free(hin);
    /* river export */
    { FILE *f=fopen("rivers.bin","wb"); int64_t c=0;
      for(uint32_t a=1;a<=N;a++) if(mass[a]>=RIVER_MIN){
          uint64_t nx=(uint64_t)a+phi[a]; uint32_t nx32=nx<=N?(uint32_t)nx:0;
          fwrite(&a,4,1,f); fwrite(&nx32,4,1,f); fwrite(&mass[a],8,1,f); c++; }
      fclose(f); fprintf(st,"river edges exported (mass>=%d): %lld\n",RIVER_MIN,(long long)c); }
    fflush(st);
    /* splat */
    int nt=omp_get_max_threads(); if(nt>4)nt=4;
    size_t GS=(size_t)R*R;
    float **G=malloc(sizeof(float*)*nt);
    for(int t=0;t<nt;t++) G[t]=calloc(GS*5,sizeof(float));
    double t0=omp_get_wtime();
    #pragma omp parallel num_threads(nt)
    {
        int tid=omp_get_thread_num(); float *g=G[tid];
        uint64_t seed=0x9E3779B97F4A7C15ULL*(tid+1)+12345;
        #pragma omp for schedule(dynamic,1u<<20)
        for(uint32_t a=2;a<=N;a++){
            uint64_t nx=(uint64_t)a+phi[a];
            double x0=xpix(a), y0=ypix(a);
            double x1,y1;
            if(nx<=N){ x1=xpix((double)nx); y1=ypix((uint32_t)nx); }
            else     { x1=xpix((double)nx); y1=y0; } /* exit: glide out of frame */
            int po=a&1;  /* parity of source (edges never cross for a>=3) */
            if(mass[a]>=16 && nx<=N) seg(g+(po?3:2)*GS,x0,y0,x1,y1,(double)mass[a]/a);
            double pk = a<ACUT ? 1.0 : (double)ACUT/a;
            if(a<ACUT || (xs64(&seed)>>11)*(1.0/9007199254740992.0) < pk){
                double w=1.0/((double)a*pk);
                seg(g+(po?1:0)*GS,x0,y0,x1,y1,w);
                if(sf[a]) bil(g+4*GS,x0,y0,w);
            }
        }
    }
    for(int t=1;t<nt;t++) for(size_t i=0;i<GS*5;i++) G[0][i]+=G[t][i];
    fprintf(st,"splat time %.1f s\n",omp_get_wtime()-t0);
    { FILE *f=fopen("fog.f32","wb"); fwrite(G[0],sizeof(float),GS*5,f); fclose(f); }
    fclose(st);
    return 0;
}
