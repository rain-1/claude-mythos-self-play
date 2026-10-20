// Square achievement game solver (n <= 8, uint64 bitboards).
// Players X (first, "attacker") and O alternate; first to own the 4 corners of an
// axis-parallel square wins. Question solved: can X force a win within d of its own moves?
// Iterative deepening on d; rigorous (no unsound move pruning), with:
//  - immediate wins / forced blocks / double-threat detection
//  - Erdos-Selfridge bound (O as Breaker) => X cannot win at all
//  - lower bound on moves needed (min over live squares of 4-count)
//  - exact transposition table keyed on canonical board under the 8 symmetries
//  - defender moves on cells lying in no live square (for either side) skipped (dominated: pass)
// Usage: ./sqgame n [maxd] [tt_log2] [timelimit_sec]
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

typedef uint64_t u64;
#define INF 31
static int N, NC;
static u64 FULL;
static int NSQ;
static u64 SQ[512];
static int cellSq[64][64], cellSqN[64];
static u64 symTab[8][8][256];
static long long nodes = 0;
static double tstart, tlimit = 1e18;
static int timeout_flag = 0;

static double now() { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec * 1e-9; }

// ---------------- TT ----------------
typedef struct { u64 x; u64 o; uint32_t info; } Ent; // info: bits0-4 winD, 5-9 failD, bit 31 valid
static Ent *TT; static u64 TTmask; static int TTlog;
#define WINNONE 31

static u64 applySym(int s, u64 b) {
  u64 r = 0; for (int k = 0; b; k++, b >>= 8) r |= symTab[s][k][b & 255]; return r;
}
static void canon(u64 X, u64 O, u64 *cx, u64 *co) {
  u64 bx = X, bo = O;
  for (int s = 1; s < 8; s++) {
    u64 x = applySym(s, X), o = applySym(s, O);
    if (x < bx || (x == bx && o < bo)) { bx = x; bo = o; }
  }
  *cx = bx; *co = bo;
}
static inline u64 hsh(u64 x, u64 o) { u64 h = x * 0x9E3779B97F4A7C15ULL ^ (o + 0x632BE59BD9B4E019ULL) * 0xC2B2AE3D27D4EB4FULL; h ^= h >> 29; return h; }
#define BUCKET 4
static Ent *ttFind(u64 cx, u64 co) {
  u64 i = (hsh(cx, co) & TTmask) * BUCKET;
  for (int k = 0; k < BUCKET; k++) {
    Ent *e = &TT[i + k];
    if (e->info && e->x == cx && e->o == co) return e;
  }
  return NULL;
}
static long long ttStores = 0;
static void ttStore(u64 cx, u64 co, int winD, int failD) {
  u64 i = (hsh(cx, co) & TTmask) * BUCKET;
  Ent *e = ttFind(cx, co);
  if (e) {
    int w = e->info & 31, f = (e->info >> 5) & 31;
    if (winD < w) w = winD; if (failD > f) f = failD;
    e->info = w | (f << 5) | (1u << 31);
    return;
  }
  ttStores++;
  // replace: empty slot, else the shallowest-information slot (smallest failD & largest winD); round robin tie
  int best = 0, bscore = 1 << 30;
  for (int k = 0; k < BUCKET; k++) {
    Ent *f = &TT[i + k];
    if (!f->info) { best = k; break; }
    int w = f->info & 31, fd = (f->info >> 5) & 31;
    int sc = (w != WINNONE ? 32 - w : 0) + fd;
    if (sc < bscore) { bscore = sc; best = k; }
  }
  TT[i + best].x = cx;
  TT[i + best].o = co; TT[i + best].info = winD | (failD << 5) | (1u << 31);
}

// ---------------- setup ----------------
static void setup(int n) {
  N = n; NC = n * n; FULL = (NC == 64) ? ~0ULL : ((1ULL << NC) - 1);
  NSQ = 0;
  for (int s = 1; s < n; s++) for (int r = 0; r + s < n; r++) for (int c = 0; c + s < n; c++) {
    u64 m = (1ULL << (r * n + c)) | (1ULL << (r * n + c + s)) | (1ULL << ((r + s) * n + c)) | (1ULL << ((r + s) * n + c + s));
    SQ[NSQ++] = m;
  }
  memset(cellSqN, 0, sizeof cellSqN);
  for (int q = 0; q < NSQ; q++) for (int i = 0; i < NC; i++) if (SQ[q] >> i & 1) cellSq[i][cellSqN[i]++] = q;
  int perm[8][64];
  for (int r = 0; r < n; r++) for (int c = 0; c < n; c++) {
    int i = r * n + c;
    int rr[8] = {r, c, n-1-r, n-1-c, r, n-1-r, c, n-1-c};
    int cc[8] = {c, n-1-r, n-1-c, r, n-1-c, c, r, n-1-r};
    for (int s = 0; s < 8; s++) perm[s][i] = rr[s] * n + cc[s];
  }
  memset(symTab, 0, sizeof symTab);
  for (int s = 0; s < 8; s++) for (int k = 0; k < 8; k++) for (int v = 0; v < 256; v++) {
    u64 r = 0; for (int b = 0; b < 8; b++) if (v >> b & 1) { int i = k * 8 + b; if (i < NC) r |= 1ULL << perm[s][i]; }
    symTab[s][k][v] = r;
  }
}

