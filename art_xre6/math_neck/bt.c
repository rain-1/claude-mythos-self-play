// backtracking search for precarious necklaces with fixed counts and deletion primes
// usage: bt k n c0..c{k-1} p0..p{k-1} [maxsol]
#include <stdio.h>
#include <stdlib.h>
int k,n,cnt[8],need[8],P[8],per[8];
int w[256];
int seq[8][256], len[8];
long long nsol=0, maxsol=1000000, nodes=0;
int periodic_full(){
  // check whether w is rotationally symmetric
  for(int d=1; d<n; d++){ if(n%d) continue; int ok=1; for(int i=0;i<n;i++) if(w[i]!=w[(i+d)%n]){ok=0;break;} if(ok) return 1;}
  return 0;
}
void rec(int i){
  nodes++;
  if(i==n){
    if(!periodic_full()){ nsol++; for(int j=0;j<n;j++) putchar('A'+w[j]); putchar('\n'); if(nsol>=maxsol){fflush(stdout); exit(0);} }
    return;
  }
  for(int x=0;x<k;x++){
    if(i==0 && x!=0) continue;
    if(cnt[x]>=need[x]) continue;
    int ok=1;
    for(int c=0;c<k;c++){ if(c==x) continue; if(len[c]>=per[c] && seq[c][len[c]-per[c]]!=x){ok=0;break;} }
    if(!ok) continue;
    // remaining feasibility: fine
    w[i]=x; cnt[x]++;
    for(int c=0;c<k;c++) if(c!=x) seq[c][len[c]++]=x;
    rec(i+1);
    for(int c=0;c<k;c++) if(c!=x) len[c]--;
    cnt[x]--;
  }
}
int main(int argc,char**argv){
  k=atoi(argv[1]); n=atoi(argv[2]);
  for(int c=0;c<k;c++) need[c]=atoi(argv[3+c]);
  for(int c=0;c<k;c++){ P[c]=atoi(argv[3+k+c]); per[c]=(n-need[c])/P[c]; }
  if(argc>3+2*k) maxsol=atoll(argv[3+2*k]);
  rec(0);
  fprintf(stderr,"nsol=%lld nodes=%lld\n",nsol,nodes);
}
