// Wide-board version (n <= 16) of the square-game solver: "can X (first player) force a win
// within d of its own moves?" Same sound rules as sqgame.c (immediate win, forced block,
// double threat, Erdos-Selfridge, min-moves bound, dead-cell skipping for both sides).
// Board kept as per-cell array + per-square counts updated incrementally.
// TT keyed by a 128-bit Zobrist hash minimised over the 8 board symmetries (probabilistic key,
// collision probability ~ entries*lookups/2^128 -- negligible).
// Usage: ./sqwide n d [tt_log2] [timelimit] [iterate_from]
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
typedef uint64_t u64;
#define INF 31
#define MAXC 256
#define MAXSQ 1400
static int N, NC, NSQ;
static int sqc[MAXSQ][4];
static int cellSq[MAXC][64], cellSqN[MAXC];
static int cntX[MAXSQ], cntO[MAXSQ];
static char bd[MAXC];
static int nX, nO;
static u64 Z1[8][MAXC][2], Z2[8][MAXC][2], H1[8], H2[8];
static long long nodes;
static double tstart, tlimit = 1e18; static int timeout_flag;
static double now() { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec * 1e-9; }
static u64 rng = 88172645463325252ULL;
static u64 rnd() { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng * 0x2545F4914F6CDD1DULL; }

typedef struct { u64 a, b; uint32_t info; } Ent;
static Ent *TT; static u64 TTmask; static long long ttStores;
#define BUCKET 4
#define WINNONE 31
static Ent *ttFind(u64 a, u64 b) {
  Ent *e = &TT[(a & TTmask) * BUCKET];
  for (int k = 0; k < BUCKET; k++) if (e[k].info && e[k].a == a && e[k].b == b) return &e[k];
  return NULL;
}
static void ttStore(u64 a, u64 b, int w, int f) {
  Ent *e = ttFind(a, b);
  if (e) { int w0 = e->info & 31, f0 = (e->info >> 5) & 31; if (w < w0) w0 = w; if (f > f0) f0 = f; e->info = w0 | (f0 << 5) | (1u << 31); return; }
  ttStores++;
  Ent *bk = &TT[(a & TTmask) * BUCKET]; int best = 0, bs = 1 << 30;
  for (int k = 0; k < BUCKET; k++) {
    if (!bk[k].info) { best = k; break; }
    int w0 = bk[k].info & 31, f0 = (bk[k].info >> 5) & 31, sc = (w0 != WINNONE ? 32 - w0 : 0) + f0;
    if (sc < bs) { bs = sc; best = k; }
  }
  bk[best].a = a; bk[best].b = b; bk[best].info = w | (f << 5) | (1u << 31);
}

static void setup(int n) {
  N = n; NC = n * n; NSQ = 0;
  for (int s = 1; s < n; s++) for (int r = 0; r + s < n; r++) for (int c = 0; c + s < n; c++) {
    int *q = sqc[NSQ++]; q[0] = r*n+c; q[1] = r*n+c+s; q[2] = (r+s)*n+c; q[3] = (r+s)*n+c+s; }
  for (int q = 0; q < NSQ; q++) for (int k = 0; k < 4; k++) { int i = sqc[q][k]; cellSq[i][cellSqN[i]++] = q; }
  u64 b1[MAXC][2], b2[MAXC][2];
  for (int i = 0; i < NC; i++) for (int p = 0; p < 2; p++) { b1[i][p] = rnd(); b2[i][p] = rnd(); }
  for (int r = 0; r < n; r++) for (int c = 0; c < n; c++) {
    int i = r*n+c;
    int rr[8] = {r, c, n-1-r, n-1-c, r, n-1-r, c, n-1-c}, cc[8] = {c, n-1-r, n-1-c, r, n-1-c, c, r, n-1-r};
    for (int s = 0; s < 8; s++) for (int p = 0; p < 2; p++) { Z1[s][i][p] = b1[rr[s]*n+cc[s]][p]; Z2[s][i][p] = b2[rr[s]*n+cc[s]][p]; }
  }
}
static inline void play(int i, int p) { // p: 0 = X, 1 = O
  bd[i] = p + 1; if (p) nO++; else nX++;
  for (int k = 0; k < cellSqN[i]; k++) { int q = cellSq[i][k]; if (p) cntO[q]++; else cntX[q]++; }
  for (int s = 0; s < 8; s++) { H1[s] ^= Z1[s][i][p]; H2[s] ^= Z2[s][i][p]; }
}
static inline void unplay(int i, int p) {
  bd[i] = 0; if (p) nO--; else nX--;
  for (int k = 0; k < cellSqN[i]; k++) { int q = cellSq[i][k]; if (p) cntO[q]--; else cntX[q]--; }
  for (int s = 0; s < 8; s++) { H1[s] ^= Z1[s][i][p]; H2[s] ^= Z2[s][i][p]; }
}

