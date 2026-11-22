// toss n [print]: strings of length N=n-1 (paths with n points).
// counts tossprint classes a(N), ribbon classes R(n) (BTvW via union-find on alpha o beta ~ alpha o beta*),
// and prints tossprint classes that contain more than one ribbon class.
#include <bits/stdc++.h>
#include <omp.h>
using namespace std;
typedef unsigned long long u64; typedef __uint128_t u128;
int n,N;
static u64 H1[64][64],H2[64][64];
vector<uint32_t> par;
uint32_t fnd(uint32_t x){while(par[x]!=x){par[x]=par[par[x]];x=par[x];}return x;}
void uni(uint32_t a,uint32_t b){a=fnd(a);b=fnd(b);if(a!=b){if(a<b)par[b]=a;else par[a]=b;}}
// strings: bit i (LSB first) = i-th step
u64 rev(u64 w,int L){u64 r=0;for(int i=0;i<L;i++)if(w>>i&1)r|=1ULL<<(L-1-i);return r;}
u64 comp(u64 a,int la,u64 b,int lb){ // alpha o beta: beta s1 beta s2 ... beta ; la,lb = string lengths
  u64 r=0;int pos=0;for(int i=0;i<=la;i++){r|=b<<pos;pos+=lb;if(i<la){if(a>>i&1)r|=1ULL<<pos;pos++;}}return r;}
string str(u64 w){string s;for(int i=0;i<N;i++)s+=(w>>i&1)?'1':'0';return s;}
int main(int argc,char**argv){
  n=atoi(argv[1]);N=n-1;int pr=argc>2?atoi(argv[2]):0;
  mt19937_64 rng(12345);for(auto&r:H1)for(auto&x:r)x=rng();for(auto&r:H2)for(auto&x:r)x=rng();
  u64 M=1ULL<<N;
  par.resize(M);for(u64 i=0;i<M;i++)par[i]=i;
  for(u64 w=0;w<M;w++)uni(w,rev(w,N));
  for(int a=2;a<n;a++)if(n%a==0){int b=n/a;
    for(u64 x=0;x<(1ULL<<(a-1));x++)for(u64 y=0;y<(1ULL<<(b-1));y++){
      u64 c=comp(x,a-1,y,b-1);uni(c,comp(x,a-1,rev(y,b-1),b-1));}}
  u64 R=0;for(u64 i=0;i<M;i++)if(fnd(i)==i)R++;
  // tossprints for canonical strings (w<=rev w)
  vector<pair<u128,uint32_t>> v;
  vector<u64> can;for(u64 w=0;w<M;w++)if(w<=rev(w,N))can.push_back(w);
  v.resize(can.size());
  #pragma omp parallel for schedule(dynamic,4096)
  for(size_t k=0;k<can.size();k++){u64 w=can[k];
    int pz[64];pz[0]=0;for(int i=0;i<N;i++)pz[i+1]=pz[i]+!(w>>i&1);
    u64 h1=0,h2=0;
    for(int i=0;i<N;i++)for(int j=i+1;j<=N;j++){int z=pz[j]-pz[i];int o=j-i-z;h1+=H1[z][o];h2+=H2[z][o];}
    v[k]={((u128)h1<<64)|h2,(uint32_t)w};}
  sort(v.begin(),v.end());
  u64 A=0,extra=0;
  for(size_t i=0;i<v.size();){size_t j=i;set<uint32_t> rc;while(j<v.size()&&v[j].first==v[i].first){rc.insert(fnd(v[j].second));j++;}
    A++;
    if(rc.size()>1){extra+=rc.size()-1;
      if(pr){printf("CLASS %zu ribbon classes:\n",rc.size());for(size_t k=i;k<j;k++)printf("  %s  rc=%u\n",str(v[k].second).c_str(),fnd(v[k].second));}}
    i=j;}
  printf("n=%d N=%d a(N)=%llu R(n)=%llu diff=%llu\n",n,N,A,R,extra);
}
