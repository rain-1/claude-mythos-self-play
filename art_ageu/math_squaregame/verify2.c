// Independent simple verifier for n <= 16: "can X force a win with <= d own moves?"
// Only trivially sound rules: take an immediate win; if the opponent has an open 3-of-4 you
// must block it (two distinct such cells and no win => you lose). Every other legal move is tried
// (no symmetry, no Erdos-Selfridge, no dominance pruning). Memo table keyed on the EXACT board.
// Usage: ./verify2 n d [tbits] [timelimit]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#define MAXC 256
static int n, nc, nsq, sq[1400][4], csq[MAXC][64], ncsq[MAXC];
static char bd[MAXC];
static long long nodes; static double t0, tl = 1e18; static int tout;
static double now() { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec * 1e-9; }
typedef struct { uint64_t x[4], o[4]; signed char d, val; } Slot;
static Slot *tab; static uint64_t tmask;

static int solve(int tomove, int d) { // tomove 1 = X, 2 = O
  nodes++;
  if ((nodes & 0xFFFFF) == 0 && now() - t0 > tl) tout = 1;
  if (tout) return 0;
  int other = 3 - tomove, empt = 0;
  for (int i = 0; i < nc; i++) if (!bd[i]) empt++;
  if (!empt) return 0;
  if (tomove == 1 && d == 0) return 0;
  // square counts
  int mewin = 0, forced = -1, nforced = 0;
  for (int q = 0; q < nsq; q++) {
    int a = 0, b = 0, e = -1;
    for (int k = 0; k < 4; k++) { int c = sq[q][k]; if (bd[c] == tomove) a++; else if (bd[c] == other) b++; else e = c; }
    if (a == 3 && b == 0) mewin = 1;
    if (b == 3 && a == 0 && e != forced) { if (forced < 0) { forced = e; nforced = 1; } else nforced = 2; }
  }
  if (mewin) return tomove == 1;
  uint64_t X[4] = {0}, O[4] = {0};
  for (int i = 0; i < nc; i++) { if (bd[i] == 1) X[i >> 6] |= 1ULL << (i & 63); else if (bd[i] == 2) O[i >> 6] |= 1ULL << (i & 63); }
  uint64_t h = 0x12345;
  for (int k = 0; k < 4; k++) { h = (h ^ X[k]) * 0x9E3779B97F4A7C15ULL; h ^= h >> 29; h = (h ^ O[k]) * 0xBF58476D1CE4E5B9ULL; h ^= h >> 31; }
  Slot *s = &tab[h & tmask];
  if (s->val >= 0 && !memcmp(s->x, X, 32) && !memcmp(s->o, O, 32)) {
    if (s->val == 1 && s->d <= d) return 1;
    if (s->val == 0 && s->d >= d) return 0;
  }
  int res;
  if (nforced >= 2) res = (tomove == 2);
  else {
    int cand[MAXC], sc[MAXC], nm = 0;
    if (nforced == 1) cand[nm++] = forced;
    else for (int i = 0; i < nc; i++) if (!bd[i]) {
      int v = 0; // ordering heuristic only
      for (int k = 0; k < ncsq[i]; k++) { int q = csq[i][k], me = 0, op = 0;
        for (int j = 0; j < 4; j++) { int c = sq[q][j]; if (bd[c] == tomove) me++; else if (bd[c] == other) op++; }
        if (!op) v += 1 << (3 * me); if (!me) v += 1 << (3 * op); }
      int j = nm++; while (j > 0 && sc[j-1] < v) { cand[j] = cand[j-1]; sc[j] = sc[j-1]; j--; } cand[j] = i; sc[j] = v;
    }
    if (tomove == 1) { res = 0; for (int k = 0; k < nm && !res; k++) { bd[cand[k]] = 1; res = solve(2, d - 1); bd[cand[k]] = 0; } }
    else { res = 1; for (int k = 0; k < nm && res; k++) { bd[cand[k]] = 2; res = solve(1, d); bd[cand[k]] = 0; } }
  }
  if (tout) return 0;
  memcpy(s->x, X, 32); memcpy(s->o, O, 32); s->d = d; s->val = res;
  return res;
}

int main(int argc, char **argv) {
  n = atoi(argv[1]); int d = atoi(argv[2]); int tb = argc > 3 ? atoi(argv[3]) : 22; tl = argc > 4 ? atof(argv[4]) : 1e18;
  nc = n * n;
  for (int r = 0; r < n; r++) for (int c = 0; c < n; c++) for (int s = 1; r + s < n && c + s < n; s++) {
    int *q = sq[nsq]; q[0] = r*n+c; q[1] = r*n+c+s; q[2] = (r+s)*n+c; q[3] = (r+s)*n+c+s;
    for (int k = 0; k < 4; k++) csq[q[k]][ncsq[q[k]]++] = nsq;
    nsq++;
  }
  tmask = (1ULL << tb) - 1; tab = calloc(1ULL << tb, sizeof(Slot));
  for (uint64_t i = 0; i <= tmask; i++) tab[i].val = -1;
  t0 = now();
  int r = solve(1, d);
  printf("verify2 n=%d d=%d: %s (nodes=%lld, %.1fs)\n", n, d, tout ? "TIMEOUT" : r ? "X forces win" : "no forced win", nodes, now() - t0);
  return 0;
}
