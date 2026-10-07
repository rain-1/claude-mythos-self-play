// pivot.c — pivot-algorithm self-avoiding walk on the honeycomb (= one enormous bee number).
// Honeycomb = Eisenstein integers z=a+b*w with (a-b) mod 3 != 0; edges = unit steps.
// Stabiliser of a vertex v: z -> v + w^k (z-v), z -> v + w^k conj(z-v)   (D3).
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef struct {int a,b;} P;
static int N; static P *W,*T;
static uint64_t *tab; static int *tabv; static int *tabi; static uint64_t HM; static int stamp=1;
static uint64_t key(P p){return ((uint64_t)(uint32_t)(p.a+1000000)<<32)|(uint32_t)(p.b+1000000);}
static uint64_t hsh(uint64_t k){k^=k>>33;k*=0xff51afd7ed558ccdULL;k^=k>>33;k*=0xc4ceb9fe1a85ec53ULL;k^=k>>33;return k;}
static void ins(P p,int i){uint64_t k=key(p),h=hsh(k)&HM; while(tabv[h]==stamp&&tab[h]!=k)h=(h+1)&HM; tab[h]=k;tabv[h]=stamp;tabi[h]=i;}
static int idx(P p){uint64_t k=key(p),h=hsh(k)&HM; while(tabv[h]==stamp){if(tab[h]==k)return tabi[h];h=(h+1)&HM;} return -1;}
static int has(P p){uint64_t k=key(p),h=hsh(k)&HM; while(tabv[h]==stamp){if(tab[h]==k)return 1;h=(h+1)&HM;} return 0;}
// multiply by w: (a+bw)*w = a w + b w^2 = a w + b(-1-w) = -b + (a-b) w
static P mulw(P z){P r={-z.b,z.a-z.b};return r;}
static P cnj(P z){P r={z.a-z.b,-z.b};return r;} // conj(a+bw)=a+b w^2 = a-b - b w
static P apply(int g,P v,P z){P d={z.a-v.a,z.b-v.b}; if(g>=3)d=cnj(d); for(int k=0;k<g%3;k++)d=mulw(d); P r={v.a+d.a,v.b+d.b};return r;}
static uint64_t rs=88172645463325252ULL; static uint64_t rnd(){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return rs;}
int main(int argc,char**argv){
  N=atoi(argv[1]); long long iters=atoll(argv[2]); rs^=atoll(argv[3])*0x9E3779B97F4A7C15ULL;
  W=malloc(sizeof(P)*(N+1)); T=malloc(sizeof(P)*(N+1));
  int sz=1; while(sz<4*(N+1))sz<<=1; HM=sz-1; tab=calloc(sz,8); tabv=calloc(sz,4); tabi=calloc(sz,4);
  // initial walk: armchair zigzag (bits 1010...), the straightest a bee can fly.
  // start 1 (a=1,b=0: 1-0=1 ok). steps alternate units 1 and -w^2 ... just use a greedy straight zigzag
  P u[6]={{1,0},{0,1},{-1,-1},{-1,0},{0,-1},{1,1}}; // 1, w, w^2, -1, -w, -w^2  (w^2=-1-w)
  W[0]=(P){1,0};
  for(int i=1;i<=N;i++){ // try units in an order preferring +x drift
    int order[6]={0,5,1,4,2,3}; for(int k=0;k<6;k++){P q={W[i-1].a+u[order[k]].a,W[i-1].b+u[order[k]].b};
      if(((q.a+q.b)%3+3)%3==0) continue; int ok=1; for(int j=(i>4?i-4:0);j<i;j++) if(W[j].a==q.a&&W[j].b==q.b) ok=0; if(ok){W[i]=q;break;}}
  }
  long long acc=0;
  stamp++; for(int i=0;i<=N;i++) ins(W[i],i);
  for(long long it=0;it<iters;it++){
    int k=1+rnd()%(N-1); int g=1+rnd()%5; P v=W[k]; int ok=1;
    if(k>N/2){ for(int i=k+1;i<=N;i++){T[i]=apply(g,v,W[i]); int j=idx(T[i]); if(j>=0&&j<=k){ok=0;break;}}
      if(ok){ /* self-collisions within the moved tail are impossible (isometry) */ memcpy(W+k+1,T+k+1,sizeof(P)*(N-k)); } }
    else { for(int i=k-1;i>=0;i--){T[i]=apply(g,v,W[i]); int j=idx(T[i]); if(j>=k){ok=0;break;}}
      if(ok){ memcpy(W,T,sizeof(P)*k); } }
    if(ok){ acc++; stamp++; if(stamp==0x7fffffff){memset(tabv,0,sizeof(int)*sz);stamp=1;} for(int i=0;i<=N;i++) ins(W[i],i); }
  }
  fprintf(stderr,"acc %.4f\n",(double)acc/iters);
  for(int i=0;i<=N;i++) printf("%d %d\n",W[i].a,W[i].b);
}
