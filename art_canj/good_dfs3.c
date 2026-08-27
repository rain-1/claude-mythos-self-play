/* MO 514690 v3: exhaustive DFS for good permutations of {1..n}, n = 2^m-1.
   Adds the full dyadic MATCHING filter: for each j (2^j <= n-1), the
   position-class (i mod 2^j) <-> value-residue (v mod 2^j) assignment must
   be a bijection (supply/demand: class sizes and residue counts both equal
   2^(m-j), except the 0-class/0-residue pair at 2^(m-j)-1; any sharing
   overflows supply).  This subsumes the periodicity + zero-class filters.
   Complement quotient: a_1 < (n+1)/2; true count = 2x reported.
   gcc -O3 -march=native -fopenmp good_dfs3.c -o good_dfs3 -lm
   ./good_dfs3 n [split]                                                  */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>

static int n, SPLIT, NJ; /* NJ = max j with 2^j <= n-1 */

typedef struct { int a[26]; } Prefix;
static Prefix *plist; static int np_pref = 0, cap_pref = 0;

typedef struct {
    int a[300]; long long pre[300]; uint8_t used[300];
    /* classres[j][c] = residue claimed by class c mod 2^j, or -1
       resown [j][r] = class owning residue r mod 2^j, or -1 */
    int classres[7][64], resown[7][64];
    long long sols; unsigned long long nodes;
} Ctx;

static long long total_sol = 0;
static unsigned long long total_nodes = 0;

static inline int try_claim(Ctx* c, int i, int v, int touched[7]){
    /* returns 1 if v is consistent with matching at all levels; records
       which levels made a NEW claim in touched[] (bitmask semantics) */
    for (int j = 1; j <= NJ; j++){
        int P = 1 << j;
        int cl = i & (P-1), r = v & (P-1);
        int cr = c->classres[j][cl];
        if (cr == -1){
            if (c->resown[j][r] != -1){       /* residue already owned */
                for (int k = 1; k < j; k++) if (touched[k]){
                    int Pk = 1<<k;
                    c->classres[k][i & (Pk-1)] = -1;
                    c->resown[k][v & (Pk-1)] = -1;
                    touched[k]=0;
                }
                return 0;
            }
            c->classres[j][cl] = r; c->resown[j][r] = cl;
            touched[j] = 1;
        } else if (cr != r){
            for (int k = 1; k < j; k++) if (touched[k]){
                int Pk = 1<<k;
                c->classres[k][i & (Pk-1)] = -1;
                c->resown[k][v & (Pk-1)] = -1;
                touched[k]=0;
            }
            return 0;
        } else touched[j] = 0;
    }
    return 1;
}
static inline void unclaim(Ctx* c, int i, int v, const int touched[7]){
    for (int j = 1; j <= NJ; j++) if (touched[j]){
        int P = 1 << j;
        c->classres[j][i & (P-1)] = -1;
        c->resown[j][v & (P-1)] = -1;
    }
}

static void rec(Ctx* c, int i){
    if (i > n){
        c->sols++;
        #pragma omp critical
        {
            printf("SOL");
            for (int k=1;k<=n;k++) printf(" %d", c->a[k]);
            printf("\n"); fflush(stdout);
        }
        return;
    }
    int vmax = (i==1) ? (n+1)/2 - 1 : n;  /* complement quotient */
    for (int v=1; v<=vmax; v++){
        if (c->used[v]) continue;
        long long s = c->pre[i-1] + v;
        int ok = 1, Lmax = i<n ? i : n-1;
        for (int L=2; L<=Lmax; L++)
            if ((s - c->pre[i-L]) % L == 0){ ok=0; break; }
        if (!ok) continue;
        int touched[7] = {0,0,0,0,0,0,0};
        if (!try_claim(c, i, v, touched)) continue;
        c->nodes++;
        c->used[v]=1; c->a[i]=v; c->pre[i]=s;
        rec(c, i+1);
        c->used[v]=0;
        unclaim(c, i, v, touched);
    }
}

/* serial prefix enumeration reusing the same Ctx machinery */
static Ctx *c0;
static void rec0(int i){
    if (i > SPLIT){
        if (np_pref == cap_pref){
            cap_pref = cap_pref ? cap_pref*2 : 1024;
            plist = realloc(plist, sizeof(Prefix)*cap_pref);
        }
        for (int k=1;k<=SPLIT;k++) plist[np_pref].a[k-1] = c0->a[k];
        np_pref++;
        return;
    }
    int vmax = (i==1) ? (n+1)/2 - 1 : n;
    for (int v=1; v<=vmax; v++){
        if (c0->used[v]) continue;
        long long s = c0->pre[i-1] + v;
        int ok = 1, Lmax = i<n ? i : n-1;
        for (int L=2; L<=Lmax; L++)
            if ((s - c0->pre[i-L]) % L == 0){ ok=0; break; }
        if (!ok) continue;
        int touched[7] = {0};
        if (!try_claim(c0, i, v, touched)) continue;
        c0->used[v]=1; c0->a[i]=v; c0->pre[i]=s;
        rec0(i+1);
        c0->used[v]=0;
        unclaim(c0, i, v, touched);
    }
}

int main(int argc, char** argv){
    n = argc>1 ? atoi(argv[1]) : 63;
    SPLIT = argc>2 ? atoi(argv[2]) : 14;
    NJ = 0; while ((2 << NJ) <= n-1) NJ++;   /* 2^(NJ) <= n-1 < 2^(NJ+1) */
    if ((n & (n+1)) != 0){
        fprintf(stderr, "matching filter requires n = 2^m-1\n"); return 1;
    }
    double t0 = omp_get_wtime();
    c0 = calloc(1, sizeof(Ctx));
    memset(c0->classres, -1, sizeof c0->classres);
    memset(c0->resown,  -1, sizeof c0->resown);
    rec0(1);
    fprintf(stderr, "prefixes(depth %d) = %d   (%.1fs)\n", SPLIT, np_pref,
            omp_get_wtime()-t0);
    int done = 0;
    #pragma omp parallel
    {
        Ctx* c = calloc(1, sizeof(Ctx));
        #pragma omp for schedule(dynamic,1)
        for (int t=0; t<np_pref; t++){
            memset(c->used, 0, n+1);
            memset(c->classres, -1, sizeof c->classres);
            memset(c->resown,  -1, sizeof c->resown);
            c->pre[0]=0;
            int ok = 1;
            for (int k=1;k<=SPLIT && ok;k++){
                int v = plist[t].a[k-1];
                int touched[7]={0};
                c->a[k]=v; c->pre[k]=c->pre[k-1]+v; c->used[v]=1;
                ok = try_claim(c, k, v, touched);
            }
            if (ok) rec(c, SPLIT+1);
            #pragma omp atomic
            done++;
            if ((done & 2047)==0)
                fprintf(stderr,"prefix %d/%d  %.0fs\n", done, np_pref,
                        omp_get_wtime()-t0);
        }
        #pragma omp critical
        { total_sol += c->sols; total_nodes += c->nodes; }
        free(c);
    }
    printf("n=%d raw_sols=%lld (true count = 2x = %lld) nodes=%llu elapsed=%.0fs\n",
           n, total_sol, 2*total_sol, total_nodes, omp_get_wtime()-t0);
    return 0;
}
