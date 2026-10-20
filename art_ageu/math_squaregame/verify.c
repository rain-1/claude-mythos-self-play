// Independent, deliberately simple verifier: "can first player force a win using at most d
// of its own moves?" Plain AND/OR search over char boards. Only sound rules used:
//  - a side that can complete a square does so (win);
//  - if the opponent has an open 3-of-4 the mover must block it (any other move loses at once).
// Exact-key memo table (no symmetry reduction, no Erdos-Selfridge, no lower bounds).
// Usage: ./verify n d
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int n, nc, nsq;
static int sq[1000][4];
static long long nodes;

typedef struct { uint64_t a, b; signed char d; signed char val; } Slot; // key = (Xbits, Obits)
#define TBITS 24
static Slot *tab;

static int completes(const char *bd, int p, int cell) { // would p playing cell complete a square?
  for (int q = 0; q < nsq; q++) {
    int has = 0, cnt = 0;
    for (int k = 0; k < 4; k++) { if (sq[q][k] == cell) has = 1; else if (bd[sq[q][k]] == p) cnt++; }
    if (has && cnt == 3) return 1;
  }
  return 0;
}

// returns 1 if X (player 1) can force a win with <= d more X moves; tomove in {1,2}
static int solve(char *bd, int tomove, int d) {
  nodes++;
  int other = 3 - tomove, empt = 0;
  for (int i = 0; i < nc; i++) if (!bd[i]) empt++;
  if (empt == 0) return 0;
  if (tomove == 1 && d == 0) return 0;
  // immediate win for mover
  for (int i = 0; i < nc; i++) if (!bd[i] && completes(bd, tomove, i)) return tomove == 1;
  // memo
  uint64_t A = 0, B = 0;
  for (int i = 0; i < nc; i++) { if (bd[i] == 1) A |= 1ULL << i; else if (bd[i] == 2) B |= 1ULL << i; }
  uint64_t h = (A * 0x9E3779B97F4A7C15ULL) ^ (B * 0xD6E8FEB86659FD93ULL); h ^= h >> 31;
  Slot *s = &tab[h & ((1ULL << TBITS) - 1)];
  if (s->a == A && s->b == B && s->val >= 0) {
    if (s->val == 1 && s->d <= d) return 1;
    if (s->val == 0 && s->d >= d) return 0;
  }
  // forced blocks
  int forced[64], nf = 0;
  for (int i = 0; i < nc; i++) if (!bd[i] && completes(bd, other, i)) forced[nf++] = i;
  int res;
  if (nf >= 2) res = (tomove == 2); // mover can block only one -> opponent wins
  else {
    int cand[64], nm = 0;
    if (nf == 1) cand[nm++] = forced[0];
    else {
      int sc[64];
      for (int i = 0; i < nc; i++) if (!bd[i]) {
        int v = 0; // move-ordering heuristic only (does not affect soundness)
        for (int q = 0; q < nsq; q++) {
          int has = 0, me = 0, op = 0;
          for (int k = 0; k < 4; k++) { int c = sq[q][k]; if (c == i) has = 1; else if (bd[c] == tomove) me++; else if (bd[c] == other) op++; }
          if (has && !op) v += 1 << (3 * me);
          if (has && !me) v += 1 << (3 * op);
        }
        int j = nm++; while (j > 0 && sc[j - 1] < v) { cand[j] = cand[j - 1]; sc[j] = sc[j - 1]; j--; }
        cand[j] = i; sc[j] = v;
      }
    }
    if (tomove == 1) {
      res = 0;
      for (int k = 0; k < nm && !res; k++) { bd[cand[k]] = 1; res = solve(bd, 2, d - 1); bd[cand[k]] = 0; }
    } else {
      res = 1;
      for (int k = 0; k < nm && res; k++) { bd[cand[k]] = 2; res = solve(bd, 1, d); bd[cand[k]] = 0; }
    }
  }
  s->a = A; s->b = B; s->d = d; s->val = res;
  return res;
}

int main(int argc, char **argv) {
  n = atoi(argv[1]); int d = atoi(argv[2]); nc = n * n;
  for (int r = 0; r < n; r++) for (int c = 0; c < n; c++) for (int s = 1; r + s < n && c + s < n; s++) {
    sq[nsq][0] = r * n + c; sq[nsq][1] = r * n + c + s; sq[nsq][2] = (r + s) * n + c; sq[nsq][3] = (r + s) * n + c + s; nsq++;
  }
  tab = calloc(1ULL << TBITS, sizeof(Slot));
  for (size_t i = 0; i < (1ULL << TBITS); i++) tab[i].val = -1;
  char bd[64] = {0};
  int r = solve(bd, 1, d);
  printf("verify n=%d d=%d: %s (nodes=%lld)\n", n, d, r ? "X forces win" : "no forced win", nodes);
  return 0;
}
