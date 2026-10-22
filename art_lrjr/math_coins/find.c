/* Find cyclic incremental q by randomized backtracking. usage: find n seed [nsol] [nontoroidal]
   prints up to nsol solutions; if nontoroidal=1 only prints q whose layer-0 is not a toroidal queens sol; =2 only toroidal but nonlinear. */
#include <stdio.h>
#include <stdlib.h>
#define MX 64
int n,q[MX],used[MX],cs[MX][2*MX],cd[MX][2*MX],nsol=1,nontor=0,found=0; long long nodes=0;
int perm[MX][MX];
int ok(int j,int s){for(int i=0;i<n;i++){int v=(i+s)%n,a=i+j,b=i-j+n-1;for(int k=v;k<n-1;k++)if(cs[k][a]>=k+1||cd[k][b]>=k+1)return 0;}return 1;}
void place(int j,int s,int d){for(int i=0;i<n;i++){int v=(i+s)%n,a=i+j,b=i-j+n-1;for(int k=v;k<n-1;k++){cs[k][a]+=d;cd[k][b]+=d;}}}
int toroidal(){int A[MX]={0},B[MX]={0};for(int j=0;j<n;j++){int r=(n-q[j])%n;if(A[(r+j)%n]++||B[((r-j)%n+n)%n]++)return 0;}return 1;}
int linear(){int a=((q[1]-q[0])%n+n)%n;for(int j=0;j<n;j++)if(q[j]!=(a*j+q[0])%n)return 0;return 1;}
void rec(int j){ if(found>=nsol) return; if(++nodes>200000000LL) return;
  if(j==n){ if(nontor==1 && toroidal()) return; if(nontor==2 && (!toroidal()||linear())) return; found++; printf("[");for(int t=0;t<n;t++)printf("%d%s",q[t],t<n-1?",":"]\n");fflush(stdout);return;}
  for(int t=0;t<n;t++){int s=perm[j][t]; if(!used[s]&&ok(j,s)){used[s]=1;q[j]=s;place(j,s,1);rec(j+1);place(j,s,-1);used[s]=0;}}}
int main(int c,char**v){n=atoi(v[1]);srand(atoi(v[2]));if(c>3)nsol=atoi(v[3]);if(c>4)nontor=atoi(v[4]);
  for(int j=0;j<n;j++){for(int t=0;t<n;t++)perm[j][t]=t;for(int t=n-1;t>0;t--){int r=rand()%(t+1),x=perm[j][t];perm[j][t]=perm[j][r];perm[j][r]=x;}}
  rec(0); fprintf(stderr,"found=%d nodes=%lld\n",found,nodes);}
