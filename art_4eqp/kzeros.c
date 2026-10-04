// kzeros.c — exhaustive search for zeros of C_k((1-x)^A (1+x)^B) = binary Krawtchouk K_k(A; N), N=A+B,
// in the fundamental region 1<=A<=k<=N/2 (MO 515696), modulo two 31-bit primes; prints (N,A,k) with min(A,N-2k)>=MINM.
// usage: kzeros Nlo Nhi MINM
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef int64_t i64;
static const i64 P[2]={2147483629LL,2147483587LL};
static i64 pw(i64 a,i64 e,i64 p){i64 r=1;a%=p;while(e){if(e&1)r=r*a%p;a=a*a%p;e>>=1;}return r;}
int main(int c,char**v){
  int lo=atoi(v[1]),hi=atoi(v[2]),minm=atoi(v[3]);
  i64 *inv[2];
  for(int t=0;t<2;t++){inv[t]=malloc(sizeof(i64)*(hi+2));for(int i=1;i<=hi+1;i++)inv[t][i]=pw(i,P[t]-2,P[t]);}
  #pragma omp parallel for schedule(dynamic,1)
  for(int N=hi;N>=lo;N--){
    for(int A=1;2*A<=N;A++){
      i64 km[2],k0[2],k1[2];
      for(int t=0;t<2;t++){km[t]=0;k0[t]=1;}           // K_{-1}=0, K_0=1
      for(int k=0;2*(k+1)<=N;k++){
        for(int t=0;t<2;t++){ i64 p=P[t];
          i64 a=((i64)(N-2*A)%p+p)%p*k0[t]%p, b=(i64)(N-k+1)%p*km[t]%p;
          k1[t]=((a-b)%p+p)%p*inv[t][k+1]%p; km[t]=k0[t]; k0[t]=k1[t]; }
        int kk=k+1;
        if(k0[0]==0&&k0[1]==0&&kk>=A){int m=A<N-2*kk?A:N-2*kk; if(m>=minm){
          #pragma omp critical
          {printf("%d %d %d %d\n",N,A,kk,m);fflush(stdout);} }}
      }
    }
  }
}
