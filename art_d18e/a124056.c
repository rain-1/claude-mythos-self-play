// A124056: a1=1, a_{n+1} = #{i<=n : a_i | a_n}. Records positions of 3s, max value, primes.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#define MAXV 200000000
static uint32_t *cnt, *spf;
int main(int argc,char**argv){
  long N=atol(argv[1]);
  cnt=calloc(MAXV,4); spf=calloc(MAXV,4);
  for(long i=2;i<MAXV;i++) if(!spf[i]) for(long j=i;j<MAXV;j+=i) if(!spf[j]) spf[j]=i;
  FILE*f=fopen("a124056.bin","wb");
  uint32_t a=1; long n3=0; uint32_t mx=0;
  for(long n=1;n<=N;n++){
    fwrite(&a,4,1,f);
    cnt[a]++;
    if(a==3){n3++; if(n3<60|| (n3%1000==0)) printf("3 #%ld at n=%ld\n",n3,n);}
    if(a>mx){mx=a;}
    // divisors of a
    uint32_t p[32],e[32];int k=0;uint32_t x=a;
    while(x>1){uint32_t q=spf[x];int ee=0;while(x%q==0){x/=q;ee++;}p[k]=q;e[k]=ee;k++;}
    // enumerate
    static uint32_t dv[20000];int nd=1;dv[0]=1;
    for(int i=0;i<k;i++){int m=nd;uint32_t pw=1;for(int t=1;t<=e[i];t++){pw*=p[i];for(int j=0;j<m;j++)dv[nd++]=dv[j]*pw;}}
    uint64_t s=0;for(int j=0;j<nd;j++)s+=cnt[dv[j]];
    if(s>=MAXV){printf("overflow at n=%ld\n",n);break;}
    a=(uint32_t)s;
    if((n&(n-1))==0) printf("n=%ld a=%u max=%u threes=%ld\n",n,a,mx,n3);
  }
  fclose(f);printf("done max=%u threes=%ld\n",mx,n3);
}
