/* MO 514690 v4: exhaustive DFS for good permutations of {1..n}, n = 2^m-1,
   with EARLY TAIL CHECKING.
   Structural facts (forced by dyadic matching, machine-verified v3):
     M = (n+1)/2;  a_M = M;  a_{M+t} = partner(a_t) = a_t ± M  (t=1..M-1).
   So placing a_t determines a_{M+t} immediately; every window lying fully
   inside the tail [M+1 .. M+t] is checked at depth t instead of depth M+t.
   Windows crossing the middle are checked during the (branching-1) descent
   of depths M..n.  Everything else as v3 (matching filter, complement
   quotient a_1 < M, split-parallel).
   gcc -O3 -march=native -fopenmp good_dfs5.c -o good_dfs4 -lm
   ./good_dfs5 n [split]                                                  */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>

static int n, M, S_, SPLIT, NJ;   /* M = P = largest 2^j <= n-1; S_ = n-M */

typedef struct { int a[16]; } Prefix;
static Prefix *plist; static int np_pref = 0, cap_pref = 0;

typedef struct {
    int a[300]; long long pre[300]; uint8_t used[300];
    long long pre2[160];              /* prefix sums of tail a_{M+1..} */
    int classres[7][64], resown[7][64];
    long long sols; unsigned long long nodes;
} Ctx;

static long long total_sol = 0;
static unsigned long long total_nodes = 0;

static inline int try_claim(Ctx* c, int i, int v, int touched[7]){
    for (int j = 1; j <= NJ; j++){
        int P = 1 << j;
        int cl = i & (P-1), r = v & (P-1);
        int cr = c->classres[j][cl];
        if (cr == -1){
            if (c->resown[j][r] != -1) goto fail;
            c->classres[j][cl] = r; c->resown[j][r] = cl; touched[j] = 1;
        } else if (cr != r) goto fail;
        else touched[j] = 0;
        continue;
    fail:
        for (int k = 1; k < j; k++) if (touched[k]){
            int Pk = 1<<k;
            c->classres[k][i & (Pk-1)] = -1;
            c->resown[k][v & (Pk-1)] = -1;
        }
        return 0;
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

/* place value v at position i: head windows ending at i; if i <= S_, the
   forced partner sits at M+i and tail windows inside [M+1, M+i] are checked
   early.  Returns 0 if any violated. */
static inline int head_tail_ok(Ctx* c, int i, int v, int* w_out){
    long long s = c->pre[i-1] + v;
    int Lmax = i < n ? i : n-1;
    for (int L = 2; L <= Lmax; L++)
        if ((s - c->pre[i-L]) % L == 0) return 0;
    if (i > S_){ *w_out = 0; return 1; }  /* no forced partner */
    int w = v <= M ? v + M : v - M;
    if (w < 1 || w > n) return 0;         /* partner must exist for i<=S_ */
    long long s2 = c->pre2[i-1] + w;
    for (int L = 2; L <= i; L++)
        if ((s2 - c->pre2[i-L]) % L == 0) return 0;
    *w_out = w;
    return 1;
}

static void rec(Ctx* c, int i){
    if (i == M + 1){
        /* forced descent: a_{M+t} = partner(a_t) for t = 1..S_ */
        long long spre[300];
        memcpy(spre, c->pre, sizeof(long long)*(M+1));
        for (int p = M + 1; p <= n; p++){
            int u = c->a[p-M];
            int v = u <= M ? u + M : u - M;
            long long s = spre[p-1] + v;
            int Lmax = p < n ? p : n-1;
            for (int L = 2; L <= Lmax; L++)
                if ((s - spre[p-L]) % L == 0) return;
            spre[p] = s;
            c->a[p] = v;
        }
        c->sols++;
        #pragma omp critical
        {
            printf("SOL");
            for (int k=1;k<=n;k++) printf(" %d", c->a[k]);
            printf("\n"); fflush(stdout);
        }
        return;
    }
    for (int v=1; v<=n; v++){
        if (c->used[v]) continue;
        int w;
        if (!head_tail_ok(c, i, v, &w)) continue;
        int touched[7] = {0};
        if (!try_claim(c, i, v, touched)) continue;
        c->nodes++;
        c->used[v]=1; c->a[i]=v; c->pre[i]=c->pre[i-1]+v;
        if (i <= S_){ c->used[w]=1; c->pre2[i]=c->pre2[i-1]+w; }
        rec(c, i+1);
        c->used[v]=0;
        if (i <= S_) c->used[w]=0;
        unclaim(c, i, v, touched);
    }
}

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
    for (int v=1; v<=n; v++){
        if (c0->used[v]) continue;
        int w;
        if (!head_tail_ok(c0, i, v, &w)) continue;
        int touched[7] = {0};
        if (!try_claim(c0, i, v, touched)) continue;
        c0->used[v]=1; c0->a[i]=v; c0->pre[i]=c0->pre[i-1]+v;
        if (i <= S_){ c0->used[w]=1; c0->pre2[i]=c0->pre2[i-1]+w; }
        rec0(i+1);
        c0->used[v]=0;
        if (i <= S_) c0->used[w]=0;
        unclaim(c0, i, v, touched);
    }
}

int main(int argc, char** argv){
    n = argc>1 ? atoi(argv[1]) : 63;
    SPLIT = argc>2 ? atoi(argv[2]) : 8;
    M = 2; while (M*2 <= n-1) M *= 2;
    S_ = n - M;
    NJ = 0; while ((2 << NJ) <= n-1) NJ++;
    if (SPLIT > 15) SPLIT = 15;
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
        #pragma omp for schedule(dynamic,64)
        for (int t=0; t<np_pref; t++){
            memset(c->used, 0, n+1);
            memset(c->classres, -1, sizeof c->classres);
            memset(c->resown,  -1, sizeof c->resown);
            c->pre[0]=0; c->pre2[0]=0;
            int ok = 1;
            for (int k=1;k<=SPLIT && ok;k++){
                int v = plist[t].a[k-1];
                int touched[7]={0};
                c->a[k]=v; c->pre[k]=c->pre[k-1]+v; c->used[v]=1;
                if (k <= S_){
                    int w = v <= M ? v + M : v - M;
                    c->pre2[k]=c->pre2[k-1]+w; c->used[w]=1;
                }
                ok = try_claim(c, k, v, touched);
            }
            if (ok) rec(c, SPLIT+1);
            #pragma omp atomic
            done++;
            if ((done & 0xFFFFF)==0)
                fprintf(stderr,"prefix %d/%d  %.0fs\n", done, np_pref,
                        omp_get_wtime()-t0);
        }
        #pragma omp critical
        { total_sol += c->sols; total_nodes += c->nodes; }
        free(c);
    }
    printf("n=%d total_good=%lld nodes=%llu elapsed=%.0fs\n",
           n, total_sol, total_nodes, omp_get_wtime()-t0);
    return 0;
}
