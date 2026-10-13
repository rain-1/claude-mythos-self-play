#include <stdio.h>
#include <stdlib.h>
int k,n,w[64];
int symm(int*a,int L){ if(L<=1) return 0; for(int d=1;d<L;d++){ if(L%d) continue; int ok=1; for(int i=0;i<L;i++) if(a[i]!=a[(i+d)%L]){ok=0;break;} if(ok) return 1;} return 0;}
int main(int argc,char**argv){k=atoi(argv[1]);n=atoi(argv[2]);
 long long tot=1; for(int i=1;i<n;i++) tot*=k; long long cnt=0;
 for(long long t=0;t<tot;t++){ long long x=t; w[0]=0; int used=1; for(int i=1;i<n;i++){w[i]=x%k;x/=k; used|=1<<w[i];}
  if(used!=(1<<k)-1) continue; if(symm(w,n)) continue; int ok=1;
  for(int c=0;c<k&&ok;c++){ int b[64],L=0; for(int i=0;i<n;i++) if(w[i]!=c) b[L++]=w[i]; if(!symm(b,L)) ok=0;}
  if(ok){cnt++; if(cnt<=3){for(int i=0;i<n;i++) putchar('A'+w[i]); putchar('\n');}}
 } printf("k=%d n=%d count(w0=A)=%lld\n",k,n,cnt);}
