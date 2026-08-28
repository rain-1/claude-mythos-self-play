/* MO 514678: permutations a_0..a_{2N} of {-N..N} with every consecutive
   triple (u,v,w) having disc = v^2 - 4uw a perfect square.

   Modes:
     ./perm  solve  N  [seed] [direct]   - find one solution
         mirror mode (default): find b_1..b_N with |b| a permutation of
         1..N, all internal triples good; output b (full perm is
         b + [0] + reversed(-b), all seam triples provably good).
         direct mode: find the full 2N+1 sequence over {-N..N} directly.
     ./perm  count  N                    - exhaustively count b-solutions
     ./perm  countfull N                 - exhaustively count full solutions
     ./perm  sweep  N0 N1 [seed]         - solve every N in [N0,N1], report

   Heuristic: Warnsdorff (fewest onward moves first) + bounded backtracking
   + randomized restarts.
   gcc -O3 -march=native perm514678.c -o perm -lm
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <time.h>

static uint64_t rngs;
static inline uint64_t rnd(void){ rngs ^= rngs<<13; rngs ^= rngs>>7; rngs ^= rngs<<17; return rngs; }

static inline int is_square(int64_t d){
    if (d < 0) return 0;
    int64_t r = (int64_t)sqrtl((long double)d);
    while (r*r > d) r--;
    while ((r+1)*(r+1) <= d) r++;
    return r*r == d;
}
static inline int64_t isqrt64(int64_t d){
    int64_t r = (int64_t)sqrtl((long double)d);
    while (r*r > d) r--;
    while ((r+1)*(r+1) <= d) r++;
    return r;
}

/* ---------------- generic sequencing engine ----------------
   Values: an array vals[0..M-1] of the M values to be sequenced.
   used[] over indices. Adjacent triple condition on values.        */

static int M;                 /* number of values in the pool */
static int64_t *vals;         /* the pool */
static unsigned char *used;
static int *seq;              /* indices into vals */
static int seqlen;
static long long backtracks, btlimit;

static inline int good(int64_t u, int64_t v, int64_t w){
    return is_square(v*v - 4*u*w);
}

/* candidate buffer per depth */
typedef struct { int idx; int deg; } Cand;

static int degree_of(int64_t u, int64_t v){
    /* onward moves from pair (u,v) among unused values */
    int d = 0;
    for (int i = 0; i < M; i++) if (!used[i] && good(u, v, vals[i])) d++;
    return d;
}

static int cmp_cand(const void *a, const void *b){
    const Cand *x = a, *y = b;
    if (x->deg != y->deg) return x->deg - y->deg;
    return 0;
}

static int dfs(int depth){
    if (depth == M) return 1;
    if (backtracks > btlimit) return -1;   /* abort -> restart */
    int64_t u = vals[seq[depth-2]], v = vals[seq[depth-1]];
    Cand cand[8192]; int nc = 0;
    for (int i = 0; i < M; i++)
        if (!used[i] && good(u, v, vals[i])) cand[nc++].idx = i;
    if (nc == 0){ backtracks++; return 0; }
    /* Warnsdorff: fewest onward continuations first (jittered) */
    for (int c = 0; c < nc; c++){
        used[cand[c].idx] = 1;
        cand[c].deg = (depth+1 == M) ? 0 : degree_of(v, vals[cand[c].idx]);
        used[cand[c].idx] = 0;
        cand[c].deg = cand[c].deg * 4 + (int)(rnd() & 3);
    }
    qsort(cand, nc, sizeof(Cand), cmp_cand);
    for (int c = 0; c < nc; c++){
        int i = cand[c].idx;
        used[i] = 1; seq[depth] = i;
        int r = dfs(depth+1);
        if (r) return r;                 /* 1 success, -1 abort */
        used[i] = 0;
    }
    backtracks++;
    return 0;
}

static int solve_pool(int64_t *pool, int m, uint64_t seed, int64_t *out){
    M = m; vals = pool;
    used = calloc(M,1); seq = malloc(sizeof(int)*M);
    rngs = seed ? seed : 0x9E3779B97F4A7C15ULL;
    for (int restart = 0; restart < 400; restart++){
        memset(used, 0, M);
        backtracks = 0;
        btlimit = 2000 + (long long)M * (20 + 30*restart);
        /* random ordered first pair */
        int i0 = (int)(rnd() % M), i1;
        do { i1 = (int)(rnd() % M); } while (i1 == i0);
        used[i0] = used[i1] = 1; seq[0] = i0; seq[1] = i1;
        int r = dfs(2);
        if (r == 1){
            for (int i = 0; i < M; i++) out[i] = vals[seq[i]];
            free(used); free(seq);
            return restart+1;
        }
    }
    free(used); free(seq);
    return 0;
}

