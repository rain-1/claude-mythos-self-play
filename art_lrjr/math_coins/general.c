/* Count ALL incremental Latin squares of order n (values 0..n-1; every ordinary diagonal
   has at most k+1 cells with value <= k). Built layer by layer: layer v = permutation matrix.
   usage: general n [dumpfile] ; dump prints each square as n*n digits (base 36). */
#include <stdio.h>
#include <stdlib.h>
int n; int L[16][16]; int cs[32], cd[32]; int colused; long long total=0; FILE*dump=NULL;
long long rowcyc=0, colcyc=0;
void finish(){ total++;
  /* row-cyclic: L[i][j]=(i+L[0][j])%n ; column-cyclic: L[i][j]=(j+L[i][0])%n */
  int rc=1,cc=1; for(int i=0;i<n;i++)for(int j=0;j<n;j++){ if(L[i][j]!=(i+L[0][j])%n)rc=0; if(L[i][j]!=(j+L[i][0])%n)cc=0;}
  rowcyc+=rc; colcyc+=cc;
  if(dump){for(int i=0;i<n;i++)for(int j=0;j<n;j++)fputc("0123456789abcdefghijklmnopqrstuvwxyz"[L[i][j]],dump);fputc('\n',dump);} }
void rec(int v,int i){
  if(v==n-1){ /* fill remaining cells */
    for(int a=0;a<n;a++)for(int b=0;b<n;b++)if(L[a][b]<0)L[a][b]=n-1;
    finish();
    for(int a=0;a<n;a++)for(int b=0;b<n;b++)if(L[a][b]==n-1)L[a][b]=-1;
    return;}
  if(i==n){int sv=colused; colused=0; rec(v+1,0); colused=sv; return;}
  for(int c=0;c<n;c++){ if((colused>>c)&1) continue; if(L[i][c]>=0) continue;
    int a=i+c,b=i-c+n-1; if(cs[a]>=v+1||cd[b]>=v+1) continue;
    L[i][c]=v; cs[a]++;cd[b]++; colused|=1<<c;
    rec(v,i+1);
    L[i][c]=-1; cs[a]--;cd[b]--; colused&=~(1<<c);}
}
int main(int argc,char**argv){n=atoi(argv[1]); if(argc>2)dump=fopen(argv[2],"w");
  for(int i=0;i<n;i++)for(int j=0;j<n;j++)L[i][j]=-1;
  rec(0,0); printf("n=%d incremental_latin=%lld row_cyclic=%lld col_cyclic=%lld\n",n,total,rowcyc,colcyc);
  if(dump)fclose(dump);}
