// Exact min |±1^k ± ... ± n^k| when k = 2^r * odd, r >= 3 (so 2^k ≡ 0 mod M, M = 2^(r+3)):
//   odd i:  i^k ≡ 1 (i ≡ ±1 mod 8)  or  1 + M/2 (i ≡ ±3 mod 8)   (mod M);   even i: i^k ≡ 0 (mod M)
//   => S ≡ m - 2J + (M/2) u  (mod M),  m = #odd i <= n, J = #odd i with a minus sign, u = #{i<=n: i ≡ ±3 mod 8}.
// For the target (0 or ±1) only a few J are allowed; we enumerate the minus-sets among the odd terms (|set| = J or m-J
// by symmetry, must be <= JMAX) and solve the even terms by meet-in-the-middle.  Exhaustive => a proof of the minimum
// restricted to |S| < M/2 window... we report the exact minimum of |S| over ALL sign choices whose J is allowed for
// some target value t with |t| <= W (W small), i.e. the exact answer provided it is <= W.
// usage: lock k n W
#include <bits/stdc++.h>
using namespace std; typedef __int128 I;
static string str(I x){ if(x==0) return "0"; bool neg=x<0; if(neg) x=-x; string s; while(x>0){ s+=char('0'+(int)(x%10)); x/=10;} if(neg) s+='-'; reverse(s.begin(),s.end()); return s; }
int main(int argc,char**argv){
  int k=atoi(argv[1]), n=atoi(argv[2]), W=atoi(argv[3]);
  int r=0; while(((k>>r)&1)==0) r++; long long M=1LL<<(r+3);
  vector<I> w(n+1); vector<I> odd, even; int u=0;
  for(int i=1;i<=n;i++){ I p=1; for(int j=0;j<k;j++) p*=i; w[i]=p; long long res=(long long)(p%M);
    if(i&1){ odd.push_back(p); int c=i%8; bool pm3=(c==3||c==5); if(pm3) u++; if(res!=(pm3? 1+M/2:1)){ fprintf(stderr,"structure fails\n"); return 1; } }
    else { even.push_back(p); if(res!=0){ fprintf(stderr,"structure fails (even)\n"); return 1; } } }
  int m=odd.size(); int par=(int)(((long long)n*(n+1)/2)&1);
  // even part: MITM lists
  int ne=even.size(), na=ne/2, nb=ne-na;
  vector<I> A((size_t)1<<na), B((size_t)1<<nb);
  for(size_t x=0;x<A.size();x++){ I s=0; for(int i=0;i<na;i++) s+=(x>>i&1)?-even[i]:even[i]; A[x]=s; }
  for(size_t x=0;x<B.size();x++){ I s=0; for(int i=0;i<nb;i++) s+=(x>>i&1)?-even[na+i]:even[na+i]; B[x]=s; }
  sort(A.begin(),A.end()); sort(B.begin(),B.end());
  I sumodd=0; for(I x:odd) sumodd+=x;
  I best=-1; long long patterns=0;
  // which J are allowed for a total t with |t|<=W, t ≡ par mod 2
  set<int> Js; for(int J=0;J<=m;J++){ long long res=((m-2*J+(M/2)*(long long)u)%M+M)%M; for(int t=-W;t<=W;t++) if(((t%2)+2)%2==par && ((t%M)+M)%M==res) Js.insert(min(J,m-J)); }
  printf("k=%d n=%d M=%lld m=%d u=%d allowed min(J,m-J):",k,n,M,m,u); for(int J:Js) printf(" %d",J); printf("\n"); fflush(stdout);
  if(argc>4){ // random mode: sample minus-sets of an allowed size until the target parity value is hit (a certificate of success)
    long long R=atoll(argv[4]); mt19937_64 rng(n*1000+k); vector<int> Jv(Js.begin(),Js.end()); vector<int> idx(m); iota(idx.begin(),idx.end(),0);
    for(long long it=0; it<R; it++){ int J=Jv[it%Jv.size()]; shuffle(idx.begin(),idx.end(),rng);
      I so=sumodd; for(int i=0;i<J;i++) so-=2*odd[idx[i]];
      I target=-so; size_t ia=0; long long ib=(long long)B.size()-1;
      while(ia<A.size() && ib>=0){ I cur=A[ia]+B[ib]-target; I ac=cur<0?-cur:cur; if(best<0||ac<best) best=ac; if(cur<0) ia++; else ib--; }
      if(best<=W){ printf("k=%d n=%d parity=%d FOUND |S|=%s after %lld random patterns (J=%d of %d odd terms on the minority pan):",k,n,par,str(best).c_str(),it+1,J,m); for(int i=0;i<J;i++) printf(" %d",2*idx[i]+1); printf("\n"); return 0; } }
    printf("k=%d n=%d parity=%d NOT FOUND in %lld random patterns, best %s\n",k,n,par,R,str(best).c_str()); return 0; }
  for(int J:Js){
    if(J>4){ printf("J=%d too large to enumerate here\n",J); continue; }
    // enumerate J-subsets of odd terms carrying the minus sign (the mirror image m-J is the global sign flip)
    vector<int> c(J); for(int i=0;i<J;i++) c[i]=i;
    while(true){
      I so=sumodd; for(int i=0;i<J;i++) so-=2*odd[c[i]];
      patterns++;
      // closest a+b to -so
      I target=-so; size_t ia=0; long long ib=(long long)B.size()-1;
      while(ia<A.size() && ib>=0){ I cur=A[ia]+B[ib]-target; I ac=cur<0?-cur:cur; if(best<0||ac<best) best=ac; if(cur<0) ia++; else ib--; }
      int i=J-1; while(i>=0 && c[i]==m-J+i) i--; if(i<0) break; c[i]++; for(int j=i+1;j<J;j++) c[j]=c[j-1]+1;
    }
  }
  printf("k=%d n=%d parity=%d patterns=%lld  min|S| over allowed J = %s  (exact minimum if <= %d)\n",k,n,par,patterns,str(best).c_str(),W);
}
