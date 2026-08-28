/* MO 514678 generation-march: maintain a pool of b-solutions for level N
   (b_1..b_N, |b| a permutation of 1..N, every internal triple
   (u,v,w) has v^2-4uw a perfect square), advance N -> N+1 by
   (a) appending +-(N+1) at either end (1 new triple to check),
   (b) tail-repair top-up: rip k tail values off a pool member, mini-DFS
       re-lay them together with (N+1) (signs free).
   Every solution emitted is re-verified from scratch.

   gcc -O3 -march=native pool514678.c -o pool -lm
   ./pool NMAX POOLCAP SEED
   output: pool_march.log (per-N stats), pool_witness_N.txt (milestones)   */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

static uint64_t rngs = 88172645463325252ULL;
static inline uint64_t rnd(void){ rngs ^= rngs<<13; rngs ^= rngs>>7; rngs ^= rngs<<17; return rngs; }

static inline int is_square(int64_t d){
    if (d < 0) return 0;
    int64_t r = (int64_t)sqrtl((long double)d);
    while (r*r > d) r--;
    while ((r+1)*(r+1) <= d) r++;
    return r*r == d;
}
static inline int good(int64_t u, int64_t v, int64_t w){
    return is_square(v*v - 4*u*w);
}

/* ---------- persistent deque tree ---------- */
typedef struct {
    int32_t parent;      /* -1 => root */
    int32_t rootid;      /* valid for roots */
    int16_t val;         /* appended value (signed) */
    int8_t  side;        /* 0 = back, 1 = front */
    int16_t f1, f2, b2, b1;  /* seq[0], seq[1], seq[len-2], seq[len-1] */
} Node;

static Node *nodes; static long ncap, nn;
static int16_t **roots; static int *rootlen; static long nroots, rcap;

static long new_root(int16_t *seq, int len){
    if (nroots == rcap){ rcap = rcap? rcap*2 : 1024; roots = realloc(roots, rcap*sizeof(void*)); rootlen = realloc(rootlen, rcap*sizeof(int)); }
    int16_t *cp = malloc(sizeof(int16_t)*len); memcpy(cp, seq, sizeof(int16_t)*len);
    roots[nroots] = cp; rootlen[nroots] = len;
    if (nn == ncap){ ncap = ncap? ncap*2 : 1<<20; nodes = realloc(nodes, ncap*sizeof(Node)); }
    Node *nd = &nodes[nn];
    nd->parent = -1; nd->rootid = (int32_t)nroots; nd->side = 0; nd->val = 0;
    nd->f1 = seq[0]; nd->f2 = len>1? seq[1] : 0;
    nd->b1 = seq[len-1]; nd->b2 = len>1? seq[len-2] : 0;
    nroots++;
    return nn++;
}
static long new_child(long p, int16_t w, int side){
    if (nn == ncap){ ncap *= 2; nodes = realloc(nodes, ncap*sizeof(Node)); }
    Node *par = &nodes[p]; Node *nd = &nodes[nn];
    nd->parent = (int32_t)p; nd->rootid = -1; nd->val = w; nd->side = (int8_t)side;
    if (side == 0){ nd->f1 = par->f1; nd->f2 = par->f2; nd->b2 = par->b1; nd->b1 = w; }
    else          { nd->b1 = par->b1; nd->b2 = par->b2; nd->f2 = par->f1; nd->f1 = w; }
    return nn++;
}
static int reconstruct(long id, int16_t *out, int N){
    /* returns length; walks ancestry, fills deque */
    static int16_t *back = NULL, *front = NULL; static int cap = 0;
    if (cap < N+8){ cap = N+8; back = realloc(back, sizeof(int16_t)*cap); front = realloc(front, sizeof(int16_t)*cap); }
    int nb = 0, nf = 0;
    long cur = id;
    while (nodes[cur].parent >= 0){
        if (nodes[cur].side == 0) back[nb++] = nodes[cur].val;
        else front[nf++] = nodes[cur].val;
        cur = nodes[cur].parent;
    }
    int rid = nodes[cur].rootid, rl = rootlen[rid], L = 0;
    for (int i = 0; i < nf; i++) out[L++] = front[i];
    for (int i = 0; i < rl; i++) out[L++] = roots[rid][i];
    for (int i = nb-1; i >= 0; i--) out[L++] = back[i];
    return L;
}
static int verify_b(int16_t *b, int N){
    unsigned char *seen = calloc(N+1, 1);
    for (int i = 0; i < N; i++){
        int a = b[i] < 0 ? -b[i] : b[i];
        if (a < 1 || a > N || seen[a]){ free(seen); return 0; }
        seen[a] = 1;
    }
    free(seen);
    for (int i = 1; i+1 < N; i++)
        if (!good(b[i-1], b[i], b[i+1])) return 0;
    return 1;
}

