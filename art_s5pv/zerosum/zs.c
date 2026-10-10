// enumerate subsets of U (629 modular reciprocals mod p^3) of size 4..7 with zero sum
// meet in the middle: hash of all triples (key = sum mod M), canonical split = smallest elements first
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#define N 629
static const uint64_t M=1179926954263ULL;
static uint64_t r[N];
#define HB 26
#define HS (1ULL<<HB)
static uint64_t *hk; static uint32_t *hv;
static inline uint64_t hsh(uint64_t k){k^=k>>29;k*=0xbf58476d1ce4e5b9ULL;k^=k>>32;return k&(HS-1);}
static void ins(uint64_t k,uint32_t v){uint64_t h=hsh(k);while(hv[h]!=0xffffffffu)h=(h+1)&(HS-1);hk[h]=k;hv[h]=v;}
static inline uint32_t pk(int a,int b,int c){return (uint32_t)a|((uint32_t)b<<10)|((uint32_t)c<<20);}
int main(){
  FILE*f=fopen("res.txt","r");for(int i=0;i<N;i++)fscanf(f,"%lu",&r[i]);fclose(f);
  hk=malloc(HS*8);hv=malloc(HS*4);memset(hv,0xff,HS*4);
  long nt=0;
  for(int a=0;a<N;a++)for(int b=a+1;b<N;b++)for(int c=b+1;c<N;c++){ins((r[a]+r[b]+r[c])%M,pk(a,b,c));nt++;}
  fprintf(stderr,"triples %ld\n",nt);
  FILE*o=fopen("sets.txt","w");
  // size 4,5 : pair (+) with smallest elements in triple-table? do size5 = triple(smallest3)+pair(largest2); size4 brute via pair+pair
  long cnt[9]={0};
  // size 4: pairs hash via direct check against triple table not possible; brute pairs-of-pairs with sorting
  { long np=(long)N*(N-1)/2; uint64_t *ps=malloc(np*8);uint32_t*pi=malloc(np*4);long k=0;
    for(int a=0;a<N;a++)for(int b=a+1;b<N;b++){ps[k]=(r[a]+r[b])%M;pi[k]=a|(b<<10);k++;}
    for(long i=0;i<np;i++)for(long j=i+1;j<np;j++){} // placeholder (skip; too slow) 
    free(ps);free(pi);}
  // size 5: triple(a<b<c) + pair(d<e), c<d
  for(int d=0;d<N;d++)for(int e=d+1;e<N;e++){uint64_t need=(2*M-(r[d]+r[e])%M)%M;uint64_t h=hsh(need);
    while(hv[h]!=0xffffffffu){if(hk[h]==need){uint32_t v=hv[h];int c=v>>20;if(c<d){fprintf(o,"5 %d %d %d %d %d\n",v&1023,(v>>10)&1023,c,d,e);cnt[5]++;}}h=(h+1)&(HS-1);}}
  fprintf(stderr,"size5 %ld\n",cnt[5]);
  // size 6: triple + triple
  for(int d=0;d<N;d++)for(int e=d+1;e<N;e++)for(int g=e+1;g<N;g++){uint64_t need=(3*M-(r[d]+r[e]+r[g])%M)%M;uint64_t h=hsh(need);
    while(hv[h]!=0xffffffffu){if(hk[h]==need){uint32_t v=hv[h];int c=v>>20;if(c<d){fprintf(o,"6 %d %d %d %d %d %d\n",v&1023,(v>>10)&1023,c,d,e,g);cnt[6]++;}}h=(h+1)&(HS-1);}}
  fprintf(stderr,"size6 %ld\n",cnt[6]);fflush(o);
  // size 7: triple + quad
  #pragma omp parallel for schedule(dynamic,1)
  for(int d=0;d<N;d++){char buf[256];
    for(int e=d+1;e<N;e++)for(int g=e+1;g<N;g++){uint64_t s3=r[d]+r[e]+r[g];
     for(int q=g+1;q<N;q++){uint64_t need=(4*M-(s3+r[q])%M)%M;uint64_t h=hsh(need);
      while(hv[h]!=0xffffffffu){if(hk[h]==need){uint32_t v=hv[h];int c=v>>20;if(c<d){
        #pragma omp critical
        {fprintf(o,"7 %d %d %d %d %d %d %d\n",v&1023,(v>>10)&1023,c,d,e,g,q);cnt[7]++;}}}h=(h+1)&(HS-1);}}}
    if(d%50==0)fprintf(stderr,"d=%d size7 so far %ld\n",d,cnt[7]);}
  fprintf(stderr,"size7 %ld\n",cnt[7]);fclose(o);
}
