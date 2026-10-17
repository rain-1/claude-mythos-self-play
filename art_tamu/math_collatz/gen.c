// Generalized map T(n)=(3n+d)/2^v on odd n coprime to d, n < N. Labels basins by cycle (cycle id = order found).
// Output: per-octave-bin counts for the 4 largest... we output counts for cycle ids 1..8 (others lumped as 9) in B bins/octave.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
typedef unsigned __int128 u128;
static long gcd(long a,long b){while(b){long t=a%b;a=b;b=t;}return a;}
int main(int argc,char**argv){
  long d=atol(argv[1]); int LOG=atoi(argv[2]); int B=atoi(argv[3]);
  long N=1L<<LOG, M=N/2; uint8_t*L=calloc(M,1); int nc=0; long cmin[256];
  for(long i=0;i<M;i++){ long n0=2*i+1; if(gcd(n0,d)!=1) continue;
    u128 n=n0; int lab=0; u128 pw=1, lam=1, tort=n0;   /* Brent cycle detection */
    for(long s=0;s<10000000;s++){ n=3*n+d; while(!(n&1)) n>>=1;
      if(n<(u128)n0){ lab=L[(long)n>>1]; break; }
      if(n<(u128)N && L[(long)n>>1]){ lab=L[(long)n>>1]; break; }
      if(n==tort){ /* in a cycle: find its minimum */
        u128 m=n, t=n; do{ t=3*t+d; while(!(t&1)) t>>=1; if(t<m) m=t; }while(t!=n);
        int c; for(c=1;c<=nc;c++) if((u128)cmin[c]==m) break;
        if(c>nc){ nc++; cmin[nc]=(long)m; }
        lab=c<255?c:255; break; }
      if(pw==lam){ tort=n; pw*=2; lam=0; } lam++; }
    L[i]=lab; }
  fprintf(stderr,"d=%ld: %d cycles, mins:",d,nc); for(int c=1;c<=nc&&c<255;c++) fprintf(stderr," %ld",cmin[c]); fprintf(stderr,"\n");
  // counts per bin, labels 1..8 and 9=other
  int K=LOG; uint32_t*cnt=calloc((size_t)K*B*10,4);
  for(long i=0;i<M;i++){ if(!L[i]) continue; double x=log2(2.0*i+1); int k=(int)x; int b=(int)((x-k)*B); if(b>=B)b=B-1;
    int l=L[i]>8?9:L[i]; cnt[((size_t)k*B+b)*10+l]++; }
  char fn[64]; sprintf(fn,"gen_d%ld.u32",d); FILE*o=fopen(fn,"wb"); fwrite(cnt,4,(size_t)K*B*10,o); fclose(o);
}
