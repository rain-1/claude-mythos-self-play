/* fpaths.c: read graph6 graphs on stdin, compute f(G)=max_{u!=v} #simple u-v paths.
   Mode "census": aggregate per k=f(G) the min edge count + witness (g6,u,v); print at end.
   Mode "each": print "f m u v g6" per graph. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXN 32
static int n; static uint32_t adj[MAXN]; static long long cnt[MAXN];
static void dfs(int x, uint32_t vis){
  uint32_t nb = adj[x] & ~vis;
  while(nb){ int y=__builtin_ctz(nb); nb&=nb-1; cnt[y]++; dfs(y, vis|(1u<<y)); }
}
static int parse_g6(char*s){
  int len=strlen(s); while(len&&(s[len-1]=='\n'||s[len-1]=='\r')) s[--len]=0;
  if(s[0]=='>') { s+=10; }
  n=s[0]-63; memset(adj,0,sizeof adj);
  int k=0; char*p=s+1; int bit=6, val=0;
  for(int j=1;j<n;j++) for(int i=0;i<j;i++){
    if(bit==6){ val=*p++-63; bit=0; }
    if(val & (32>>bit)) { adj[i]|=1u<<j; adj[j]|=1u<<i; k++; }
    bit++;
  }
  return k;
}
#define KMAX 2000000
static int bestm[KMAX]; static char *bestg[KMAX]; static int bu[KMAX], bv[KMAX];
int main(int argc,char**argv){
  int each = argc>1 && !strcmp(argv[1],"each");
  char line[256]; long long ng=0;
  for(int i=0;i<KMAX;i++) bestm[i]=1<<30;
  while(fgets(line,sizeof line,stdin)){
    char orig[256]; strcpy(orig,line);
    int m=parse_g6(line); ng++;
    long long best=0; int Bu=0,Bv=1;
    for(int u=0;u<n-1;u++){
      memset(cnt,0,sizeof cnt); dfs(u,1u<<u);
      for(int v=u+1;v<n;v++) if(cnt[v]>best){best=cnt[v];Bu=u;Bv=v;}
    }
    int l=strlen(orig); while(l&&(orig[l-1]=='\n')) orig[--l]=0;
    if(each){ printf("%lld %d %d %d %s\n",best,m,Bu,Bv,orig); continue; }
    if(best<KMAX && m<bestm[best]){ bestm[best]=m; free(bestg[best]); bestg[best]=strdup(orig); bu[best]=Bu; bv[best]=Bv; }
  }
  if(!each){ for(int k=0;k<KMAX;k++) if(bestg[k]) printf("%d %d %d %d %s\n",k,bestm[k],bu[k],bv[k],bestg[k]); }
  fprintf(stderr,"graphs=%lld\n",ng);
  return 0;
}
