/* MO 514678 generation-march v2: pool of full b-solution arrays.
   Level N -> N+1 by:
     (a) 1-step append: +-(N+1) at either end (after optional reversal);
     (b) 2-step append: unused helper x, then +-(N+1)  [the workhorse];
     (c) tail repair (rip k, re-lay with N+1) as last resort.
   b-solution: |b| = permutation of 1..N, all internal triples
   (u,v,w) have v^2 - 4uw a perfect square.  Full permutation of {-N..N}
   = b + [0] + reversed(-b)  (seam triples always good).
   Every emitted witness is re-verified from scratch.

   gcc -O3 -march=native march514678.c -o march -lm
   ./march NMAX POOLCAP SEED                                              */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

static uint64_t rngs = 20260828ULL;
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
static int verify_b(int16_t *b, int N){
    static unsigned char *seen = NULL; static int scap = 0;
    if (scap < N+1){ scap = N+1024; seen = realloc(seen, scap); }
    memset(seen, 0, N+1);
    for (int i = 0; i < N; i++){
        int a = b[i] < 0 ? -b[i] : b[i];
        if (a < 1 || a > N || seen[a]) return 0;
        seen[a] = 1;
    }
    for (int i = 1; i+1 < N; i++)
        if (!good(b[i-1], b[i], b[i+1])) return 0;
    return 1;
}

/* ---------- seed enumeration at N=12 (collect up to cap) ---------- */
static int16_t sseq[64]; static unsigned char sused[64];
static int16_t (*seeds)[12]; static long nseed; static long seedwant;
static void seed_dfs(int depth){
    if (nseed >= seedwant) return;
    if (depth == 12){ memcpy(seeds[nseed++], sseq, sizeof(int16_t)*12); return; }
    int64_t u = sseq[depth-2], v = sseq[depth-1];
    for (int m = 1; m <= 12; m++){
        if (sused[m]) continue;
        for (int s = -1; s <= 1; s += 2){
            int64_t w = (int64_t)s*m;
            if (good(u, v, w)){ sused[m]=1; sseq[depth]=(int16_t)w; seed_dfs(depth+1); sused[m]=0; }
        }
    }
}

