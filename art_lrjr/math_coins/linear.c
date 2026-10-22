/* For each n, test all linear q(j)=a*j+b mod n; report which a work (for which b) and compare with gcd(a(a^2-1),n)==1 */
#include <stdio.h>
#include <stdlib.h>
int gcd(int a,int b){while(b){int t=a%b;a=b;b=t;}return a;}
int n; int q[200]; int hs[400][200], hd[400][200];
int incr(){ for(int d=0;d<2*n-1;d++)for(int v=0;v<n;v++)hs[d][v]=hd[d][v]=0;
  for(int i=0;i<n;i++)for(int j=0;j<n;j++){int v=(i+q[j])%n; hs[i+j][v]++; hd[i-j+n-1][v]++;}
  for(int d=0;d<2*n-1;d++){int a=0,b=0;for(int k=0;k<n;k++){a+=hs[d][k];b+=hd[d][k]; if(a>k+1||b>k+1)return 0;}}
  return 1;}
int main(int c,char**v){int N=atoi(v[1]);
  for(n=1;n<=N;n++){int cnt=0,mism=0; printf("n=%d good a:",n);
    for(int a=0;a<n;a++){int nb=0; for(int b=0;b<n;b++){ if(gcd(a,n)!=1 && n>1){continue;} for(int j=0;j<n;j++)q[j]=(a*j+b)%n; if(incr())nb++;}
      int tor = (n==1) || (gcd(a,n)==1 && gcd((a+1)%n,n)==1 && gcd((a-1+n)%n,n)==1);
      if(nb){printf(" %d(%d b)",a,nb);cnt+=nb;}
      if((nb>0)!=tor || (nb>0 && nb!=n)) mism++;}
    printf("  total=%d mismatches_vs_toroidal=%d\n",cnt,mism);}
}