/* build pools */
static int64_t *pool_signed(int N){       /* mirror mode: +-1..N, choose sign per |v| */
    /* pool holds both signs; the |value|-distinctness is enforced by
       marking both +m and -m used when one is taken.  We implement that
       by a paired-used trick: indices 2k (=+ (k+1)) and 2k+1 (= -(k+1)). */
    int64_t *p = malloc(sizeof(int64_t)*2*N);
    for (int k = 0; k < N; k++){ p[2*k] = k+1; p[2*k+1] = -(k+1); }
    return p;
}

/* mirror-mode dfs wrapper: uses pool of 2N but pairs share a "used" flag */
static int pair_of(int i){ return i ^ 1; }
static int dfs_m(int depth, int targetlen){
    if (depth == targetlen) return 1;
    if (backtracks > btlimit) return -1;
    int64_t u = vals[seq[depth-2]], v = vals[seq[depth-1]];
    Cand cand[8192]; int nc = 0;
    for (int i = 0; i < M; i++)
        if (!used[i] && !used[pair_of(i)] && good(u, v, vals[i])) cand[nc++].idx = i;
    if (nc == 0){ backtracks++; return 0; }
    for (int c = 0; c < nc; c++){
        int i = cand[c].idx;
        used[i] = 1;
        int d = 0;
        if (depth+1 < targetlen){
            int64_t vv = vals[i];
            for (int j = 0; j < M; j++)
                if (!used[j] && !used[pair_of(j)] && good(v, vv, vals[j])) d++;
        }
        used[i] = 0;
        int64_t aw = vals[i] < 0 ? -vals[i] : vals[i];
        cand[c].deg = d * 16 + (int)(rnd() & 3) + (int)(4 - (8*aw)/(M/2+1));
    }
    qsort(cand, nc, sizeof(Cand), cmp_cand);
    for (int c = 0; c < nc; c++){
        int i = cand[c].idx;
        used[i] = 1; seq[depth] = i;
        int r = dfs_m(depth+1, targetlen);
        if (r) return r;
        used[i] = 0;
    }
    backtracks++;
    return 0;
}

static int solve_mirror(int N, uint64_t seed, int64_t *out){
    int64_t *p = pool_signed(N);
    M = 2*N; vals = p;
    used = calloc(M,1); seq = malloc(sizeof(int)*N);
    rngs = seed ? seed : 0x9E3779B97F4A7C15ULL;
    for (int restart = 0; restart < 400; restart++){
        memset(used, 0, M);
        backtracks = 0;
        btlimit = (long long)N * 3000 * (1LL<<(restart<4?restart:4));
        int i0 = (int)(rnd() % M), i1;
        do { i1 = (int)(rnd() % M); } while ((i1>>1) == (i0>>1));
        used[i0] = used[i1] = 1; seq[0] = i0; seq[1] = i1;
        int r = dfs_m(2, N);
        if (r == 1){
            for (int i = 0; i < N; i++) out[i] = vals[seq[i]];
            free(used); free(seq); free(p);
            return restart+1;
        }
    }
    free(used); free(seq); free(p);
    return 0;
}

/* exhaustive count of mirror b-solutions (all first pairs, full DFS) */
static long long count_total;
static FILE *gdump = NULL;
static void dfs_count(int depth, int N){
    if (depth == N){
        count_total++;
        if (gdump){
            for (int i = 0; i < N; i++) fprintf(gdump, "%lld ", (long long)vals[seq[i]]);
            fprintf(gdump, "\n");
        }
        return;
    }
    int64_t u = vals[seq[depth-2]], v = vals[seq[depth-1]];
    for (int i = 0; i < M; i++)
        if (!used[i] && !used[pair_of(i)] && good(u, v, vals[i])){
            used[i] = 1; seq[depth] = i;
            dfs_count(depth+1, N);
            used[i] = 0;
        }
}
static long long count_mirror(int N){
    int64_t *p = pool_signed(N);
    M = 2*N; vals = p; used = calloc(M,1); seq = malloc(sizeof(int)*N);
    count_total = 0;
    for (int i0 = 0; i0 < M; i0++) for (int i1 = 0; i1 < M; i1++){
        if ((i1>>1) == (i0>>1)) continue;
        memset(used, 0, M);
        used[i0] = used[i1] = 1; seq[0] = i0; seq[1] = i1;
        dfs_count(2, N);
    }
    free(used); free(seq); free(p);
    return count_total;
}

/* exhaustive count of FULL solutions over {-N..N} (2N+1 values) */
static void dfs_countf(int depth, int L){
    if (depth == L){ count_total++; return; }
    int64_t u = vals[seq[depth-2]], v = vals[seq[depth-1]];
    for (int i = 0; i < M; i++)
        if (!used[i] && good(u, v, vals[i])){
            used[i] = 1; seq[depth] = i;
            dfs_countf(depth+1, L);
            used[i] = 0;
        }
}
static long long count_full(int N){
    int L = 2*N+1;
    int64_t *p = malloc(sizeof(int64_t)*L);
    for (int k = 0; k < L; k++) p[k] = k - N;
    M = L; vals = p; used = calloc(M,1); seq = malloc(sizeof(int)*L);
    count_total = 0;
    for (int i0 = 0; i0 < M; i0++) for (int i1 = 0; i1 < M; i1++){
        if (i1 == i0) continue;
        memset(used, 0, M);
        used[i0] = used[i1] = 1; seq[0] = i0; seq[1] = i1;
        dfs_countf(2, L);
    }
    free(used); free(seq); free(p);
    return count_total;
}

