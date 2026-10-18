/* Plugin for nauty's genposetg: for every poset P (Hasse diagram, topological
   labelling, edge i->j means i<j is a cover with i<j as integers) compute
   e(P) = #linear extensions (DP over down-sets) and #Aut(P) (backtracking with
   twin-class reduction), and keep the TOPK largest values of f = e/#Aut with
   all posets attaining them.  Nothing is written to stdout (we return from
   POSET_PRUNE1); results are printed in POSET_SUMMARY to stderr.
   Compile:  gcc -O3 -march=native -o genposet_f -DPLUGIN='"posetplugin.c"' \
              genposetg.c gtoolsS.o nauty S1 objects (see build.sh)              */

#define TOPK 4
#define MAXKEEP 200
typedef unsigned long long u64;
typedef unsigned __int128 u128;

static u64 top_e[TOPK], top_a[TOPK];     /* f-values as fractions e/a, sorted desc */
static int top_cnt[TOPK];
static int ntop = 0;
static setword keep[TOPK][MAXKEEP][MAXN];
static int keep_n;
static long long n_aut_calls = 0;
static u64 last_e;

/* DP buffers */
static u64 dpv[1 << MAXN];
static int stamp[1 << MAXN];
static int curstamp = 0;
static int lvl[2][1 << MAXN];

static setword DN[MAXN], UP[MAXN];   /* strict down/up closures */

static u64 count_linext(int n)
{
    /* down-sets processed by size; pred[j] = DN[j] */
    int a = 0, na = 1, nb, s, t, j;
    curstamp++;
    if (curstamp == 0x7fffffff) { memset(stamp, 0, sizeof(stamp)); curstamp = 1; }
    lvl[0][0] = 0; dpv[0] = 1;
    for (s = 0; s < n; ++s) {
        nb = 0;
        int *cur = lvl[a], *nxt = lvl[a ^ 1];
        curstamp++;
        for (t = 0; t < na; ++t) {
            int m = cur[t]; u64 v = dpv[m];
            for (j = 0; j < n; ++j) {
                if (m & (1 << j)) continue;
                if ((DN[j] & ~m) != 0) continue;
                int m2 = m | (1 << j);
                if (stamp[m2] != curstamp) { stamp[m2] = curstamp; dpv[m2] = 0; nxt[nb++] = m2; }
                dpv[m2] += v;
            }
        }
        /* dpv of previous level no longer needed */
        a ^= 1; na = nb;
    }
    return dpv[(1 << n) - 1];
}

/* automorphisms */
static int inv[MAXN], cls[MAXN], img[MAXN], used_[MAXN];
static int classrep_prev[MAXN];  /* previous member of same twin class, or -1 */
static int nn;
static u64 autcount;

static void aut_bt(int i)
{
    if (i == nn) { autcount++; return; }
    int v;
    int lo = 0;
    if (classrep_prev[i] >= 0) lo = img[classrep_prev[i]] + 1;
    for (v = lo; v < nn; ++v) {
        if (used_[v] || inv[v] != inv[i]) continue;
        if (classrep_prev[i] >= 0 && cls[v] != cls[img[classrep_prev[i]]]) continue;
        int ok = 1, k;
        for (k = 0; k < i; ++k) {
            int w = img[k];
            int a1 = (DN[i] >> k) & 1, b1 = (DN[v] >> w) & 1;
            int a2 = (UP[i] >> k) & 1, b2 = (UP[v] >> w) & 1;
            if (a1 != b1 || a2 != b2) { ok = 0; break; }
        }
        if (!ok) continue;
        used_[v] = 1; img[i] = v;
        aut_bt(i + 1);
        used_[v] = 0;
    }
}

