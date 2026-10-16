// naive DFS: count good permutations of 1..n (n odd), block lengths 2..n-1 checked incrementally
#include <stdio.h>
#include <stdlib.h>
int n; long long S[64]; int a[64]; int used[64]; long long cnt=0, nodes=0; FILE*out=NULL;
void dfs(int t){ // place a_t, t from 1
  if(t>n){cnt++; if(out){for(int i=1;i<=n;i++)fprintf(out,"%d%c",a[i],i==n?'\n':' ');} return;}
  for(int v=1;v<=n;v++) if(!used[v]){
    nodes++;
    long long s=S[t-1]+v; int ok=1;
    for(int i=1;i<t;i++){ int L=t-i+1; if(L==n) continue; if((s-S[i-1])%L==0){ok=0;break;} }
    if(!ok) continue;
    used[v]=1;a[t]=v;S[t]=s; dfs(t+1); used[v]=0;
  }
}
int main(int c,char**v){n=atoi(v[1]); if(c>2) out=fopen(v[2],"w"); S[0]=0; dfs(1);
 printf("n=%d good=%lld nodes=%lld\n",n,cnt,nodes); if(out)fclose(out); return 0;}