/* ---------- seed enumeration (exhaustive small N) ---------- */
static int16_t sseq[64]; static unsigned char sused[64];
static long *seedlist; static long nseed, seedcap; static int SEEDN;
static void seed_dfs(int depth){
    if (depth == SEEDN){
        if (nseed == seedcap){ seedcap *= 2; seedlist = realloc(seedlist, seedcap*sizeof(long)); }
        seedlist[nseed++] = new_root(sseq, SEEDN);
        return;
    }
    int64_t u = sseq[depth-2], v = sseq[depth-1];
    for (int m = 1; m <= SEEDN; m++){
        if (sused[m]) continue;
        for (int s = -1; s <= 1; s += 2){
            int64_t w = (int64_t)s*m;
            if (good(u, v, w)){ sused[m]=1; sseq[depth]=(int16_t)w; seed_dfs(depth+1); sused[m]=0; }
        }
    }
}

/* ---------- tail-repair mini-DFS ---------- */
static int rep_k;              /* number of values to lay */
static int rep_abs[40];        /* their absolute values */
static unsigned char rep_used[40];
static int16_t rep_out[40];
static long rep_bt, rep_btlim;
static int rep_dfs(int depth, int64_t u, int64_t v){
    if (depth == rep_k) return 1;
    if (rep_bt > rep_btlim) return -1;
    int order[40];
    for (int i = 0; i < rep_k; i++) order[i] = i;
    for (int i = rep_k-1; i > 0; i--){ int j = (int)(rnd()%(i+1)); int t=order[i]; order[i]=order[j]; order[j]=t; }
    for (int oi = 0; oi < rep_k; oi++){
        int i = order[oi];
        if (rep_used[i]) continue;
        for (int s = -1; s <= 1; s += 2){
            int64_t w = (int64_t)s*rep_abs[i];
            if (good(u, v, w)){
                rep_used[i] = 1; rep_out[depth] = (int16_t)w;
                int r = rep_dfs(depth+1, v, w);
                if (r) return r;
                rep_used[i] = 0;
            }
        }
    }
    rep_bt++;
    return 0;
}

