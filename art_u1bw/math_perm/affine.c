// test a_t = (alpha*t + beta[t mod 2]) mod 2^m  (values must be a permutation of 1..n, n=2^m-1), report good ones
// and report for each, the failing blocks summary
#include <stdio.h>
#include <stdlib.h>
int main(int c,char**v){ int m=atoi(v[1]); int N=1<<m, n=N-1; int a[4200]; long long P[4200]; int seen[4200];
 long long tested=0,good=0;
 for(int al=1;al<N;al+=2) for(int b0=0;b0<N;b0++) for(int b1=0;b1<N;b1++){
   int ok=1; for(int i=0;i<N;i++)seen[i]=0;
   for(int t=1;t<=n;t++){ int x=((long long)al*t + (t&1?b1:b0))%N; if(x==0||seen[x]){ok=0;break;} seen[x]=1; a[t]=x; }
   if(!ok) continue; tested++;
   P[0]=0; for(int t=1;t<=n;t++)P[t]=P[t-1]+a[t];
   int nf=0, fi=0,fj=0;
   for(int L=2;L<n&&nf==0;L++) for(int i=1;i+L-1<=n;i++) if((P[i+L-1]-P[i-1])%L==0){nf++;fi=i;fj=L;break;}
   if(!nf){ good++; if(good<=8){ printf("GOOD alpha=%d b0=%d b1=%d :",al,b0,b1); for(int t=1;t<=n&&t<=12;t++)printf(" %d",a[t]); printf(" ...\n"); } }
 }
 printf("m=%d n=%d bijective-candidates=%lld good=%lld\n",m,n,tested,good); }