static int scoreMove(int cell, int att) {
  static const int wOwn[4] = {1, 8, 64, 0}, wBlk[4] = {1, 6, 48, 0};
  int sc = 0;
  for (int k = 0; k < cellSqN[cell]; k++) { int q = cellSq[cell][k];
    int a = att ? cntX[q] : cntO[q], b = att ? cntO[q] : cntX[q];
    if (b == 0) sc += wOwn[a]; if (a == 0) sc += wBlk[b]; }
  return sc;
}

static int search(int d) {
  nodes++;
  if ((nodes & 0xFFFFF) == 0 && now() - tstart > tlimit) timeout_flag = 1;
  if (timeout_flag) return 0;
  int att = nX == nO;
  if (nX + nO == NC) return -INF;
  // analyse
  int athrCell = -1, athrN = 0, dthrCell = -1, dthrN = 0, nlive = 0, es = 0, minNeed = 99;
  static char mark[MAXC]; // reuse; small boards
  for (int q = 0; q < NSQ; q++) {
    int cx = cntX[q], co = cntO[q];
    if (co == 0) { nlive++; es += 1 << cx; if (4 - cx < minNeed) minNeed = 4 - cx;
      if (cx == 3) { for (int k = 0; k < 4; k++) { int c = sqc[q][k]; if (!bd[c] && c != athrCell) { if (athrN == 0) { athrCell = c; athrN = 1; } else athrN = 2; } } } }
    if (cx == 0 && co == 3) { for (int k = 0; k < 4; k++) { int c = sqc[q][k]; if (!bd[c] && c != dthrCell) { if (dthrN == 0) { dthrCell = c; dthrN = 1; } else dthrN = 2; } } }
  }
  (void)mark;
  if (att) {
    if (athrN) return d >= 1 ? 1 : 0;
    if (!nlive || es < 8 || dthrN >= 2) return -INF;
    if (d <= 0) return 0;
    if (minNeed > d) return -(minNeed - 1);
  } else {
    if (dthrN) return -INF;
    if (!nlive || es < 16) return -INF;
    if (athrN >= 2) return d >= 1 ? 1 : 0;
    if (d <= 1) return -(d < 0 ? 0 : d);
    if (minNeed > d) return -(minNeed - 1);
  }
  int bs = 0; for (int s = 1; s < 8; s++) if (H1[s] < H1[bs] || (H1[s] == H1[bs] && H2[s] < H2[bs])) bs = s;
  u64 ka = H1[bs], kb = H2[bs];
  Ent *e = ttFind(ka, kb);
  if (e) { int w = e->info & 31, f = (e->info >> 5) & 31; if (w <= d) return w; if (f >= d) return -f; }
  int mv[MAXC], sc[MAXC], nm = 0;
  int forced = att ? (dthrN ? dthrCell : -1) : (athrN ? athrCell : -1);
  if (forced >= 0) mv[nm++] = forced;
  else for (int i = 0; i < NC; i++) if (!bd[i]) {
    int live = 0; for (int k = 0; k < cellSqN[i]; k++) { int q = cellSq[i][k]; if (!cntO[q] || !cntX[q]) { live = 1; break; } }
    if (!live) continue;
    int v = scoreMove(i, att), j = nm++;
    while (j > 0 && sc[j-1] < v) { mv[j] = mv[j-1]; sc[j] = sc[j-1]; j--; }
    mv[j] = i; sc[j] = v;
  }
  int res = 0;
  if (att) {
    int minf = INF;
    for (int k = 0; k < nm; k++) {
      play(mv[k], 0); int r = search(d - 1); unplay(mv[k], 0);
      if (timeout_flag) return 0;
      if (r > 0) { res = r + 1; break; }
      int f = (-r == INF) ? INF : -r + 1; if (f < minf) minf = f;
    }
    if (!res) res = -minf;
  } else {
    int maxw = 0;
    for (int k = 0; k < nm; k++) {
      play(mv[k], 1); int r = search(d); unplay(mv[k], 1);
      if (timeout_flag) return 0;
      if (r <= 0) { res = r; break; }
      if (r > maxw) maxw = r;
    }
    if (!res) res = maxw;
  }
  if (res > 0) ttStore(ka, kb, res, 0); else ttStore(ka, kb, WINNONE, -res);
  return res;
}