static u64 count_aut(setword *h, int n)
{
    int i, j;
    n_aut_calls++;
    nn = n;
    int ncov_up[MAXN], ncov_dn[MAXN];
    for (i = 0; i < n; ++i) { ncov_up[i] = POPCOUNT(h[i]); ncov_dn[i] = 0; }
    for (i = 0; i < n; ++i) for (j = 0; j < n; ++j) if (h[i] & bit[j]) ncov_dn[j]++;
    /* invariant: combine; plus refine once with neighbor invariant sums */
    long long base[MAXN];
    for (i = 0; i < n; ++i)
        base[i] = ((long long)POPCOUNT(UP[i]) << 24) | (POPCOUNT(DN[i]) << 16) | (ncov_up[i] << 8) | ncov_dn[i];
    long long ref[MAXN];
    for (i = 0; i < n; ++i) {
        long long su = 0, sd = 0;
        for (j = 0; j < n; ++j) {
            if (h[i] & bit[j]) su += base[j] * 1000003LL + 7;
            if (h[j] & bit[i]) sd += base[j] * 998244353LL + 13;
        }
        ref[i] = base[i] * 31 + su * 17 + sd;
    }
    /* compress ref to small ints */
    for (i = 0; i < n; ++i) { inv[i] = i; for (j = 0; j < i; ++j) if (ref[j] == ref[i]) { inv[i] = inv[j]; break; } }
    /* twin classes: same DN and UP */
    u64 fact = 1;
    for (i = 0; i < n; ++i) {
        cls[i] = i; classrep_prev[i] = -1;
        for (j = i - 1; j >= 0; --j) if (DN[j] == DN[i] && UP[j] == UP[i]) { cls[i] = cls[j]; classrep_prev[i] = j; break; }
        int sz = 1; for (j = 0; j < i; ++j) if (cls[j] == cls[i]) sz++;
        fact *= sz;
    }
    for (i = 0; i < n; ++i) used_[i] = 0;
    autcount = 0;
    aut_bt(0);
    return autcount * fact;
}

/* compare e1/a1 with e2/a2 : returns sign */
static int fcmp(u64 e1, u64 a1, u64 e2, u64 a2)
{
    u128 l = (u128)e1 * a2, r = (u128)e2 * a1;
    return (l > r) - (l < r);
}

static void consider(setword *h, int n)
{
    int i, j;
    keep_n = n;
    /* closures: topological order, edges i->j with i<j */
    for (i = n - 1; i >= 0; --i) {
        setword u = h[i], w = h[i];
        while (w) { TAKEBIT(j, w); u |= UP[j]; }
        UP[i] = u;
    }
    for (i = 0; i < n; ++i) DN[i] = 0;
    for (i = 0; i < n; ++i) { setword w = UP[i]; while (w) { TAKEBIT(j, w); DN[j] |= bit[i]; } }
    /* nauty's bit[] is MSB-first; convert to LSB-first ints for the DP */
    setword DNl[MAXN], UPl[MAXN];
    for (i = 0; i < n; ++i) {
        setword d = 0, u = 0;
        for (j = 0; j < n; ++j) { if (DN[i] & bit[j]) d |= (1u << j); if (UP[i] & bit[j]) u |= (1u << j); }
        DNl[i] = d; UPl[i] = u;
    }
    for (i = 0; i < n; ++i) { DN[i] = DNl[i]; UP[i] = UPl[i]; }
    u64 e = count_linext(n);
    last_e = e;
    if (ntop == TOPK && fcmp(e, 1, top_e[TOPK - 1], top_a[TOPK - 1]) < 0) return;
    u64 a = count_aut(h, n);
    int pos;
    for (pos = 0; pos < ntop; ++pos) {
        int c = fcmp(e, a, top_e[pos], top_a[pos]);
        if (c == 0) {
            if (top_cnt[pos] < MAXKEEP) memcpy(keep[pos][top_cnt[pos]], h, sizeof(setword) * n);
            top_cnt[pos]++;
            return;
        }
        if (c > 0) break;
    }
    if (pos == TOPK) return;
    /* insert at pos */
    int last = (ntop < TOPK) ? ntop : TOPK - 1;
    for (i = last; i > pos; --i) {
        top_e[i] = top_e[i - 1]; top_a[i] = top_a[i - 1]; top_cnt[i] = top_cnt[i - 1];
        memcpy(keep[i], keep[i - 1], sizeof(keep[i]));
    }
    top_e[pos] = e; top_a[pos] = a; top_cnt[pos] = 1;
    memcpy(keep[pos][0], h, sizeof(setword) * n);
    if (ntop < TOPK) ntop++;
}

