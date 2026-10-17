// Basins of the 3n-1 map on odd integers: reduced T(n) = (3n-1)/2^v.
// Cycles: {1}, {5,7}, {17,25,37,55,41,61,91}.  Labels 1,2,3 ; table over odd n < N.
// Output: basin.u8 (label per odd n, index n>>1), and counts per log-bin.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef unsigned __int128 u128;
int main(int argc,char**argv){
  uint64_t N = strtoull(argv[1],0,10);   // exclusive bound, power of 2
  uint64_t M = N/2;
  uint8_t *L = calloc(M,1);
  L[0]=1; L[2]=2; L[3]=2;               // 1,5,7
  uint64_t c17[7]={17,25,37,55,41,61,91};
  for(int i=0;i<7;i++) L[c17[i]>>1]=3;
  for(uint64_t i=1;i<M;i++){
    if(L[i]) continue;
    uint64_t n0=2*i+1; u128 n=n0; int lab=0;
    for(int s=0;s<100000;s++){
      n = 3*n-1; while(!(n&1)) n>>=1;
      if(n<n0){ lab=L[(uint64_t)n>>1]; break; }
      if(n<N && L[(uint64_t)n>>1]){ lab=L[(uint64_t)n>>1]; break; }
    }
    if(!lab){ fprintf(stderr,"unresolved %llu\n",(unsigned long long)n0); lab=0; }
    L[i]=lab;
  }
  FILE*f=fopen("basin.u8","wb"); fwrite(L,1,M,f); fclose(f);
  uint64_t c[4]={0}; for(uint64_t i=0;i<M;i++) c[L[i]]++;
  printf("N=%llu  p1=%.6f p5=%.6f p17=%.6f unres=%llu\n",(unsigned long long)N,
   (double)c[1]/M,(double)c[2]/M,(double)c[3]/M,(unsigned long long)c[0]);
}