static void verify_and_print_full(int64_t *a, int L, const char *tag){
    for (int i = 1; i+1 < L; i++){
        int64_t d = a[i]*a[i] - 4*a[i-1]*a[i+1];
        if (!is_square(d)){ printf("VERIFY-FAIL at %d\n", i); exit(1); }
    }
    printf("%s VERIFIED L=%d:", tag, L);
    for (int i = 0; i < L; i++) printf(" %lld", (long long)a[i]);
    printf("\n");
}

int main(int argc, char **argv){
    if (argc < 3){ fprintf(stderr, "usage: see header\n"); return 1; }
    const char *mode = argv[1];
    if (!strcmp(mode, "solve")){
        int N = atoi(argv[2]);
        uint64_t seed = argc > 3 ? strtoull(argv[3],0,10) : 12345;
        int direct = argc > 4 && !strcmp(argv[4], "direct");
        clock_t t0 = clock();
        if (direct){
            int L = 2*N+1;
            int64_t *p = malloc(sizeof(int64_t)*L), *out = malloc(sizeof(int64_t)*L);
            for (int k = 0; k < L; k++) p[k] = k - N;
            int r = solve_pool(p, L, seed, out);
            double el = (double)(clock()-t0)/CLOCKS_PER_SEC;
            if (r){ printf("N=%d DIRECT restarts=%d time=%.2fs\n", N, r, el);
                    verify_and_print_full(out, L, "FULL"); }
            else printf("N=%d DIRECT FAILED (%.2fs)\n", N, el);
        } else {
            int64_t *b = malloc(sizeof(int64_t)*N);
            int r = solve_mirror(N, seed, b);
            double el = (double)(clock()-t0)/CLOCKS_PER_SEC;
            if (r){
                int L = 2*N+1;
                int64_t *a = malloc(sizeof(int64_t)*L);
                for (int i = 0; i < N; i++) a[i] = b[i];
                a[N] = 0;
                for (int i = 0; i < N; i++) a[N+1+i] = -b[N-1-i];
                printf("N=%d MIRROR restarts=%d time=%.2fs\n", N, r, el);
                verify_and_print_full(a, L, "FULL");
            } else printf("N=%d MIRROR FAILED (%.2fs)\n", N, el);
        }
    } else if (!strcmp(mode, "count")){
        int N = atoi(argv[2]);
        clock_t t0 = clock();
        long long c = count_mirror(N);
        printf("N=%d b-solutions=%lld (%.1fs)\n", N, c,
               (double)(clock()-t0)/CLOCKS_PER_SEC);
    } else if (!strcmp(mode, "countfull")){
        int N = atoi(argv[2]);
        clock_t t0 = clock();
        long long c = count_full(N);
        printf("N=%d full-solutions=%lld (%.1fs)\n", N, c,
               (double)(clock()-t0)/CLOCKS_PER_SEC);
    } else if (!strcmp(mode, "dump")){
        int N = atoi(argv[2]);
        int64_t *p = pool_signed(N);
        M = 2*N; vals = p; used = calloc(M,1); seq = malloc(sizeof(int)*N);
        count_total = 0;
        FILE *fd = fopen(argc>3?argv[3]:"dump.txt", "w");
        gdump = fd;
        for (int i0 = 0; i0 < M; i0++) for (int i1 = 0; i1 < M; i1++){
            if ((i1>>1) == (i0>>1)) continue;
            memset(used, 0, M);
            used[i0] = used[i1] = 1; seq[0] = i0; seq[1] = i1;
            dfs_count(2, N);
        }
        fclose(fd);
        printf("N=%d dumped %lld\n", N, count_total);
    } else if (!strcmp(mode, "sweep")){
        int N0 = atoi(argv[2]), N1 = atoi(argv[3]);
        uint64_t seed = argc > 4 ? strtoull(argv[4],0,10) : 777;
        int fails = 0;
        for (int N = N0; N <= N1; N++){
            clock_t t0 = clock();
            int64_t *b = malloc(sizeof(int64_t)*N);
            int r = solve_mirror(N, seed + N, b);
            double el = (double)(clock()-t0)/CLOCKS_PER_SEC;
            if (r) printf("N=%d ok restarts=%d %.2fs\n", N, r, el);
            else { printf("N=%d **FAILED** %.2fs\n", N, el); fails++; }
            fflush(stdout);
            free(b);
        }
        printf("sweep done, %d failures\n", fails);
    }
    return 0;
}