/* ---- connected posets: keep the TOPC best individual posets by e/aut ---- */
#define TOPC 60
static u64 tc_e[TOPC], tc_a[TOPC];
static setword tc_p[TOPC][MAXN];
static int ntc = 0;
static long long nconn = 0;

static int is_connected(setword *h, int n)
{
    /* h in nauty bit order; BFS over undirected cover graph */
    setword und[MAXN]; int i, j;
    for (i = 0; i < n; ++i) und[i] = h[i];
    for (i = 0; i < n; ++i) for (j = 0; j < n; ++j) if (h[i] & bit[j]) und[j] |= bit[i];
    setword seen = bit[0], frontier = bit[0];
    while (frontier) {
        setword nf = 0, w = frontier;
        while (w) { TAKEBIT(j, w); nf |= und[j]; }
        nf &= ~seen; seen |= nf; frontier = nf;
    }
    return seen == ALLMASK(n);
}

static void consider_conn(setword *h, int n, u64 e)
{
    int i;
    nconn++;
    if (ntc == TOPC && fcmp(e, 1, tc_e[TOPC - 1], tc_a[TOPC - 1]) < 0) return;
    u64 a = count_aut(h, n);
    if (ntc == TOPC && fcmp(e, a, tc_e[TOPC - 1], tc_a[TOPC - 1]) <= 0) return;
    int pos = (ntc < TOPC) ? ntc : TOPC - 1;
    while (pos > 0 && fcmp(e, a, tc_e[pos - 1], tc_a[pos - 1]) > 0) {
        tc_e[pos] = tc_e[pos - 1]; tc_a[pos] = tc_a[pos - 1];
        memcpy(tc_p[pos], tc_p[pos - 1], sizeof(tc_p[pos]));
        pos--;
    }
    tc_e[pos] = e; tc_a[pos] = a; memcpy(tc_p[pos], h, sizeof(setword) * n);
    if (ntc < TOPC) ntc++;
}

#define POSET_PRUNE1(pos,n) { consider(pos,n); if (is_connected(pos,n)) consider_conn(pos,n,last_e); return; }

#define POSET_SUMMARY { int r_, s_, i_, j_; \
    fprintf(stderr, "AUTCALLS %lld\n", n_aut_calls); \
    for (r_ = 0; r_ < ntop; ++r_) { \
        fprintf(stderr, "RANK %d e %llu aut %llu count %d\n", r_, top_e[r_], top_a[r_], top_cnt[r_]); \
        for (s_ = 0; s_ < top_cnt[r_] && s_ < MAXKEEP; ++s_) { \
            fprintf(stderr, "POSET"); \
            for (i_ = 0; i_ < keep_n; ++i_) for (j_ = 0; j_ < keep_n; ++j_) \
                if (keep[r_][s_][i_] & bit[j_]) fprintf(stderr, " %d,%d", i_, j_); \
            fprintf(stderr, "\n"); } } \
    fprintf(stderr, "NCONN %lld\n", nconn); \
    for (r_ = 0; r_ < ntc; ++r_) { \
        fprintf(stderr, "CONN e %llu aut %llu :", tc_e[r_], tc_a[r_]); \
        for (i_ = 0; i_ < keep_n; ++i_) for (j_ = 0; j_ < keep_n; ++j_) \
            if (tc_p[r_][i_] & bit[j_]) fprintf(stderr, " %d,%d", i_, j_); \
        fprintf(stderr, "\n"); } }