int main(int argc, char **argv){
    int NMAX   = argc > 1 ? atoi(argv[1]) : 4096;
    int PCAP   = argc > 2 ? atoi(argv[2]) : 8192;
    rngs = argc > 3 ? strtoull(argv[3],0,10) : 20260828ULL;
    FILE *lg = fopen("pool_march.log", "w");

    /* seed at N=12 exhaustively */
    SEEDN = 12;
    seedcap = 1024; seedlist = malloc(seedcap*sizeof(long));
    for (int m1 = 1; m1 <= SEEDN; m1++) for (int s1 = -1; s1 <= 1; s1 += 2)
    for (int m2 = 1; m2 <= SEEDN; m2++) for (int s2 = -1; s2 <= 1; s2 += 2){
        if (m2 == m1) continue;
        memset(sused, 0, sizeof sused);
        sused[m1] = sused[m2] = 1;
        sseq[0] = (int16_t)(s1*m1); sseq[1] = (int16_t)(s2*m2);
        seed_dfs(2);
    }
    fprintf(lg, "N=12 seeds=%ld\n", nseed); fflush(lg);

    long *pool = malloc(sizeof(long)*PCAP), np = 0;
    long *newp = malloc(sizeof(long)*(2*PCAP+8));
    for (long i = 0; i < nseed && np < PCAP; i++) pool[np++] = seedlist[i];
    int16_t *buf = malloc(sizeof(int16_t)*(NMAX+8));
    int16_t *buf2 = malloc(sizeof(int16_t)*(NMAX+8));

    for (int N = SEEDN+1; N <= NMAX; N++){
        long nc = 0, from_append = 0, from_repair = 0;
        /* (a) appends */
        for (long i = 0; i < np && nc < 2*PCAP; i++){
            int16_t cf1 = nodes[pool[i]].f1, cf2 = nodes[pool[i]].f2;
            int16_t cb1 = nodes[pool[i]].b1, cb2 = nodes[pool[i]].b2;
            for (int s = -1; s <= 1; s += 2){
                int64_t w = (int64_t)s*N;
                if (good(cb2, cb1, w)) newp[nc++] = new_child(pool[i], (int16_t)w, 0);
                if (good(cf2, cf1, w)) newp[nc++] = new_child(pool[i], (int16_t)w, 1);
            }
        }
        from_append = nc;
        /* (b) repair top-up */
        long want = PCAP;
        int rep_tries = 0;
        while (nc < want && rep_tries < 4000 && np > 0){
            rep_tries++;
            long src = pool[rnd()%np];
            int L = reconstruct(src, buf, N);
            if (L != N-1) { fprintf(lg, "BUG reconstruct L=%d N=%d\n", L, N); break; }
            if (rnd() & 1)   /* reversal is free: churn BOTH ends over time */
                for (int x = 0, y = L-1; x < y; x++, y--){ int16_t t = buf[x]; buf[x] = buf[y]; buf[y] = t; }
            int k = 4 + (int)(rnd()%12);     /* rip 4..15 tail values */
            if (k > N-3) k = N-3;
            int keep = (N-1) - k;
            rep_k = k+1;
            for (int j = 0; j < k; j++){ int a = buf[keep+j]; rep_abs[j] = a<0?-a:a; }
            rep_abs[k] = N;
            memset(rep_used, 0, sizeof rep_used);
            rep_bt = 0; rep_btlim = 30000;
            int r = rep_dfs(0, keep>=2? buf[keep-2] : 0, keep>=1? buf[keep-1] : 0);
            /* note: keep>=2 guaranteed since N-1-k >= 2 */
            if (r == 1){
                memcpy(buf2, buf, sizeof(int16_t)*keep);
                memcpy(buf2+keep, rep_out, sizeof(int16_t)*rep_k);
                if (verify_b(buf2, N)){
                    newp[nc++] = new_root(buf2, N);
                    from_repair++;
                }
            }
        }
        if (nc == 0){
            fprintf(lg, "N=%d EXTINCT (append=0, repairs failed)\n", N);
            fflush(lg);
            printf("EXTINCT at N=%d\n", N);
            return 2;
        }
        /* subsample to PCAP */
        if (nc > PCAP){
            for (long i = nc-1; i > 0; i--){ long j = rnd()%(i+1); long t=newp[i]; newp[i]=newp[j]; newp[j]=t; }
            nc = PCAP;
        }
        memcpy(pool, newp, sizeof(long)*nc); np = nc;
        int milestone = (N <= 200) || (N % 256 == 0) || (N == NMAX) ||
                        ((N & (N-1)) == 0);
        /* verify one member every level (cheap safety) */
        {
            int L = reconstruct(pool[rnd()%np], buf, N+1);
            if (L != N || !verify_b(buf, N)){
                fprintf(lg, "N=%d VERIFY-FAIL\n", N); fflush(lg);
                printf("VERIFY FAIL at N=%d\n", N); return 3;
            }
        }
        if (milestone){
            char fn[64]; snprintf(fn, 64, "pool_witness_%d.txt", N);
            FILE *fw = fopen(fn, "w");
            int L = reconstruct(pool[0], buf, N+1);
            if (L != N || !verify_b(buf, N)){ printf("VERIFY FAIL milestone N=%d\n", N); return 3; }
            for (int i = 0; i < N; i++) fprintf(fw, "%d ", (int)buf[i]);
            fprintf(fw, "\n"); fclose(fw);
        }
        fprintf(lg, "N=%d pool=%ld append=%ld repair=%ld\n", N, np, from_append, from_repair);
        if (N % 64 == 0) fflush(lg);
    }
    fflush(lg);
    printf("MARCH COMPLETE to N=%d\n", NMAX);
    return 0;
}
