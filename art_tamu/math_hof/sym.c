#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
int main(){ int K=28; int64_t N=1LL<<K;
  int32_t *c=malloc((N+1)*4),*a=malloc((N+1)*4);
  c[1]=c[2]=1;a[1]=a[2]=1;
  for(int64_t n=3;n<=N;n++){c[n]=c[c[n-1]]+c[n-c[n-1]]; a[n]=n-a[a[n-1]]-a[n-a[n-1]];}
  for(int k=1;k<K;k++){ int64_t lo=1LL<<k, hi=lo<<1; int64_t asym=0, bminfail=0, bmin_eq=0, Asymm=0, slackR=INT64_MAX;
    for(int64_t x=0;x<=lo;x++){ int64_t n=lo+x, m=hi-x;
      int64_t b1=llabs(2LL*a[n]-n), b2=llabs(2LL*a[m]-m);
      if(b1!=b2) asym++;
      int64_t A1=2LL*c[n]-n, A2=2LL*c[m]-m; int64_t mn=A1<A2?A1:A2;
      if(b1>mn) bminfail++; if(b1==mn) bmin_eq++; if(A1==A2) Asymm++;
      if(mn-b1<slackR) slackR=mn-b1;
    }
    printf("k=%d beta_asym=%lld  beta>min(A,RA): %lld  beta==min: %lld  A==RA: %lld\n",k,(long long)asym,(long long)bminfail,(long long)bmin_eq,(long long)Asymm);
  }
}
