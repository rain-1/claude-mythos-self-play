#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
// test: for all x in [ceil((n-1)/2), c(n-1)+1], c(x)+c(n-x) <= c(n)
// also verify g recurrence derived
int main(int argc,char**argv){
  int K=atoi(argv[1]); int64_t N=1LL<<K;
  int32_t *c=malloc((N+2)*4),*a=malloc((N+2)*4),*g=malloc((N+2)*4);
  c[1]=c[2]=1;a[1]=a[2]=1;
  for(int64_t n=3;n<=N;n++){c[n]=c[c[n-1]]+c[n-c[n-1]]; a[n]=n-a[a[n-1]]-a[n-a[n-1]];}
  for(int64_t n=1;n<=N;n++){int k=63-__builtin_clzll(n); g[n]=(k%2==0)?a[n]:n-a[n];}
  int64_t bad=0,badrec=0, badhi=0, badlo=0; int64_t first=-1;
  for(int64_t n=3;n<=N;n++){
    int k=63-__builtin_clzll(n);
    int64_t x1=g[n-1]; int64_t gr = (k%2==0)? (int64_t)g[x1]+g[n-x1] : (int64_t)g[x1+1]+g[n-1-x1];
    if(n>4 && gr!=g[n]) {badrec++; if(badrec<5)printf("rec fail n=%lld\n",(long long)n);}
    int64_t lo=n/2; int64_t hi=c[n-1]+1; // lo=floor(n/2) <= ceil((n-1)/2)
    for(int64_t x=lo;x<=hi && x<n;x++){ if((int64_t)c[x]+c[n-x]>c[n]){bad++; if(bad<10)printf("lemma fail n=%lld x=%lld c(n-1)=%d\n",(long long)n,(long long)x,c[n-1]);}}
  }
  printf("K=%d recfail=%lld lemmafail=%lld\n",K,(long long)badrec,(long long)bad);
}