// ---------------- analysis ----------------
typedef struct { u64 athr, dthr, alive, dlive; int minNeed, esA, nlive; } Info;
static inline void analyse(u64 X, u64 O, Info *I) {
  I->athr = I->dthr = I->alive = I->dlive = 0; I->minNeed = 99; I->esA = 0; I->nlive = 0;
  for (int q = 0; q < NSQ; q++) {
    u64 m = SQ[q]; int cx = __builtin_popcountll(X & m), co = __builtin_popcountll(O & m);
    if (co == 0) { I->alive |= m; I->esA += 1 << cx; I->nlive++; if (4 - cx < I->minNeed) I->minNeed = 4 - cx; if (cx == 3) I->athr |= m & ~X; }
    if (cx == 0) { I->dlive |= m; if (co == 3) I->dthr |= m & ~O; }
  }
}

// result: >0 win with r attacker moves; <=0 fail, failure depth -r (INF=31 absolute)
#define WIN(w) (w)
#define FAIL(f) (-(f))

static int scoreMove(u64 X, u64 O, int cell, int attackerMoving) {
  u64 me = attackerMoving ? X : O, op = attackerMoving ? O : X;
  int sc = 0;
  static const int wOwn[4] = {1, 8, 64, 0}, wBlk[4] = {1, 6, 48, 0};
  for (int k = 0; k < cellSqN[cell]; k++) {
    u64 m = SQ[cellSq[cell][k]];
    int a = __builtin_popcountll(me & m), b = __builtin_popcountll(op & m);
    if (b == 0) sc += wOwn[a];
    if (a == 0) sc += wBlk[b];
  }
  return sc;
}

static int search(u64 X, u64 O, int d);

static int genMoves(u64 X, u64 O, u64 cand, int att, int *mv) {
  int n = 0, sc[64];
  while (cand) { int c = __builtin_ctzll(cand); cand &= cand - 1; mv[n] = c; sc[n] = scoreMove(X, O, c, att); n++; }
  for (int i = 1; i < n; i++) { int m = mv[i], s = sc[i], j = i - 1; while (j >= 0 && sc[j] < s) { mv[j+1] = mv[j]; sc[j+1] = sc[j]; j--; } mv[j+1] = m; sc[j+1] = s; }
  return n;
}

static int search(u64 X, u64 O, int d) {
  nodes++;
  if ((nodes & 0xFFFFF) == 0 && now() - tstart > tlimit) timeout_flag = 1;
  if (timeout_flag) return FAIL(0);
  int att = __builtin_popcountll(X) == __builtin_popcountll(O);
  u64 empty = FULL & ~(X | O);
  if (!empty) return FAIL(INF);
  Info I; analyse(X, O, &I);
  if (att) {
    if (I.athr) return d >= 1 ? WIN(1) : FAIL(0);
    if (!I.nlive) return FAIL(INF);
    if (I.esA < 8) return FAIL(INF);              // Erdos-Selfridge, Maker to move
    if (__builtin_popcountll(I.dthr) >= 2) return FAIL(INF);
    if (d <= 0) return FAIL(0);
    if (I.minNeed > d) return FAIL(I.minNeed - 1);
  } else {
    if (I.dthr) return FAIL(INF);                 // defender wins now
    if (!I.nlive) return FAIL(INF);
    if (I.esA < 16) return FAIL(INF);             // Erdos-Selfridge, Breaker to move
    int nt = __builtin_popcountll(I.athr);
    if (nt >= 2) return d >= 1 ? WIN(1) : FAIL(0);
    if (d <= 1) return FAIL(d < 0 ? 0 : d);
    if (I.minNeed > d) return FAIL(I.minNeed - 1);
  }
  u64 cx, co; canon(X, O, &cx, &co);
  Ent *e = ttFind(cx, co);
  if (e) {
    int w = e->info & 31, f = (e->info >> 5) & 31;
    if (w <= d) return WIN(w);
    if (f >= d) return FAIL(f);
  }
  int mv[64], nm, res;
  if (att) {
    u64 cand = I.dthr ? I.dthr : (empty & (I.alive | I.dlive));
    nm = genMoves(X, O, cand, 1, mv);
    int minf = INF; res = 0;
    for (int i = 0; i < nm; i++) {
      int r = search(X | (1ULL << mv[i]), O, d - 1);
      if (timeout_flag) return FAIL(0);
      if (r > 0) { res = WIN(r + 1); break; }
      int f = -r + 1; if (-r == INF) f = INF; if (f < minf) minf = f;
    }
    if (!res) res = FAIL(minf);
  } else {
    u64 cand = I.athr ? I.athr : (empty & (I.alive | I.dlive));
    nm = genMoves(X, O, cand, 0, mv);
    int maxw = 0; res = 0;
    for (int i = 0; i < nm; i++) {
      int r = search(X, O | (1ULL << mv[i]), d);
      if (timeout_flag) return FAIL(0);
      if (r <= 0) { res = r; break; }
      if (r > maxw) maxw = r;
    }
    if (!res) res = WIN(maxw);
  }
  if (res > 0) ttStore(cx, co, res, 0); else ttStore(cx, co, WINNONE, -res);
  return res;
}

