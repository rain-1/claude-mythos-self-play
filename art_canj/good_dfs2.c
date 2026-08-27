/* MO 514690 v2: parallel exhaustive DFS for good permutations of {1..n}.
   Pruning:
     (a) incremental window checks (every window ending at i, early break)
     (b) dyadic residue filter: v ≡ a_{i-2^j} (mod 2^j) for the largest
         2^j ≤ min(i-1, n-1)  [consequence of window conditions]
     (c) zero-class filter: (i ≡ 0 mod 2^j) ⟺ (v ≡ 0 mod 2^j) for all
         2^j ≤ n-1  [forced by counting: both classes have ⌊n/2^j⌋ elements]
   Parallel: enumerate all valid prefixes of length SPLIT serially, then
   OpenMP dynamic loop over prefixes.
   gcc -O3 -march=native -fopenmp good_dfs2.c -o good_dfs2 -lm
   ./good_dfs2 n [split]                                                  */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>

static int n, SPLIT, PMAXZ; /* PMAXZ = largest power of 2 <= n-1 */

typedef struct { int a[24]; } Prefix;
static Prefix *plist; static int np_pref = 0, cap_pref = 0;

static long long total_sol = 0;
static unsigned long long total_nodes = 0;

static inline int zero_class_ok(int i, int v){
    for (int P = 2; P <= PMAXZ; P <<= 1)
        if (((i % P) == 0) != ((v % P) == 0)) return 0;
    return 1;
}

/* serial prefix enumeration */
static int a0[300]; static long long pre0[300]; static uint8_t used0[300];
static void rec0(int i){
    if (i > SPLIT){
        if (np_pref == cap_pref){
            cap_pref = cap_pref ? cap_pref*2 : 1024;
            plist = realloc(plist, sizeof(Prefix)*cap_pref);
        }
        for (int k=1;k<=SPLIT;k++) plist[np_pref].a[k-1] = a0[k];
        np_pref++;
        return;
    }
    int P = 0;
    for (int p2=2; p2<=i-1 && p2<=n-1; p2<<=1) P = p2;
    for (int v=1; v<=n; v++){
        if (used0[v]) continue;
        if (!zero_class_ok(i, v)) continue;
        if (P && ((v - a0[i-P]) & (P-1))) continue;
        long long s = pre0[i-1] + v;
        int ok = 1, Lmax = i<n ? i : n-1;
        for (int L=2; L<=Lmax; L++)
            if ((s - pre0[i-L]) % L == 0){ ok=0; break; }
        if (!ok) continue;
        used0[v]=1; a0[i]=v; pre0[i]=s;
        rec0(i+1);
        used0[v]=0;
    }
}

typedef struct { int a[300]; long long pre[300]; uint8_t used[300];
                 long long sols; unsigned long long nodes; } Ctx;

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
    int P = 0;
    for (int p2=2; p2<=i-1 && p2<=n-1; p2<<=1) P = p2;
    for (int v=1; v<=n; v++){
        if (c->used[v]) continue;
        if (!zero_class_ok(i, v)) continue;
        if (P && ((v - c->a[i-P]) & (P-1))) continue;
        long long s = c->pre[i-1] + v;
        int ok = 1, Lmax = i<n ? i : n-1;
        for (int L=2; L<=Lmax; L++)
            if ((s - c->pre[i-L]) % L == 0){ ok=0; break; }
        if (!ok) continue;
        c->nodes++;
        c->used[v]=1; c->a[i]=v; c->pre[i]=s;
        rec(c, i+1);
        c->used[v]=0;
    }
}

int main(int argc, char** argv){
    n = argc>1 ? atoi(argv[1]) : 63;
    SPLIT = argc>2 ? atoi(argv[2]) : 12;
    PMAXZ = 2; while (PMAXZ*2 <= n-1) PMAXZ *= 2;
    double t0 = omp_get_wtime();
    pre0[0]=0;
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
            c->pre[0]=0;
            int ok=1;
            for (int k=1;k<=SPLIT;k++){
                int v = plist[t].a[k-1];
                c->a[k]=v; c->pre[k]=c->pre[k-1]+v; c->used[v]=1;
            }
            if (ok) rec(c, SPLIT+1);
            #pragma omp atomic
            done++;
            if ((done & 1023)==0)
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