/* ---------- tail-repair mini-DFS ---------- */
static int rep_k; static int rep_abs[64];
static unsigned char rep_used[64]; static int16_t rep_out[64];
static long rep_bt, rep_btlim;
static int rep_dfs(int depth, int64_t u, int64_t v){
    if (depth == rep_k) return 1;
    if (rep_bt > rep_btlim) return -1;
    int order[64];
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
    int NMAX = argc > 1 ? atoi(argv[1]) : 4096;
    int PCAP = argc > 2 ? atoi(argv[2]) : 128;
    rngs = argc > 3 ? strtoull(argv[3],0,10) : 20260828ULL;
    FILE *lg = fopen("march.log", "w");

    size_t stride = (size_t)NMAX + 4;
    int16_t *poolA = malloc(sizeof(int16_t)*PCAP*stride);
    int16_t *poolB = malloc(sizeof(int16_t)*2*PCAP*stride);
    int16_t *buf   = malloc(sizeof(int16_t)*stride);
    unsigned char *unused = malloc((size_t)NMAX+2);   /* abs values present? */

    /* seeds */
    seedwant = PCAP; seeds = malloc(sizeof(*seeds)*seedwant);
    for (int m1 = 1; m1 <= 12 && nseed < seedwant; m1++) for (int s1 = -1; s1 <= 1; s1 += 2)
    for (int m2 = 1; m2 <= 12 && nseed < seedwant; m2++) for (int s2 = -1; s2 <= 1; s2 += 2){
        if (m2 == m1) continue;
        memset(sused, 0, sizeof sused);
        sused[m1] = sused[m2] = 1;
        sseq[0] = (int16_t)(s1*m1); sseq[1] = (int16_t)(s2*m2);
        seed_dfs(2);
    }
    long np = nseed;
    for (long i = 0; i < np; i++) memcpy(poolA + i*stride, seeds[i], sizeof(int16_t)*12);
    fprintf(lg, "seeds=%ld\n", np); fflush(lg);

    for (int N = 13; N <= NMAX; N++){
        long nc = 0, n1 = 0, n2 = 0, nr = 0;
        long percap = 4;                       /* children cap per parent */
        for (long i = 0; i < np && nc < 2*PCAP; i++){
            int16_t *src = poolA + i*stride;
            int16_t *dst;
            long got = 0;
            /* copy with random orientation; b has length N-1 */
            int L = N-1;
            int16_t tmp[ /* VLA-free */ 8192 ];
            if (rnd() & 1) memcpy(tmp, src, sizeof(int16_t)*L);
            else for (int j = 0; j < L; j++) tmp[j] = src[L-1-j];
            int64_t p = tmp[L-2], q = tmp[L-1];
            /* (a) 1-step */
            for (int s = -1; s <= 1 && got < percap; s += 2){
                int64_t w = (int64_t)s*N;
                if (good(p, q, w) && nc < 2*PCAP){
                    dst = poolB + nc*stride;
                    memcpy(dst, tmp, sizeof(int16_t)*L);
                    dst[L] = (int16_t)w;
                    nc++; n1++; got++;
                }
            }
            /* (b) 2-step: helper x then +-N; scan helpers in random rotation */
            memset(unused, 0, N+1);
            for (int j = 0; j < L; j++){ int a = tmp[j]<0?-tmp[j]:tmp[j]; unused[a] = 1; }
            int start = (int)(rnd() % (N-1)) + 1;
            for (int dm = 0; dm < N-1 && got < percap; dm++){
                int m = 1 + (start + dm) % (N-1);   /* helper abs value 1..N-1 */
                if (unused[m]) continue;            /* wait: unused[]==1 means USED */
                for (int sx = -1; sx <= 1 && got < percap; sx += 2){
                    int64_t x = (int64_t)sx*m;
                    if (!good(p, q, x)) continue;
                    for (int s = -1; s <= 1 && got < percap; s += 2){
                        int64_t w = (int64_t)s*N;
                        if (good(q, x, w) && nc < 2*PCAP){
                            dst = poolB + nc*stride;
                            memcpy(dst, tmp, sizeof(int16_t)*L);
                            /* insert helper x, then N... but helper must be
                               re-added: sequence becomes length N+1 > N!  */
                            /* NO: helper x is an ALREADY-unused value ->
                               sequence b' = b + x would have N values but
                               |b'| misses N and duplicates nothing...
                               b has N-1 values (1..N-1 minus one? no: all
                               of 1..N-1). There are no unused helpers!   */
                            nc++; n2++; got++;
                        }
                    }
                }
            }
        }
        (void)0;
        /* --- the 2-step append needs a value bag redesign; see below --- */
        if (1){
            /* (b') PAIR-step: append two NEW values: impossible, only N is new.
               Real workhorse: INSERT +-N between any adjacent pair inside,
               3 triples to check, N-2 positions x 2 signs. */
            for (long i = 0; i < np && nc < 2*PCAP; i++){
                int16_t *src = poolA + i*stride;
                int L = N-1;
                long got = 0;
                for (int posr = 0; posr < L-1 && got < 2; posr++){
                    int pos = 1 + (int)((posr + (rnd()%(L-1))) % (L-1));
                    if (pos >= L) continue;
                    /* insert between pos-1 and pos */
                    int64_t A = pos>=2 ? src[pos-2] : 0;
                    int64_t Bv = src[pos-1], C = src[pos];
                    int64_t D = pos+1 < L ? src[pos+1] : 0;
                    for (int s = -1; s <= 1 && got < 2; s += 2){
                        int64_t w = (int64_t)s*N;
                        int ok = good(Bv, w, C);
                        if (ok && pos >= 2) ok = good(A, Bv, w);
                        if (ok && pos+1 < L) ok = good(w, C, D);
                        if (ok && nc < 2*PCAP){
                            int16_t *dst = poolB + nc*stride;
                            memcpy(dst, src, sizeof(int16_t)*pos);
                            dst[pos] = (int16_t)w;
                            memcpy(dst+pos+1, src+pos, sizeof(int16_t)*(L-pos));
                            nc++; n2++; got++;
                        }
                    }
                }
            }
        }
        /* (c) repair top-up */
        int rep_tries = 0;
        while (nc < PCAP && rep_tries < 3000 && np > 0){
            rep_tries++;
            int16_t *src = poolA + (rnd()%np)*stride;
            int L = N-1;
            memcpy(buf, src, sizeof(int16_t)*L);
            if (rnd() & 1)
                for (int x = 0, y = L-1; x < y; x++, y--){ int16_t t = buf[x]; buf[x] = buf[y]; buf[y] = t; }
            int k = 4 + (int)(rnd()%14);
            if (k > L-2) k = L-2;
            int keep = L - k;
            rep_k = k+1;
            for (int j = 0; j < k; j++){ int a = buf[keep+j]; rep_abs[j] = a<0?-a:a; }
            rep_abs[k] = N;
            memset(rep_used, 0, sizeof rep_used);
            rep_bt = 0; rep_btlim = 20000;
            int r = rep_dfs(0, buf[keep-2], buf[keep-1]);
            if (r == 1){
                int16_t *dst = poolB + nc*stride;
                memcpy(dst, buf, sizeof(int16_t)*keep);
                memcpy(dst+keep, rep_out, sizeof(int16_t)*rep_k);
                if (verify_b(dst, N)){ nc++; nr++; }
            }
        }
        if (nc == 0){
            fprintf(lg, "N=%d EXTINCT\n", N); fflush(lg);
            printf("EXTINCT at N=%d\n", N);
            return 2;
        }
        if (nc > PCAP){
            /* random subsample rows of poolB into first PCAP slots */
            for (long i = 0; i < PCAP; i++){
                long j = i + rnd()%(nc-i);
                if (j != i){
                    int16_t t[8192];
                    memcpy(t, poolB+i*stride, sizeof(int16_t)*N);
                    memcpy(poolB+i*stride, poolB+j*stride, sizeof(int16_t)*N);
                    memcpy(poolB+j*stride, t, sizeof(int16_t)*N);
                }
            }
            nc = PCAP;
        }
        for (long i = 0; i < nc; i++)
            memcpy(poolA + i*stride, poolB + i*stride, sizeof(int16_t)*N);
        np = nc;
        /* verify a random member each level */
        {
            int16_t *m = poolA + (rnd()%np)*stride;
            if (!verify_b(m, N)){
                fprintf(lg, "N=%d VERIFY FAIL\n", N); fflush(lg);
                printf("VERIFY FAIL at N=%d\n", N); return 3;
            }
        }
        int milestone = (N <= 200) || (N % 256 == 0) || (N == NMAX) || ((N & (N-1)) == 0);
        if (milestone){
            if (!verify_b(poolA, N)){ printf("VERIFY FAIL milestone N=%d\n", N); return 3; }
            char fn[64]; snprintf(fn, 64, "witness_%05d.txt", N);
            FILE *fw = fopen(fn, "w");
            for (int i = 0; i < N; i++) fprintf(fw, "%d ", (int)poolA[i]);
            fprintf(fw, "\n"); fclose(fw);
        }
        fprintf(lg, "N=%d pool=%ld app1=%ld ins=%ld rep=%ld\n", N, np, n1, n2, nr);
        if (N % 32 == 0) fflush(lg);
    }
    fflush(lg);
    printf("MARCH COMPLETE to N=%d\n", NMAX);
    return 0;
}
