// Odd-step counts K for the 3n-1 map: K10 = odd steps until n < 2^10, Kc = odd steps until n hits a cycle.
// Samples odd n near 2^x (n in [2^x, 2^x*(1+2^-6)) ), x = 12..60 step 4.  Prints mean/var.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
typedef unsigned __int128 u128;
static uint64_t s[2]={0x9E3779B97F4A7C15ull,0xD1B54A32D192ED03ull};
static uint64_t rnd(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static int incyc(u128 n){ return n==1||n==5||n==7||n==17||n==25||n==37||n==55||n==41||n==61||n==91; }
int main(int argc,char**argv){
  int S=atoi(argv[1]);
  printf("# x  mean(K10) var(K10)  mean(Kc) var(Kc)  samples\n");
  for(int x=12;x<=60;x+=4){
    double a1=0,a2=0,b1=0,b2=0;
    for(int t=0;t<S;t++){
      u128 base=((u128)1)<<x; u128 off=(rnd()>>(64-(x-6>63?63:x-6)));
      u128 n=(base+off)|1; long k=0,k10=-1;
      while(!incyc(n)){ n=3*n-1; while(!(n&1)) n>>=1; k++; if(k10<0 && n<1024) k10=k; }
      if(k10<0) k10=0;
      a1+=k10; a2+=(double)k10*k10; b1+=k; b2+=(double)k*k;
    }
    a1/=S;a2/=S;b1/=S;b2/=S;
    printf("%d %.4f %.3f %.4f %.3f %d\n",x,a1,a2-a1*a1,b1,b2-b1*b1,S);
  }
}
