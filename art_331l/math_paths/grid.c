/* count simple paths between opposite corners of the m x m grid graph, with length histogram (edges) */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
static int M; static long long hist[64]; static uint64_t vis;
static void dfs(int r,int c,int len){
  if(r==M-1&&c==M-1){hist[len]++;return;}
  static const int dr[4]={1,-1,0,0},dc[4]={0,0,1,-1};
  for(int d=0;d<4;d++){int nr=r+dr[d],nc=c+dc[d];
    if(nr<0||nc<0||nr>=M||nc>=M) continue; int b=nr*M+nc;
    if(vis>>b&1) continue; vis|=1ULL<<b; dfs(nr,nc,len+1); vis&=~(1ULL<<b);}
}
int main(){
  printf("{");
  for(M=2;M<=6;M++){memset(hist,0,sizeof hist);vis=1;dfs(0,0,0);long long t=0;for(int i=0;i<64;i++)t+=hist[i];
    printf("%s\"%d\": {\"total\": %lld, \"length_hist\": {",M>2?", ":"",M,t);int f=1;
    for(int i=0;i<64;i++) if(hist[i]){printf("%s\"%d\": %lld",f?"":", ",i,hist[i]);f=0;}
    printf("}}");}
  printf("}\n");
}
