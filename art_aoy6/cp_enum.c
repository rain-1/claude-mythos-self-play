/* cp_enum.c — enumerate all comparative probability orders on n atoms.
 *
 * A comparative probability order is a strict total order < on the 2^n
 * subsets of [n] with:
 *   (positivity)  {} < A for every nonempty A,
 *   (additivity)  A < B  <=>  A u C < B u C  for C disjoint from A u B.
 * Additivity means the orientation of {A,B} depends only on the canonical
 * disjoint pair (A\B, B\A). We enumerate orders bottom-up (rank 0 = {}),
 * maintaining orientations of canonical pairs; a subset may be placed only
 * when all its proper subsets are placed (monotonicity is implied by the
 * axioms) and when the orientations it induces against all placed subsets
 * are consistent.
 *
 * Optionally fix the singleton order {1}<{2}<...<{n} (canonical form under
 * atom relabeling) with -c.
 *
 * Output: each completed order as one line of 2^n subset masks (ranks
 * ascending), plus a final "# count = ..." line on stderr.
 * Usage: ./cp_enum n [-c] > orders_n.txt
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int n, NS;             /* NS = 2^n subsets */
static int canonical = 0;
static signed char orient[1 << 10][1 << 10]; /* orient[S][T]=+1: S side smaller; canonical S<T, disjoint */
static int placed[1 << 10];   /* order so far, by rank */
static int placedmask_of[1 << 10]; /* is subset placed */
static int nplaced;
static long long count = 0;
static FILE *out;

/* record of orientation sets per placement step for undo */
static int touched[1 << 10][1 << 10]; /* touched[depth][i] = pair code set at this depth */
static int ntouched[1 << 10];

static void emit(void){
    count++;
    for(int i=0;i<NS;i++) fprintf(out, i? " %d":"%d", placed[i]);
    fputc('\n', out);
}

static void dfs(void){
    if(nplaced == NS){ emit(); return; }
    for(int X=1; X<NS; X++){
        if(placedmask_of[X]) continue;
        /* all proper subsets placed? */
        int ok=1;
        for(int S=(X-1)&X; S; S=(S-1)&X) if(!placedmask_of[S]){ ok=0; break; }
        if(!ok) continue;
        if(canonical){
            /* singleton order fixed: {i} may be placed only if {i-1} placed */
            if(__builtin_popcount(X)==1){
                int i=__builtin_ctz(X);
                if(i>0 && !placedmask_of[1<<(i-1)]) continue;
            }
        }
        /* check consistency: Y < X for all placed Y */
        int d = nplaced; ntouched[d]=0; ok=1;
        for(int r=0; r<nplaced && ok; r++){
            int Y = placed[r];
            int S = Y & ~X, T = X & ~Y;   /* canonical pair; assert S side < T side */
            if(S==0 && T==0) { ok=0; break; } /* Y==X impossible */
            int a=S, b=T, sign=+1;
            if(a>b){ int t=a;a=b;b=t; sign=-1; } /* store with a<b; +1 means a-side < b-side */
            signed char cur = orient[a][b];
            if(cur==0){
                orient[a][b] = (signed char)sign;
                touched[d][ntouched[d]++] = a*NS+b;
            } else if(cur != sign) ok=0;
        }
        if(ok){
            placed[nplaced]=X; placedmask_of[X]=1; nplaced++;
            dfs();
            nplaced--; placedmask_of[X]=0;
        }
        for(int t=0;t<ntouched[d];t++)
            orient[touched[d][t]/NS][touched[d][t]%NS]=0;
        ntouched[d]=0;
    }
}

int main(int argc,char**argv){
    if(argc<2){ fprintf(stderr,"usage: cp_enum n [-c]\n"); return 1; }
    n = atoi(argv[1]); NS = 1<<n;
    if(argc>2 && !strcmp(argv[2],"-c")) canonical=1;
    out = stdout;
    memset(orient,0,sizeof orient);
    placed[0]=0; placedmask_of[0]=1; nplaced=1; /* {} first (positivity) */
    dfs();
    fprintf(stderr,"# n=%d canonical=%d count=%lld\n",n,canonical,count);
    return 0;
}
