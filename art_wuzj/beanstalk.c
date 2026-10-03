// beanstalk.c — Pythagorean beanstalk (MO 515674), incremental over n.
// B_n = closure of {1..n} under (x,y in B, x^2+y^2=z^2) => z in B.  a(n) = max B_n.
// Since B_n ⊆ B_{n+1}, grow once: add seed n, propagate with a queue.
// For a new element w, every triple with leg w is (w, x, z) with d | w^2, d < w,
// d ≡ w^2/d (mod 2), x = (w^2/d - d)/2, z = (w^2/d + d)/2.
// usage: beanstalk N [dumpn] ; prints records of a(n); if dumpn, writes grown.txt for B_dumpn
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef uint64_t u64;
typedef unsigned __int128 u128;
#define MAXV (1ULL<<34)
static uint8_t *bits;
static inline int has(u64 v){ return v<MAXV && (bits[v>>3]>>(v&7))&1; }
static inline void put(u64 v){ bits[v>>3] |= 1<<(v&7); }
static uint32_t *primes; static int np;
static u64 *queue; static size_t qh=0, qt=0, qcap;
typedef struct { u64 z, x, y; uint32_t gen, born; } rec;
static rec *grown; static size_t ng=0, gcap;
static uint8_t *genof_small; // generation for values < GSMALL
#define GSMALL (1ULL<<31)
static int dumpflag=0;

static int factor(u64 w, u64 *p, int *e){
  int k=0;
  for(int i=0;i<np && (u64)primes[i]*primes[i]<=w;i++){
    if(w%primes[i]==0){ p[k]=primes[i]; e[k]=0; while(w%primes[i]==0){w/=primes[i];e[k]++;} k++; }
  }
  if(w>1){ p[k]=w; e[k]=1; k++; }
  return k;
}
static u64 maxv=0; static int overflow=0;
static uint32_t gen_of(u64 v){ return v<GSMALL? genof_small[v] : 0; }

static void process(u64 w, uint32_t born){
  u64 p[20]; int e[20]; int k=factor(w,p,e);
  for(int i=0;i<k;i++) e[i]*=2;
  u128 w2=(u128)w*w;
  // enumerate divisors of w^2 below w
  u64 divs[1<<16]; int nd=1; divs[0]=1;
  for(int i=0;i<k;i++){
    int cur=nd; u64 pp=1;
    for(int j=1;j<=e[i];j++){ pp*=p[i]; for(int t=0;t<cur;t++){ u64 d=divs[t]*pp; if(d<w && nd<(1<<16)) divs[nd++]=d; } }
  }
  for(int t=0;t<nd;t++){
    u64 d=divs[t]; u128 DD=w2/d; if(DD>=((u128)1<<64)) continue; u64 D=(u64)DD;  /* x > 2^63 is never a member */
    if(((d^D)&1)) continue;
    u64 x=(D-d)/2, z=(u64)(((u128)D+d)/2);
    if(x==0 || !has(x)) continue;
    if(z>=MAXV){ overflow++; continue; }
    if(has(z)) continue;
    put(z); if(z>maxv) maxv=z;
    uint32_t g = (gen_of(w)>gen_of(x)?gen_of(w):gen_of(x))+1;
    if(z<GSMALL) genof_small[z]=g>255?255:g;
    if(dumpflag){ if(ng==gcap){ gcap*=2; grown=realloc(grown,gcap*sizeof(rec)); }
    grown[ng++] = (rec){z,w,x,g,born}; } else ng++;
    if(qt==qcap){ qcap*=2; queue=realloc(queue,qcap*8); }
    queue[qt++]=z;
  }
}

int main(int argc,char**argv){
  u64 N=strtoull(argv[1],0,10); u64 dumpn = argc>2? strtoull(argv[2],0,10):0; dumpflag = dumpn>0;
  bits=calloc(MAXV/8,1);
  genof_small=calloc(GSMALL,1);
  int L=1<<17; char *c=calloc(L,1); primes=malloc(L*4);
  for(int i=2;i<L;i++) if(!c[i]){ primes[np++]=i; for(long j=(long)i*i;j<L;j+=i) c[j]=1; }
  qcap=1<<20; queue=malloc(qcap*8); gcap=1<<20; grown=malloc(gcap*sizeof(rec));
  u64 lasta=0;
  for(u64 n=1;n<=N;n++){
    if(!has(n)){ put(n); if(n>maxv) maxv=n; queue[qt++]=n; if(qt==qcap){qcap*=2;queue=realloc(queue,qcap*8);} }
    while(qh<qt){ u64 w=queue[qh++]; process(w,(uint32_t)n); }
    qh=qt=0;
    if(maxv!=lasta){ printf("%llu %llu\n",(unsigned long long)n,(unsigned long long)maxv); lasta=maxv; fflush(stdout); }
    if(n==dumpn){
      FILE *f=fopen("grown.txt","w");
      for(size_t i=0;i<ng;i++) if(grown[i].born<=n) fprintf(f,"%llu %llu %llu %u %u\n",(unsigned long long)grown[i].z,(unsigned long long)grown[i].x,(unsigned long long)grown[i].y,grown[i].gen,grown[i].born);
      fclose(f);
    }
  }
  fprintf(stderr,"N=%llu |grown|=%zu maxv=%llu overflow=%d\n",(unsigned long long)N,ng,(unsigned long long)maxv,overflow);
}