static void printBoard(u64 X, u64 O) {
  for (int r = 0; r < N; r++) { for (int c = 0; c < N; c++) { int i = r * N + c; putchar(X >> i & 1 ? 'X' : O >> i & 1 ? 'O' : '.'); } putchar('\n'); }
}

// exact minimal win length from position (iterative deepening), 0 if none within lim
static int minWin(u64 X, u64 O, int lim) {
  for (int dd = 1; dd <= lim; dd++) { int r = search(X, O, dd); if (r > 0) return r; if (r == FAIL(INF)) return 0; }
  return 0;
}
// principal variation: X plays fastest win, O plays longest resistance (both exact)
static void pv(u64 X, u64 O, int d) {
  printf("PV (cells as (row,col)), X fastest win vs O longest resistance:\n");
  int ply = 0;
  while (1) {
    int att = __builtin_popcountll(X) == __builtin_popcountll(O);
    u64 empty = FULL & ~(X | O);
    int best = -1, bestv = 0;
    if (att) {
      for (u64 c = empty; c; c &= c - 1) { int m = __builtin_ctzll(c);
        u64 X2 = X | (1ULL << m);
        int win = 0; for (int q = 0; q < NSQ; q++) if ((X2 & SQ[q]) == SQ[q]) win = 1;
        if (win) { best = m; bestv = 1; break; }
        if (d - 1 < 1) continue;
        int r = minWin(X2, O, d - 1); if (r > 0 && (best < 0 || r + 1 < bestv)) { best = m; bestv = r + 1; } }
      if (best < 0) { printf("  (no win found)\n"); return; }
      X |= 1ULL << best; ply++;
      printf("  %2d. X (%d,%d)  [X needs %d own moves incl. this]\n", ply, best / N, best % N, bestv);
      for (int q = 0; q < NSQ; q++) if ((X & SQ[q]) == SQ[q]) { printBoard(X, O); return; }
      d = bestv - 1;
    } else {
      int bw = -1;
      for (u64 c = empty; c; c &= c - 1) { int m = __builtin_ctzll(c);
        int r = minWin(X, O | (1ULL << m), d); if (r <= 0) { printf("  refutation found?!\n"); return; }
        if (r > bw) { bw = r; best = m; } }
      O |= 1ULL << best; ply++;
      printf("  %2d. O (%d,%d)  [best resistance: X still needs %d]\n", ply, best / N, best % N, bw);
    }
  }
}

int main(int argc, char **argv) {
  int n = argc > 1 ? atoi(argv[1]) : 5;
  int maxd = argc > 2 ? atoi(argv[2]) : (n * n + 1) / 2;
  TTlog = argc > 3 ? atoi(argv[3]) : 22;
  tlimit = argc > 4 ? atof(argv[4]) : 1e18;
  if (n > 8) { fprintf(stderr, "n<=8 only\n"); return 1; }
  setup(n);
  TTmask = (1ULL << TTlog) - 1;
  TT = calloc((size_t)BUCKET << TTlog, sizeof(Ent));
  printf("n=%d squares=%d TT entries=%llu (%.0f MB)\n", n, NSQ, (unsigned long long)BUCKET << TTlog, (double)(BUCKET << TTlog) * sizeof(Ent) / 1e6);
  tstart = now();
  long long tot = 0;
  for (int d = 1; d <= maxd; d++) {
    long long n0 = nodes; double t0 = now();
    int r = search(0, 0, d);
    if (timeout_flag) { printf("d=%2d: TIMEOUT after %lld nodes\n", d, nodes - n0); break; }
    tot = nodes;
    printf("d=%2d: %s  nodes=%lld  time=%.2fs  (cum %lld nodes, TT stores %lld)\n", d,
           r > 0 ? "X WINS" : (r == FAIL(INF) ? "NO WIN (absolute: X cannot force win at all)" : "no forced X win within d"),
           nodes - n0, now() - t0, tot, ttStores);
    fflush(stdout);
    if (r > 0) { printf("RESULT: first player wins; minimal number of first-player moves = %d\n", r); pv(0, 0, r); break; }
    if (r == FAIL(INF) || -r >= (n * n + 1) / 2) { printf("RESULT: first player cannot force a win (draw with best play; second player cannot win by strategy stealing)\n"); break; }
  }
  return 0;
}