static void printBoard(void) {
  for (int r = 0; r < N; r++) { for (int c = 0; c < N; c++) { int v = bd[r*N+c]; putchar(v == 1 ? 'X' : v == 2 ? 'O' : '.'); } putchar('\n'); }
}
// PV: X plays any move keeping a win within the bound (fastest found by ID), O plays
// the reply with the longest (within-bound) resistance found.
static int minWin(int lim) { for (int dd = 1; dd <= lim; dd++) { int r = search(dd); if (r > 0) return r; if (r == -INF) return 0; } return 0; }
static void pv(int d) {
  int ply = 0;
  while (1) {
    int att = nX == nO, best = -1, bv = 0;
    if (att) {
      for (int i = 0; i < NC; i++) if (!bd[i]) {
        int win = 0; for (int k = 0; k < cellSqN[i]; k++) if (cntX[cellSq[i][k]] == 3) win = 1;
        if (win) { best = i; bv = 1; break; }
      }
      if (best < 0) for (int i = 0; i < NC; i++) if (!bd[i] && d > 1) {
        play(i, 0); int r = search(d - 1); unplay(i, 0);
        if (r > 0) { play(i, 0); r = minWin(r); unplay(i, 0); if (best < 0 || r + 1 < bv) { best = i; bv = r + 1; } }
      }
      if (best < 0) { printf("  no win?!\n"); return; }
      play(best, 0); ply++; printf("  %2d. X (%d,%d)  [X needs %d own moves incl. this]\n", ply, best / N, best % N, bv);
      if (bv == 1) { printBoard(); return; }
      d = bv - 1;
    } else {
      int bw = -1;
      for (int i = 0; i < NC; i++) if (!bd[i]) {
        play(i, 1); int r = minWin(d); unplay(i, 1);
        if (r <= 0) { printf("  refutation?!\n"); return; }
        if (r > bw) { bw = r; best = i; }
      }
      play(best, 1); ply++; printf("  %2d. O (%d,%d)  [best resistance: X still needs %d]\n", ply, best / N, best % N, bw);
    }
  }
}

int main(int argc, char **argv) {
  int n = atoi(argv[1]), d = atoi(argv[2]);
  int lg = argc > 3 ? atoi(argv[3]) : 23; tlimit = argc > 4 ? atof(argv[4]) : 1e18;
  int from = argc > 5 ? atoi(argv[5]) : d;
  int dopv = argc > 6 ? atoi(argv[6]) : 1;
  if (n > 16) return 1;
  setup(n); TTmask = (1ULL << lg) - 1; TT = calloc((size_t)BUCKET << lg, sizeof(Ent));
  printf("n=%d squares=%d TT=%.0f MB\n", n, NSQ, (double)((size_t)BUCKET << lg) * sizeof(Ent) / 1e6);
  tstart = now();
  for (int dd = from; dd <= d; dd++) {
    long long n0 = nodes; double t0 = now();
    int r = search(dd);
    if (timeout_flag) { printf("d=%2d: TIMEOUT (%lld nodes)\n", dd, nodes - n0); break; }
    printf("d=%2d: %s nodes=%lld time=%.1fs TTstores=%lld\n", dd, r > 0 ? "X WINS" : r == -INF ? "NO WIN (absolute)" : "no forced win within d",
           nodes - n0, now() - t0, ttStores);
    fflush(stdout);
    if (r > 0) { printf("RESULT n=%d: first player forces a win within %d own moves (search returned %d)\n", n, dd, r); if (dopv) pv(r); break; }
  }
  return 0;
}
