/* Count q (permutations) such that L[i][j]=(i+q[j]) mod n is incremental.
   usage: cyclic n [dumpfile]   prints total count, linear count. */
#include <stdio.h>
#include <stdlib.h>
#define MX 32
int n; int q[MX], used[MX];
int cs[MX][2*MX], cd[MX][2*MX]; /* cs[k][d]: #cells value<=k on sum diag d */
long long total=0; FILE *dump=NULL;
static int place(int j,int s,int dir){ /* dir=+1 add (with check), -1 remove */
  for(int i=0;i<n;i++){int v=(i+s)%n; int a=i+j, b=i-j+n-1;
    for(int k=v;k<n-1;k++){cs[k][a]+=dir; cd[k][b]+=dir;}}
  return 0;}
static int ok(int j,int s){
  for(int i=0;i<n;i++){int v=(i+s)%n; int a=i+j, b=i-j+n-1;
    for(int k=v;k<n-1;k++){ if(cs[k][a]>=k+1||cd[k][b]>=k+1) return 0;}}
  return 1;}
/* note: ok must account for two cells in same column on same diag: impossible (one cell per column per diag) */
void rec(int j){
  if(j==n){ total++; if(dump){for(int t=0;t<n;t++)fprintf(dump,"%d%c",q[t],t==n-1?'\n':' ');} return;}
  for(int s=0;s<n;s++) if(!used[s] && ok(j,s)){
    used[s]=1;q[j]=s;place(j,s,1);rec(j+1);place(j,s,-1);used[s]=0; if(j==0){fprintf(stderr,"q0=%d cumulative=%lld\n",s,total);fflush(stderr);}}
}
int main(int c,char**v){n=atoi(v[1]); if(c>2) dump=fopen(v[2],"w");
  rec(0); printf("%d %lld\n",n,total); if(dump)fclose(dump); return 0;}
