// Exhaustive search for n=2^m-1 using proven structure:
//  sigma: (t mod 2^k) -> (a_t mod 2^k) is a well-defined bijection of Z/2^k for every k<=m-1;
//  a_q=q; {a_t,a_{t+q}}={j,j+q}. Even block lengths are then automatically fine; only odd L in [3,n-2] checked.
// Fill order 1,q-1,2,q-2,... (each step fixes positions t and t+q).
// usage: mers2 m [skipdiv] [outfile] [maxnodes]
#include <stdio.h>
#include <stdlib.h>
int n,m,q,skipdiv; int a[2100]; int used[2100]; long long cnt=0,nodes=0,maxnodes=0; FILE*out=NULL;
int skipL[2100]; int ord[2100];
int mp[12][2100], inv[12][2100], mc[12][2100]; // mc = refcount of assignment at level k residue
static inline int okL(long long s,int L){ if(L%2==0||L==n||L<2||skipL[L]) return 1; return s%L!=0; }
int checkpos(int t){ // all blocks containing t within known run
  int lo=t,hi=t; while(lo>1&&a[lo-1])lo--; while(hi<n&&a[hi+1])hi++;
  static long long P[2100]; P[lo-1]=0; for(int i=lo;i<=hi;i++)P[i]=P[i-1]+a[i];
  for(int i=lo;i<=t;i++) for(int j=(t>i+1?t:i+2);j<=hi;j+=1){ int L=j-i+1; if(L&1){ if(!okL(P[j]-P[i-1],L)) return 0;} }
  return 1;
}
int assign(int t,int v,int dir){ // dir=+1 add (returns 0 if inconsistent, no change), -1 remove
  if(dir>0){ for(int k=1;k<m;k++){int M=(1<<k)-1; int r=t&M, s=v&M; if(mp[k][r]>=0&&mp[k][r]!=s) return 0; if(inv[k][s]>=0&&inv[k][s]!=r) return 0;}
    for(int k=1;k<m;k++){int M=(1<<k)-1; int r=t&M,s=v&M; mp[k][r]=s; inv[k][s]=r; mc[k][r]++;} return 1; }
  for(int k=1;k<m;k++){int M=(1<<k)-1; int r=t&M; if(--mc[k][r]==0){ inv[k][mp[k][r]]=-1; mp[k][r]=-1; }} return 1;
}
void dfs(int d){
  if(maxnodes&&nodes>maxnodes) return;
  if(d==q-1){ cnt++; if(out){for(int i=1;i<=n;i++)fprintf(out,"%d%c",a[i],i==n?'\n':' '); fflush(out);} return; }
  int t=ord[d];
  for(int v=1;v<=n;v++){
    if(v==q||used[v]) continue; int w= v>q? v-q: v+q; if(used[w]) continue;
    if(!assign(t,v,1)) continue;
    nodes++;
    a[t]=v; a[t+q]=w;
    if(checkpos(t)&&checkpos(t+q)){ used[v]=used[w]=1; dfs(d+1); used[v]=used[w]=0; }
    a[t]=0; a[t+q]=0; assign(t,v,-1);
  }
}
int main(int c,char**argv){ m=atoi(argv[1]); n=(1<<m)-1; q=1<<(m-1); skipdiv=c>2?atoi(argv[2]):0; if(c>3&&argv[3][0]!='-') out=fopen(argv[3],"w"); if(c>4) maxnodes=atoll(argv[4]);
  for(int L=2;L<n;L++) skipL[L]= (skipdiv==1) && (n%L==0);
  if(c>2 && argv[2][0]=='s'){ char*p=argv[2]+1; while(*p){ int L=strtol(p,&p,10); if(L>0&&L<n) skipL[L]=1; if(*p==',')p++; else break; } }
  if(c>2 && argv[2][0]=='o'){ char*p=argv[2]+1; for(int L=2;L<n;L++) skipL[L]=1; while(*p){ int L=strtol(p,&p,10); if(L>0&&L<n) skipL[L]=0; if(*p==',')p++; else break; } }
  for(int k=0;k<12;k++)for(int r=0;r<2100;r++){mp[k][r]=inv[k][r]=-1;mc[k][r]=0;}
  a[q]=q; used[q]=1; assign(q,q,1);
  int d=0,lo=1,hi=q-1; while(lo<=hi){ ord[d++]=lo++; if(lo<=hi) ord[d++]=hi--; }
  dfs(0);
  printf("n=%d skipdiv=%d count=%lld nodes=%lld%s\n",n,skipdiv,cnt,nodes,(maxnodes&&nodes>maxnodes)?" (TRUNCATED)":""); if(out) fclose(out); return 0; }
