// Exhaustively count directed Hamiltonian cycles C of Q_d (through 0) such that the d cyclic
// coordinate shifts of C are pairwise arc-disjoint, i.e. labels rho^{-i}(v) of arcs (v,i) all distinct.
// usage: ./ansatz_count d   (feasible for d<=5)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
int d,n; uint64_t used,lab; long long cnt=0; int path[64]; int printed=0, all=0;
static inline int rinv(int v,int i){ i%=d; if(!i) return v; return ((v>>i)|(v<<(d-i)))&(n-1); }
void rec(int v,int len){
  if(len==n){ for(int i=0;i<d;i++) if((v^(1<<i))==0 && !((lab>>rinv(v,i))&1)){ cnt++;
      if(all||printed<1){printed++; printf("example:"); for(int k=0;k<n;k++) printf(" %d",path[k]); printf("\n");} }
    return; }
  for(int i=0;i<d;i++){ int w=v^(1<<i); if((used>>w)&1) continue; int l=rinv(v,i); if((lab>>l)&1) continue;
    used|=1ULL<<w; lab|=1ULL<<l; path[len]=w; rec(w,len+1); used^=1ULL<<w; lab^=1ULL<<l; }
}
int main(int c,char**a){ d=atoi(a[1]); all=(c>2); n=1<<d; used=1; lab=0; path[0]=0; rec(0,1);
  printf("d=%d: cycles C with arc-disjoint shifts: %lld ; rho-invariant decompositions: %lld (=count/d)\n",d,cnt,cnt/d); return 0; }
