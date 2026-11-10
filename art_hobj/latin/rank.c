// Rank census of reduced Latin squares of order n (symbols 1..n, rank over Q via mod-p elimination).
// Rank is invariant under row/column permutations, so reduced squares cover every Latin square.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#define P 1000000007LL
int n; int L[8][8]; int rowm[8], colm[8]; long long hist[9], tot; int minr=99; long long saved=0;
static long long pw(long long a,long long e){ long long r=1; a%=P; while(e){ if(e&1) r=r*a%P; a=a*a%P; e>>=1;} return r; }
static int rnk(void){ long long A[8][8]; for(int i=0;i<n;i++)for(int j=0;j<n;j++)A[i][j]=L[i][j];
  int r=0; for(int c=0;c<n&&r<n;c++){ int p=-1; for(int i=r;i<n;i++) if(A[i][c]){p=i;break;} if(p<0) continue;
    for(int j=0;j<n;j++){ long long t=A[p][j];A[p][j]=A[r][j];A[r][j]=t; }
    long long inv=pw(A[r][c],P-2);
    for(int i=r+1;i<n;i++) if(A[i][c]){ long long f=A[i][c]*inv%P; for(int j=c;j<n;j++) A[i][j]=((A[i][j]-f*A[r][j])%P+P)%P; }
    r++; } return r; }
static void rec(int pos){
  if(pos==n*n){ int r=rnk(); hist[r]++; tot++; if(r<minr){minr=r;} if(r<=minr && saved<5000){ printf("%d:",r); for(int i=0;i<n;i++)for(int j=0;j<n;j++)printf("%d",L[i][j]); printf("\n"); saved++; } return; }
  int i=pos/n,j=pos%n; if(i==0||j==0){ rec(pos+1); return; }
  for(int s=1;s<=n;s++){ if(rowm[i]>>s&1 || colm[j]>>s&1) continue; L[i][j]=s; rowm[i]|=1<<s; colm[j]|=1<<s; rec(pos+1); rowm[i]&=~(1<<s); colm[j]&=~(1<<s); }
}
int main(int c,char**v){ n=atoi(v[1]); for(int i=0;i<n;i++){ L[0][i]=i+1; L[i][0]=i+1; }
  for(int i=0;i<n;i++){ rowm[i]=1<<(i+1); colm[i]=1<<(i+1); } rowm[0]=colm[0]=0; for(int i=0;i<n;i++){rowm[0]|=1<<(i+1);colm[0]|=1<<(i+1);}
  // row 0 full, col 0 full; rows i>0 have L[i][0]=i+1; cols j>0 have L[0][j]=j+1
  for(int i=1;i<n;i++){ rowm[i]=1<<(i+1); colm[i]=1<<(i+1); }
  rec(0); fprintf(stderr,"n=%d reduced=%lld min rank=%d\n",n,tot,minr); for(int r=0;r<=n;r++) if(hist[r]) fprintf(stderr,"  rank %d: %lld\n",r,hist[r]); return 0; }
