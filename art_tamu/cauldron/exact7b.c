/* Exact optimal total guesses for permutation Wordle (MO 497111), any permutation as guess.
   V(S) = |S| + min_g sum_{f != FULL} V(S_f).  Branch & bound with memo (hash of canonical
   candidate list under simultaneous conjugation s -> p s p^-1, which preserves the game).
   Root: first guess = identity (WLOG).  Usage: ./exact n   (n <= 7)                       */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define MAXN 7
#define MAXP 5040
int n, NP, FULL;
int P[MAXP][MAXN];
unsigned char FB[MAXP][MAXP];
short CONJ[MAXP][MAXP];          /* CONJ[p][s] = index of p s p^-1 */
static int pidx(int *a){ int r=0; for(int i=0;i<n;i++){ int c=0; for(int j=i+1;j<n;j++) if(a[j]<a[i]) c++; r=r*(n-i)+c; } return r; }
/* ---- memo: open addressing, key = sorted short list ---- */
typedef struct { unsigned long long h; int len; short *v; int val; char exact; } Ent;
#define HBITS 24
Ent *H; long nent=0; long memobytes=0;
static unsigned long long hsh(short *v,int m){ unsigned long long h=1469598103934665603ULL^m; for(int i=0;i<m;i++){h^=(unsigned short)v[i]; h*=1099511628211ULL;} return h; }
static Ent* find(short *v,int m,unsigned long long h,int create){
  unsigned long long i=h&((1ULL<<HBITS)-1);
  while(H[i].v){ if(H[i].h==h&&H[i].len==m&&!memcmp(H[i].v,v,m*2)) return &H[i]; i=(i+1)&((1ULL<<HBITS)-1);}
  if(!create) return NULL;
  if(memobytes>2000000000L || nent>(1L<<HBITS)*3/4) return NULL;
  H[i].h=h;H[i].len=m;H[i].v=malloc(m*2);memcpy(H[i].v,v,m*2);H[i].val=0;H[i].exact=0;nent++;memobytes+=m*2+48;return &H[i];
}
static int cmps(const void*a,const void*b){return *(short*)a-*(short*)b;}
static void canon(short *S,int m,short *out){
  static short tmp[MAXP]; int first=1;
  for(int p=0;p<(m>200?1:NP);p++){ for(int i=0;i<m;i++) tmp[i]=CONJ[p][S[i]]; qsort(tmp,m,2,cmps);
    int lt=first; if(!first){ for(int i=0;i<m;i++){ if(tmp[i]!=out[i]){ lt=tmp[i]<out[i]; break; } } }
    if(lt) memcpy(out,tmp,m*2); first=0; }
}
long nodes=0;
/* returns exact V(S) if < beta, else some value >= beta (a lower bound). */
static int V(short *S0,int m,int beta){
  if(m==1) return 1;
  if(m==2) return 3;
  int lbS=2*m-1; if(lbS>=beta) return lbS;
  short S[MAXP]; canon(S0,m,S);
  unsigned long long h=hsh(S,m); Ent *e=find(S,m,h,0);
  if(e){ if(e->exact) return e->val; if(e->val>=beta) return e->val; if(e->val>lbS) lbS=e->val; }
  nodes++;
  /* quick: a candidate splitting the rest into singletons gives the absolute minimum 2m-1 */
  int best=beta; int exact=0;
  /* evaluate guesses: compute partitions, order by sum of squares */
  int *order=malloc(NP*sizeof(int)); long *score=malloc(NP*sizeof(long));
  char *inS=calloc(NP,1); for(int i=0;i<m;i++) inS[S[i]]=1;
  int c[128];
  int ng=0;
  for(int g=0;g<NP;g++){ memset(c,0,sizeof c); for(int i=0;i<m;i++) c[FB[g][S[i]]]++;
    int nparts=0; long sq=0; for(int f=0;f<128;f++) if(c[f]){nparts++; if(f!=FULL) sq+=(long)c[f]*c[f];}
    if(nparts==1 && !inS[g]) continue;
    long lb=m; for(int f=0;f<128;f++) if(c[f]&&f!=FULL) lb+=2*c[f]-1;
    if(lb>=best) continue;
    if(lb==2*m-1 && lb<best){ best=lb; exact=1; break; }  /* all-singleton split by a candidate: achieves absolute minimum */
    score[g]=sq*4-(inS[g]?1:0); order[ng++]=g; }
  if(!exact){
    /* sort by score */
    for(int i=1;i<ng;i++){int x=order[i];long sx=score[x];int j=i-1; while(j>=0&&score[order[j]]>sx){order[j+1]=order[j];j--;} order[j+1]=x;}
    short *buf=malloc(m*2);
    for(int k=0;k<ng;k++){ int g=order[k];
      memset(c,0,sizeof c); for(int i=0;i<m;i++) c[FB[g][S[i]]]++;
      int start[128],pos[128],s=0; for(int f=0;f<128;f++){start[f]=s;pos[f]=s;s+=c[f];}
      for(int i=0;i<m;i++){int f=FB[g][S[i]]; buf[pos[f]++]=S[i];}
      long tot=m; int lbp[128]; for(int f=0;f<128;f++) if(c[f]&&f!=FULL){ lbp[f]=2*c[f]-1; tot+=lbp[f]; }
      if(tot>=best) continue;
      /* evaluate parts, largest first */
      int fo[128],nf=0; for(int f=0;f<128;f++) if(c[f]&&f!=FULL) fo[nf++]=f;
      for(int i=1;i<nf;i++){int x=fo[i],j=i-1; while(j>=0&&c[fo[j]]<c[x]){fo[j+1]=fo[j];j--;} fo[j+1]=x;}
      int ok=1;
      for(int i=0;i<nf;i++){ int f=fo[i]; if(c[f]<=2) continue;
        short *sub=malloc(c[f]*2); memcpy(sub,buf+start[f],c[f]*2);
        int v=V(sub,c[f],best-(int)(tot-lbp[f])); free(sub);
        tot+=v-lbp[f]; if(tot>=best){ok=0;break;} }
      if(ok && tot<best){ best=(int)tot; exact=1; if(best==lbS) break; }
    }
    free(buf);
  }
  free(order);free(score);free(inS);
  e=find(S,m,h,1);
  if(e){ if(exact){e->val=best;e->exact=1;} else { if(best>e->val) e->val=best; } }
  return best;
}
int main(int argc,char**argv){
  n=atoi(argv[1]); FULL=(1<<n)-1;
  int a[MAXN]; for(int i=0;i<n;i++) a[i]=i; NP=0;
  /* generate perms in lexicographic order */
  while(1){ memcpy(P[NP],a,sizeof a); NP++;
    int i=n-2; while(i>=0&&a[i]>a[i+1]) i--; if(i<0) break; int j=n-1; while(a[j]<a[i]) j--;
    int t=a[i];a[i]=a[j];a[j]=t; for(int l=i+1,r=n-1;l<r;l++,r--){t=a[l];a[l]=a[r];a[r]=t;} }
  for(int g=0;g<NP;g++) for(int s=0;s<NP;s++){int f=0; for(int i=0;i<n;i++) if(P[g][i]==P[s][i]) f|=1<<i; FB[g][s]=f;}
  for(int p=0;p<NP;p++){ int inv[MAXN]; for(int i=0;i<n;i++) inv[P[p][i]]=i;
    for(int s=0;s<NP;s++){ int b[MAXN]; for(int i=0;i<n;i++) b[i]=P[p][P[s][inv[i]]]; CONJ[p][s]=pidx(b);} }
  H=calloc(1ULL<<HBITS,sizeof(Ent));
  /* root: identity guess (index 0). sum over feedback classes */
  int c[128]={0}; for(int s=0;s<NP;s++) c[FB[0][s]]++;
  long total=NP; clock_t t0=clock();
  /* classes with same number of fixed points are conjugate-equivalent; solve one per size */
  long perk[MAXN+1];
  for(int k=n;k>=0;k--){ int f=(1<<k)-1; /* fixed set = first k positions */
    short S[MAXP]; int m=0; for(int s=0;s<NP;s++) if(FB[0][s]==f) S[m++]=s;
    int v = (f==FULL)?0:V(S,m,1<<29);
    int mult=0; for(int ff=0;ff<128;ff++) if(__builtin_popcount(ff)==k && ff<=FULL) mult++;
    perk[k]=v; total+=(long)v*mult;
    printf("fixed=%d  |class|=%d  V=%d  (lb %d)  x%d   t=%.1fs nodes=%ld memo=%ld\n",k,m,v,2*m-1,mult,(double)(clock()-t0)/CLOCKS_PER_SEC,nodes,nent); fflush(stdout); }
  printf("n=%d total=%ld / %d = %.6f\n",n,total,NP,(double)total/NP);
  return 0;
}
