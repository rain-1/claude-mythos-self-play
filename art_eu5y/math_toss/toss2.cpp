// toss2 n K out : tossprint classes of binary strings of length n-1, in K hash-bucket passes.
// Writes every class that is larger than {w, reverse(w)} to `out` (one class per line), prints a(N).
#include <bits/stdc++.h>
#include <omp.h>
using namespace std;
typedef unsigned long long u64;
int n,N;
static u64 H1[64][64];
#pragma pack(push,1)
struct E{u64 h;uint32_t w;};
#pragma pack(pop)
static inline u64 rev(u64 w,int L){u64 r=0;for(int i=0;i<L;i++)if(w>>i&1)r|=1ULL<<(L-1-i);return r;}
int main(int argc,char**argv){
  n=atoi(argv[1]);N=n-1;int K=atoi(argv[2]);FILE*f=fopen(argv[3],"w");
  mt19937_64 rng(777);for(auto&r:H1)for(auto&x:r)x=rng();
  u64 M=1ULL<<N;u64 A=0,groups=0;
  int T=omp_get_max_threads();
  for(int pass=0;pass<K;pass++){
    vector<vector<E>> loc(T);
    #pragma omp parallel
    {int t=omp_get_thread_num();auto&L=loc[t];
     #pragma omp for schedule(dynamic,1<<14)
     for(u64 w=0;w<M;w++){ if(w>rev(w,N))continue;
       int pz[64];pz[0]=0;for(int i=0;i<N;i++)pz[i+1]=pz[i]+!(w>>i&1);
       u64 h=0;for(int i=0;i<N;i++)for(int j=i+1;j<=N;j++){int z=pz[j]-pz[i];h+=H1[z][j-i-z];}
       h^=h>>29;h*=0x9E3779B97F4A7C15ULL;h^=h>>32;
       if((int)(h%K)==pass)L.push_back({h,(uint32_t)w});}
    }
    vector<E> v;size_t tot=0;for(auto&L:loc)tot+=L.size();v.reserve(tot);
    for(auto&L:loc){v.insert(v.end(),L.begin(),L.end());vector<E>().swap(L);}
    sort(v.begin(),v.end(),[](const E&a,const E&b){return a.h<b.h;});
    for(size_t i=0;i<v.size();){size_t j=i;while(j<v.size()&&v[j].h==v[i].h)j++;A++;
      if(j-i>1){groups++;for(size_t k=i;k<j;k++){for(int b=0;b<N;b++)fputc((v[k].w>>b&1)?'1':'0',f);fputc(k+1<j?' ':'\n',f);}}
      i=j;}
    fprintf(stderr,"pass %d done, %zu canonical strings\n",pass,tot);
  }
  fclose(f);printf("n=%d N=%d a(N)=%llu nontrivial classes=%llu\n",n,N,A,groups);
}
