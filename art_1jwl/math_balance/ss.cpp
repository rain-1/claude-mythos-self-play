// Exact minimum of |±1^k ± 2^k ± ... ± n^k| by Schroeppel–Shamir (4 lists, 2 heaps), __int128.
// usage: ss k n1 n2 [n0]   -> for each n in [n1,n2] prints n, parity, min, a sign vector achieving it
// If n > n0 (n0>0): top terms n..n0+1 are signed greedily (with random perturbation on retries) and
// only the bottom n0 terms are searched: a found parity value is a certificate, a miss is NOT a proof.
#include <bits/stdc++.h>
using namespace std;
typedef __int128 I;
typedef unsigned long long u64;
static string str(I x){ if(x==0) return "0"; bool neg=x<0; if(neg) x=-x; string s; while(x>0){ s+=char('0'+(int)(x%10)); x/=10;} if(neg) s+='-'; reverse(s.begin(),s.end()); return s; }
struct E{ I v; uint32_t m; };           // value, sign mask (bit=1 -> minus)
static void gen(const vector<I>&w, vector<E>&L){
  int n=w.size(); L.assign((size_t)1<<n, E{0,0});
  for(uint32_t m=0;m<(1u<<n);m++){ I s=0; for(int i=0;i<n;i++) s+= (m>>i&1)? -w[i]:w[i]; L[m]=E{s,m}; }
  sort(L.begin(),L.end(),[](const E&a,const E&b){return a.v<b.v;});
}
struct H{ I v; uint32_t i,j; };
// returns min |sum - target| over all sign choices of w (groups g[0..3]); early exit when <= stop
static I closest(const vector<I> g[4], I target, I stop, uint32_t msk[4]){
  vector<E> L[4]; for(int t=0;t<4;t++) gen(g[t],L[t]);
  // A ascending: L0[i]+L1[j]; B descending: L2[i]+L3[j]
  auto cmpA=[](const H&a,const H&b){return a.v>b.v;};
  auto cmpB=[](const H&a,const H&b){return a.v<b.v;};
  vector<H> ha,hb; ha.reserve(L[0].size()); hb.reserve(L[2].size());
  for(uint32_t i=0;i<L[0].size();i++) ha.push_back(H{L[0][i].v+L[1][0].v,i,0});
  uint32_t last3=L[3].size()-1;
  for(uint32_t i=0;i<L[2].size();i++) hb.push_back(H{L[2][i].v+L[3][last3].v,i,last3});
  make_heap(ha.begin(),ha.end(),cmpA); make_heap(hb.begin(),hb.end(),cmpB);
  I best=-1;
  while(!ha.empty() && !hb.empty()){
    H a=ha.front(), b=hb.front();
    I c=a.v+b.v-target; I ac=c<0?-c:c;
    if(best<0||ac<best){ best=ac; msk[0]=L[0][a.i].m; msk[1]=L[1][a.j].m; msk[2]=L[2][b.i].m; msk[3]=L[3][b.j].m; if(best<=stop) return best; }
    if(c<0){ pop_heap(ha.begin(),ha.end(),cmpA); H&x=ha.back(); if(x.j+1<L[1].size()){ x.j++; x.v=L[0][x.i].v+L[1][x.j].v; push_heap(ha.begin(),ha.end(),cmpA);} else ha.pop_back(); }
    else   { pop_heap(hb.begin(),hb.end(),cmpB); H&x=hb.back(); if(x.j>0){ x.j--; x.v=L[2][x.i].v+L[3][x.j].v; push_heap(hb.begin(),hb.end(),cmpB);} else hb.pop_back(); }
  }
  return best;
}
int main(int argc,char**argv){
  int k=atoi(argv[1]), n1=atoi(argv[2]), n2=atoi(argv[3]); int n0=argc>4?atoi(argv[4]):0;
  mt19937_64 rng(12345);
  for(int n=n1;n<=n2;n++){
    vector<I> w(n+1); for(int i=1;i<=n;i++){ I p=1; for(int j=0;j<k;j++) p*=i; w[i]=p; }
    int par=(int)(((long long)n*(n+1)/2)&1);
    int nb = (n0>0 && n>n0)? n0 : n;
    vector<int> sgn(n+1,1);
    I best=-1; vector<int> bests; bool exact=(nb==n);
    // residue census of the bottom nb terms mod M: used to reject top sign choices that leave the
    // bottom an arithmetically starved target (the 2-adic lock for k = 4, 8, 16, ...)
    const int M=(argc>5?atoi(argv[5]):64); vector<double> cnt(M,0.0), tmp(M);
    if(!exact){ cnt[0]=1; for(int i=1;i<=nb;i++){ int r=(int)(w[i]%M); for(int x=0;x<M;x++) tmp[x]=cnt[(x-r+M)%M]+cnt[(x+r)%M]; cnt=tmp; } }
    double mean=0; if(!exact){ for(int x=0;x<M;x++) mean=max(mean, par? cnt[(x+1)%M]+cnt[(x+M-1)%M] : cnt[x]); mean*=0.4; } // threshold: 20% of the best residue
    for(int trial=0; trial<(exact?1:200); trial++){
      I top=0;
      for(int att=0; att<100000; att++){
        top=0;
        // odd terms may be forced to one pan with probability q (the lock for k=8,16 wants lopsided odd signs)
        int q=(att+trial)%11, mode=(((att+trial)/11)&1)?1:-1;
        for(int i=n;i>nb;i--){ int s=(top>0)?-1:1; if((i&1) && (int)(rng()%10)<q) s=mode; else if((trial>0||att>0) && (rng()%8==0)) s=-s; sgn[i]=s; top+=s*w[i]; }
        if(exact) break;
        int t=(int)(((-top)%M+M)%M); double sc= par? cnt[(t+1)%M]+cnt[(t+M-1)%M] : cnt[t];
        if(sc>=0.5*mean) break;
      }
      vector<I> g[4]; vector<int> idx[4];
      for(int i=nb;i>=1;i--){ int t=(nb-i)%4; if(((nb-i)/4)&1) t=3-t; g[t].push_back(w[i]); idx[t].push_back(i); }
      uint32_t msk[4]; I r=closest(g,-top,(I)par,msk);
      if(best<0||r<best){ best=r; for(int t=0;t<4;t++) for(size_t q=0;q<idx[t].size();q++) sgn[idx[t][q]]=(msk[t]>>q&1)?-1:1; bests=sgn; }
      if(best<=par) break;
    }
    // verify
    I s=0; for(int i=1;i<=n;i++) s+=bests[i]*w[i]; if(s<0){ s=-s; }
    if(s!=best){ fprintf(stderr,"VERIFY FAIL n=%d\n",n); return 1; }
    string sv; for(int i=1;i<=n;i++) sv+=(bests[i]>0?'+':'-');
    printf("%d %d %d %s %s %s\n",k,n,par,str(best).c_str(),exact?"exact":"reduced",sv.c_str()); fflush(stdout);
  }
}
