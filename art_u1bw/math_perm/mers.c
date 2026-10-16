// Structured exhaustive DFS for n=2^m-1 using the proven necessary 2-adic structure:
//  a_{t+2^k} = a_t (mod 2^k) for 2^k<n; residues of a_1..a_{2^k} mod 2^k distinct; a_q=q; {a_t,a_{t+q}}={j,j+q}.
// usage: mers m [skipdiv] [outfile]   skipdiv=1: ignore block lengths L dividing n (relaxed problem)
#include <stdio.h>
#include <stdlib.h>
int n,m,q,skipdiv; int a[600]; long long S[600],T[600]; int used[600]; long long cnt=0,nodes=0; FILE*out=NULL;
int skipL[600];
int resused[12][600]; // resused[k][r]
static int okblock(long long s,int L){ if(L==n||skipL[L]) return 1; return s%L!=0; }
void dfs(int t){
  if(t==q){ long long P[600]; P[0]=0; for(int i=1;i<=n;i++)P[i]=P[i-1]+a[i];
    for(int j=q;j<=n;j++) for(int i=1;i<=j;i++){ int L=j-i+1; if(L<2) continue; if(!okblock(P[j]-P[i-1],L)) return; }
    cnt++; if(out){for(int i=1;i<=n;i++)fprintf(out,"%d%c",a[i],i==n?'\n':' ');} return; }
  // largest k with 2^k < t
  int K=0; while((1<<(K+1))<t) K++;
  int step = (t>1)? (1<<K):1; int base = (t>1)? (a[t-step] % step) : 0;
  for(int v=(t>1? (base==0?step:base):1); v<=n; v+= (t>1?step:1)){
    if(v==q||used[v]) continue;
    int w = v>q? v-q : v+q;  // partner
    if(w<1||w>n||used[w]) continue;
    // residue distinctness for all k with t<=2^k<q... : for k where t <= 2^k, residues among first t distinct
    int bad=0;
    for(int k=1;(1<<k)<q;k++){ if(t<=(1<<k)){ if(resused[k][v&((1<<k)-1)]){bad=1;break;} } }
    if(bad) continue;
    nodes++;
    long long s=S[t-1]+v; int ok=1;
    for(int i=1;i<t;i++){ if(!okblock(s-S[i-1],t-i+1)){ok=0;break;} }
    if(!ok) continue;
    // right segment: positions q..q+t, T[j]=sum a_q..a_{q+j}
    long long tt=T[t-1]+w; // T index j=t
    for(int i=0;i<t;i++){ // block a_{q+i}..a_{q+t}, sum = tt - (i? T[i-1]:0)
      long long bs = tt - (i? T[i-1]:0); int L=t-i+1; if(!okblock(bs,L)){ok=0;break;} }
    if(!ok) continue;
    used[v]=used[w]=1; a[t]=v; a[t+q]=w; S[t]=s; T[t]=tt;
    for(int k=1;(1<<k)<q;k++) if(t<=(1<<k)) resused[k][v&((1<<k)-1)]=1;
    dfs(t+1);
    for(int k=1;(1<<k)<q;k++) if(t<=(1<<k)) resused[k][v&((1<<k)-1)]=0;
    used[v]=used[w]=0;
  }
}
int main(int c,char**argv){ m=atoi(argv[1]); n=(1<<m)-1; q=1<<(m-1); skipdiv=c>2?atoi(argv[2]):0; if(c>3) out=fopen(argv[3],"w");
  for(int L=2;L<n;L++) skipL[L]= skipdiv && (n%L==0);
  a[q]=q; used[q]=1; S[0]=0; T[0]=q; // T[0]=a_q
  // also the right segment starting at q.. needs a_q block checks handled in loop
  dfs(1);
  // final full check of all blocks for found perms is done separately
  printf("n=%d skipdiv=%d count=%lld nodes=%lld\n",n,skipdiv,cnt,nodes); if(out) fclose(out); return 0; }
