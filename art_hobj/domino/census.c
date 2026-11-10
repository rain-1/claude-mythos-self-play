// Census of domino tilings of the n x n board by the longest domino-respecting path.
// A domino-respecting path enters a domino at one cell and must leave from the other;
// by the chessboard colouring every exit cell has the same colour, so the path is a
// directed simple path in the digraph  D -> D'  iff  white(D) is adjacent to black(D').
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
int n, N, ND;
int owner[64];            // domino id of each cell
int wcell[32], bcell[32];
int nout[32], out[32][3];
uint64_t outmask[32];
long long hist[40], ntil=0;
int best, target; long long nodes, nodecap;
int minbest=99; int savemin[64]; long long nmin=0;
// FAST=1: stop each search at min+1 (the histogram then only separates "== min" from "> min")
int cap_hit=0; int FAST=0; long long PROG=100000; int PM=1, PK=0; long long pref=0;
uint64_t inmask[32];
static int reach(int v, uint64_t vis){ // number of dominoes reachable from v avoiding vis (upper bound on the gain)
  uint64_t seen = (1ULL<<v), fr = seen;
  while(fr){ int u=__builtin_ctzll(fr); fr&=fr-1; uint64_t nx=outmask[u]&~vis&~seen; seen|=nx; fr|=nx; }
  return __builtin_popcountll(seen)-1;
}
static void dfs(int v, uint64_t vis, int len){
  if(len>best) best=len;
  if(best>=target) return;
  nodes++;
  if(len + reach(v,vis) <= best) return;
  for(int k=0;k<nout[v];k++){ int u=out[v][k]; if(vis>>u&1) continue; dfs(u, vis|(1ULL<<u), len+1); if(best>=target) return; }
}
static int longest(void){
  for(int d=0;d<ND;d++){ nout[d]=0; outmask[d]=0; inmask[d]=0; }
  for(int d=0;d<ND;d++){ int w=wcell[d], r=w/n, c=w%n;
    int nb[4]={ r>0?w-n:-1, r<n-1?w+n:-1, c>0?w-1:-1, c<n-1?w+1:-1 };
    for(int k=0;k<4;k++) if(nb[k]>=0 && owner[nb[k]]!=d){ out[d][nout[d]++]=owner[nb[k]]; outmask[d]|=1ULL<<owner[nb[k]]; inmask[owner[nb[k]]]|=1ULL<<d; } }
  best=0; target=(FAST && minbest+1<ND)?minbest+1:ND; nodes=0;
  for(int s=0;s<ND && best<target;s++) dfs(s, 1ULL<<s, 1);
  return best;
}
static void rec(int pos, int nd){
  while(pos<N && owner[pos]>=0) pos++;
  if(pos==N){ int L=longest(); hist[L]++; ntil++; if(ntil%PROG==0){ fprintf(stderr,"%lld min %d\n",ntil,minbest); fflush(stderr);} 
    if(L<minbest){ minbest=L; nmin=0; }
    if(L==minbest){ if(nmin<200000){ fwrite(owner,sizeof(int),N,stdout);} nmin++; }
    return; }
  if(nd==6 && n==8){ if((pref++)%PM!=PK) return; }
  int r=pos/n,c=pos%n;
  int cells[2][2]={{pos,pos+1},{pos,pos+n}};
  for(int o=0;o<2;o++){
    if(o==0 && (c==n-1 || owner[pos+1]>=0)) continue;
    if(o==1 && r==n-1) continue;
    int a=cells[o][0], b=cells[o][1];
    owner[a]=owner[b]=nd;
    int ra=a/n, ca=a%n;
    if((ra+ca)&1){ wcell[nd]=a; bcell[nd]=b; } else { wcell[nd]=b; bcell[nd]=a; }
    rec(pos+1, nd+1);
    owner[a]=owner[b]=-1;
  }
}
int main(int argc,char**argv){ n=atoi(argv[1]); if(argc>3){ PM=atoi(argv[2]); PK=atoi(argv[3]); } if(argc>4) PROG=atoll(argv[4]); if(argc>5) FAST=atoi(argv[5]); N=n*n; ND=N/2; memset(owner,-1,sizeof owner);
  rec(0,0);
  fprintf(stderr,"n=%d tilings=%lld min longest=%d (count %lld)\n",n,ntil,minbest,nmin);
  for(int i=0;i<=ND;i++) if(hist[i]) fprintf(stderr,"  L=%d: %lld\n",i,hist[i]);
  return 0; }
