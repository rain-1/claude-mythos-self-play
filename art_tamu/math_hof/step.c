#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
int main(int argc,char**argv){
  int K=atoi(argv[1]); int64_t N=1LL<<K;
  int32_t *c=malloc((N+2)*4),*a=malloc((N+2)*4);
  c[1]=c[2]=1;a[1]=a[2]=1;
  for(int64_t n=3;n<=N;n++){c[n]=c[c[n-1]]+c[n-c[n-1]]; a[n]=n-a[a[n-1]]-a[n-a[n-1]];}
  int64_t naive=0, tight=0; 
  // naive: c(n) >= c(x)+c(n-x), x = a(n-1)
  for(int64_t n=3;n<=N;n++){ int64_t x=a[n-1]; int64_t v=(int64_t)c[x]+c[n-x];
    if(v>c[n]){naive++; if(naive<10) printf("naive fail n=%lld\n",(long long)n);} if(v==c[n]) tight++; }
  printf("K=%d naive fails %lld, tight %lld\n",K,(long long)naive,(long long)tight);
  // stronger candidate lemma: for all x between g-split and c-split ... measure first failures of 'max over x in [n-c(n-1), c(n-1)] of c(x)+c(n-x) <= c(n)'
  int64_t f2=0; int64_t f3=0;
  for(int64_t n=3;n<=N;n++){ int64_t p=c[n-1]; int64_t lo=n-p, hi=p; if(lo>hi){int64_t t=lo;lo=hi;hi=t;}
     int64_t mx=0; for(int64_t x=lo;x<=hi;x++){int64_t v=(int64_t)c[x]+c[n-x]; if(v>mx)mx=v;}
     if(mx>c[n]) f2++;
  }
  printf("max-on-[n-c(n-1),c(n-1)] fails %lld\n",(long long)f2);
}
