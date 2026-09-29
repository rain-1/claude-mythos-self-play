// bee.c — count k-bit bee numbers b_k exactly (self-avoiding walks on the honeycomb
// with a fixed first edge; each later bit = turn left(1)/right(0)).
// Honeycomb as brick-wall lattice: vertex (x,y); every vertex has horizontal
// neighbours x±1, and a vertical neighbour y+1 if (x+y) even else y-1.
// Headings: we track the walk as vertices; left/right turn determined by geometry.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define L 128
#define MAXK 64
static unsigned char vis[2*L][2*L];
static long long cnt[MAXK+1];
static int K;
// neighbours of (x,y) in cyclic (counter-clockwise) order, in real hex geometry.
// brick wall: even site (x+y even) has up-neighbour; odd has down-neighbour.
// Embedding: even site neighbours: E(x+1), W(x-1), N(y+1) at angles 330?,...
// Simpler: treat turn relation by cyclic order of the 3 neighbours around a vertex.
// Even vertex (has N): ccw order: E, N, W.  Odd vertex (has S): ccw order: W, S, E.
static int nb(int x,int y,int i,int *nx,int *ny){
  int even=((x+y)&1)==0;
  if(even){ if(i==0){*nx=x+1;*ny=y;} else if(i==1){*nx=x;*ny=y+1;} else {*nx=x-1;*ny=y;} }
  else    { if(i==0){*nx=x-1;*ny=y;} else if(i==1){*nx=x;*ny=y-1;} else {*nx=x+1;*ny=y;} }
  return 0;
}
static int idx_of(int x,int y,int px,int py){ for(int i=0;i<3;i++){int a,b;nb(x,y,i,&a,&b); if(a==px&&b==py) return i;} return -1; }
static void dfs(int x,int y,int px,int py,int depth){
  cnt[depth]++;
  if(depth==K) return;
  int j=idx_of(x,y,px,py);
  for(int t=1;t<=2;t++){ // t=1: next ccw after incoming, t=2: the other
    int a,b; nb(x,y,(j+t)%3,&a,&b);
    if(vis[a+L][b+L]) continue;
    vis[a+L][b+L]=1; dfs(a,b,x,y,depth+1); vis[a+L][b+L]=0;
  }
}
int main(int argc,char**argv){
  K=atoi(argv[1]);
  vis[L][L]=1; vis[L+1][L]=1; // start at (0,0) even, first edge to E (1,0)
  dfs(1,0,0,0,1);
  for(int k=1;k<=K;k++) printf("%d %lld\n",k,cnt[k]);
}
