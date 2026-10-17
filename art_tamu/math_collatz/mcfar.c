// Out-of-sample test far beyond the table: sample odd n with log2 n uniform in [a,a+1), find basin by iteration,
// output complex Fourier coefficients c_{j,q} = mean((1[basin=j]-pbar_j) e^{-2 pi i q log2 n}) for given q's.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
typedef unsigned __int128 u128;
static uint64_t s[2]={0x123456789abcdefull,0xfedcba9876543210ull};
static uint64_t rnd(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static int lab(u128 n){ for(;;){ if(n==1) return 1; if(n==5||n==7) return 2;
  if(n==17||n==25||n==37||n==55||n==41||n==61||n==91) return 3; n=3*n-1; while(!(n&1)) n>>=1; } }
int main(int argc,char**argv){
  int a=atoi(argv[1]); long S=atol(argv[2]); int nq=argc-3; double q[16]; for(int i=0;i<nq;i++) q[i]=atof(argv[3+i]);
  double cnt[4]={0}, re[16][4]={{0}}, im[16][4]={{0}}, sre[16]={0}, sim[16]={0};
  for(long t=0;t<S;t++){
    long double u=(rnd()>>11)*(1.0L/9007199254740992.0L); long double v=powl(2.0L,a+u);
    u128 n=(u128)v; n|=1; double x=(double)(a+u);
    int L=lab(n); cnt[L]++;
    for(int i=0;i<nq;i++){ double ph=-2*M_PI*q[i]*x; double c=cos(ph),si=sin(ph); re[i][L]+=c; im[i][L]+=si; sre[i]+=c; sim[i]+=si; }
  }
  for(int i=0;i<nq;i++){ printf("%d %g",a,q[i]);
    for(int j=1;j<=3;j++){ double p=cnt[j]/S; printf("  %.6f %.6f",(re[i][j]-p*sre[i])/S,(im[i][j]-p*sim[i])/S); }
    printf("\n"); }
  fprintf(stderr,"a=%d p=%.5f %.5f %.5f\n",a,cnt[1]/S,cnt[2]/S,cnt[3]/S);
}
