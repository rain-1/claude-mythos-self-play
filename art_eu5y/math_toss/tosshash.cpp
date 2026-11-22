// tosshash < words : prints a 128-bit additive hash of the tossprint of each word (one per line)
#include <bits/stdc++.h>
using namespace std; typedef unsigned long long u64;
static u64 H1[128][128],H2[128][128];
int main(){mt19937_64 rng(4242);for(auto&r:H1)for(auto&x:r)x=rng();for(auto&r:H2)for(auto&x:r)x=rng();
  char buf[512];
  while(scanf("%500s",buf)==1){int N=strlen(buf);int pz[512];pz[0]=0;for(int i=0;i<N;i++)pz[i+1]=pz[i]+(buf[i]=='0');
    u64 a=0,b=0;for(int i=0;i<N;i++)for(int j=i+1;j<=N;j++){int z=pz[j]-pz[i];a+=H1[z][j-i-z];b+=H2[z][j-i-z];}
    printf("%016llx%016llx\n",a,b);}
}
