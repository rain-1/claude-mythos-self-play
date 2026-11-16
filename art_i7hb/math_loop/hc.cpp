// Hamiltonian cycles of an m x n grid graph with deleted vertices (plug DP, exact uint64 counts,
// saturating at 2^62).   MO 516913.
//   hc count  m n  r,c r,c ...        -> number of Hamiltonian cycles
//   hc cycle  m n  r,c ...            -> if unique, the edges of the cycle ("r c r2 c2" per line)
//   hc search m n d [maxprint]        -> all d-subsets (colour-balanced) leaving exactly one cycle
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64;
typedef unsigned __int128 cnt;
static const cnt SAT = ((cnt)1) << 120;
string str(cnt x){ if(x==0) return "0"; string s; while(x){ s+=char('0'+(int)(x%10)); x/=10;} reverse(s.begin(),s.end()); return s; }
int M, N, W, H;            // W = frontier width (min), H = sweep length
bool tr;
vector<char> blk, fh, fv, rh, rv; // blocked, forbidden horizontal (cell -> right), vertical (cell -> down) in internal coords
inline int id(int i, int j) { return i * W + j; }
inline int get(u64 s, int k) { return (s >> (2 * k)) & 3; }
inline u64 setp(u64 s, int k, u64 v) { return (s & ~(3ULL << (2 * k))) | (v << (2 * k)); }

cnt count_hc() {
    int last = -1;
    for (int i = 0; i < H; i++) for (int j = 0; j < W; j++) if (!blk[id(i, j)]) last = id(i, j);
    if (last < 0) return 0;
    unordered_map<u64, cnt> cur, nxt;
    cur[0] = 1; cnt total = 0;
    for (int i = 0; i < H; i++) {
        for (int j = 0; j < W; j++) {
            nxt.clear();
            bool b = blk[id(i, j)];
            bool canR = (j + 1 < W) && !blk[id(i, j + 1)] && !b && !fh[id(i, j)];
            bool canD = (i + 1 < H) && !blk[id(i + 1, j)] && !b && !fv[id(i, j)];
            bool mustR = rh[id(i, j)], mustD = rv[id(i, j)];
            for (auto &kv : cur) {
                u64 s = kv.first; cnt c = kv.second;
                int l = get(s, j), u = get(s, j + 1);
                auto add = [&](u64 t) { cnt &x = nxt[t]; x += c; if (x > SAT) x = SAT; };
                if (b) { if (!l && !u) add(s); continue; }
                if (!l && !u) { if (canR && canD) add(setp(setp(s, j, 1), j + 1, 2)); }
                else if (!l || !u) {
                    int x = l | u;
                    if (canD && !mustR) add(setp(setp(s, j, x), j + 1, 0));
                    if (canR && !mustD) add(setp(setp(s, j, 0), j + 1, x));
                } else {
                    if (mustR || mustD) continue;
                    u64 t = setp(setp(s, j, 0), j + 1, 0);
                    if (l == 1 && u == 1) {
                        int d = 1;
                        for (int k = j + 2; k <= W; k++) { int p = get(s, k); if (p == 1) d++; else if (p == 2) { if (--d == 0) { t = setp(t, k, 1); break; } } }
                        add(t);
                    } else if (l == 2 && u == 2) {
                        int d = 1;
                        for (int k = j - 1; k >= 0; k--) { int p = get(s, k); if (p == 2) d++; else if (p == 1) { if (--d == 0) { t = setp(t, k, 2); break; } } }
                        add(t);
                    } else if (l == 2 && u == 1) add(t);
                    else { if (id(i, j) == last && t == 0) { total += c; if (total > SAT) total = SAT; } }
                }
            }
            cur.swap(nxt);
        }
        nxt.clear();
        for (auto &kv : cur) if (get(kv.first, W) == 0) nxt[kv.first << 2] = kv.second;
        cur.swap(nxt);
    }
    return total;
}
void setup(int m, int n) { M = m; N = n; tr = (n < m); W = tr ? n : m; H = tr ? m : n; blk.assign(W * H, 0); fh.assign(W * H, 0); fv.assign(W * H, 0); rh.assign(W * H, 0); rv.assign(W * H, 0); }
// user (r,c): r in [0,m), c in [0,n).  internal: sweep index i, frontier index j.
inline int uid(int r, int c) { return tr ? id(r, c) : id(c, r); }
int main(int argc, char **argv) {
    string mode = argv[1]; int m = atoi(argv[2]), n = atoi(argv[3]); setup(m, n);
    if (mode == "count" || mode == "cycle") {
        for (int a = 4; a < argc; a++) { int r, c; sscanf(argv[a], "%d,%d", &r, &c); blk[uid(r, c)] = 1; }
        cnt c = count_hc();
        if (mode == "count") { printf("%s\n", str(c).c_str()); return 0; }
        if (c != 1) { printf("count %s\n", str(c).c_str()); return 1; }
        for (int r = 0; r < m; r++) for (int cc = 0; cc < n; cc++) {
            // edge to (r,cc+1) and to (r+1,cc) in user coords
            for (int dir = 0; dir < 2; dir++) {
                int r2 = r + (dir == 1), c2 = cc + (dir == 0);
                if (r2 >= m || c2 >= n) continue;
                if (blk[uid(r, cc)] || blk[uid(r2, c2)]) continue;
                // internal: is this a "right" (j+1) or "down" (i+1) edge?
                bool internalRight = tr ? (dir == 0) : (dir == 1);
                vector<char> &f = internalRight ? fh : fv;
                f[uid(r, cc)] = 1;
                if (count_hc() == 0) printf("%d %d %d %d\n", r, cc, r2, c2);
                f[uid(r, cc)] = 0;
            }
        }
        return 0;
    }
    if (mode == "prob") {   // usage probability of every edge over all Hamiltonian cycles
        for (int a = 4; a < argc; a++) { int r, c; sscanf(argv[a], "%d,%d", &r, &c); blk[uid(r, c)] = 1; }
        cnt tot = count_hc(); printf("total %s\n", str(tot).c_str());
        for (int r = 0; r < m; r++) for (int cc = 0; cc < n; cc++) for (int dir = 0; dir < 2; dir++) {
            int r2 = r + (dir == 1), c2 = cc + (dir == 0);
            if (r2 >= m || c2 >= n) continue;
            if (blk[uid(r, cc)] || blk[uid(r2, c2)]) continue;
            bool internalRight = tr ? (dir == 0) : (dir == 1);
            vector<char> &f = internalRight ? fh : fv;
            f[uid(r, cc)] = 1; cnt w = count_hc(); f[uid(r, cc)] = 0;
            printf("%d %d %d %d %.12Lf\n", r, cc, r2, c2, 1.0L - (long double)w / (long double)tot);
            fflush(stdout);
        }
        return 0;
    }
    if (mode == "anneal") { // hc anneal m n d seed iters [T]
        int d = atoi(argv[4]); unsigned seed = atoi(argv[5]); long iters = atol(argv[6]); double T = argc > 7 ? atof(argv[7]) : 1.0;
        mt19937 rng(seed); int Tn = m * n;
        auto col = [&](int x) { return ((x / n + x % n) & 1) ? 1 : -1; };
        vector<int> cur(d);
        auto eval = [&](vector<int> &v) -> double {
            fill(blk.begin(), blk.end(), 0);
            for (int x : v) blk[uid(x / n, x % n)] = 1;
            cnt c = count_hc(); if (c == 0) return 1e9; return log((double)(long double)c);
        };
        double e;
        while (true) { // random balanced start with a cycle
            set<int> s; while ((int)s.size() < d) s.insert(rng() % Tn);
            cur.assign(s.begin(), s.end()); int bal = 0; for (int x : cur) bal += col(x);
            if (bal != 0 && Tn % 2 == 0) continue;
            e = eval(cur); if (e < 1e8) break;
        }
        for (long it = 0; it < iters; it++) {
            vector<int> nw = cur; int k = rng() % d; int x;
            while (true) { x = rng() % Tn; if (col(x) != col(cur[k])) continue; bool dup = false; for (int y : cur) if (y == x) dup = true; if (!dup) break; }
            nw[k] = x; double e2 = eval(nw);
            if (e2 < 1e8 && (e2 <= e || exp((e - e2) / T) > (rng() % 1000000) / 1e6)) { cur = nw; e = e2; }
            if (e == 0) { sort(cur.begin(), cur.end()); printf("UNIQUE it=%ld :", it); for (int y : cur) printf(" %d,%d", y / n, y % n); printf("\n"); fflush(stdout); return 0; }
            if (it % 200 == 0) { fprintf(stderr, "it %ld logcount %.2f\n", it, e); }
        }
        printf("no luck, last logcount %.2f\n", e); return 0;
    }
    if (mode == "sample") { // hc sample m n K seed cells... : K uniform random Hamiltonian cycles, one per line
        int K = atoi(argv[4]); unsigned seed = atoi(argv[5]); mt19937_64 rng(seed);
        for (int a = 6; a < argc; a++) { int r, c; sscanf(argv[a], "%d,%d", &r, &c); blk[uid(r, c)] = 1; }
        cnt tot = count_hc(); fprintf(stderr, "total %s\n", str(tot).c_str());
        for (int k = 0; k < K; k++) {
            fill(fh.begin(), fh.end(), 0); fill(fv.begin(), fv.end(), 0); fill(rh.begin(), rh.end(), 0); fill(rv.begin(), rv.end(), 0);
            cnt c = tot;
            for (int r = 0; r < m; r++) for (int cc = 0; cc < n; cc++) for (int dir = 0; dir < 2; dir++) {
                int r2 = r + (dir == 1), c2 = cc + (dir == 0);
                if (r2 >= m || c2 >= n) continue;
                if (blk[uid(r, cc)] || blk[uid(r2, c2)]) continue;
                bool internalRight = tr ? (dir == 0) : (dir == 1);
                vector<char> &rq = internalRight ? rh : rv; vector<char> &fb = internalRight ? fh : fv;
                rq[uid(r, cc)] = 1; cnt cin = count_hc();
                long double p = (long double)cin / (long double)c;
                long double u = (long double)(rng() >> 11) / 9007199254740992.0L;
                if (u < p) { c = cin; printf("%d %d %d %d ", r, cc, r2, c2); }
                else { rq[uid(r, cc)] = 0; fb[uid(r, cc)] = 1; c = c - cin; }
            }
            printf("\n"); fflush(stdout);
        }
        return 0;
    }
    if (mode == "search") {
        int d = atoi(argv[4]); long maxprint = argc > 5 ? atol(argv[5]) : 1000000; long found = 0, tested = 0;
        int T = m * n; vector<int> idx(d); for (int k = 0; k < d; k++) idx[k] = k;
        int want = (T - d); if (want % 2) { printf("found 0 (odd)\n"); return 0; }
        while (true) {
            int bal = 0; // colour balance of remaining
            for (int k = 0; k < d; k++) { int r = idx[k] / n, c = idx[k] % n; bal += ((r + c) & 1) ? 1 : -1; }
            int tot = 0; for (int r = 0; r < m; r++) for (int c = 0; c < n; c++) tot += ((r + c) & 1) ? 1 : -1;
            if (bal == tot) {
                fill(blk.begin(), blk.end(), 0);
                for (int k = 0; k < d; k++) blk[uid(idx[k] / n, idx[k] % n)] = 1;
                tested++;
                if (count_hc() == 1) { found++; if (found <= maxprint) { for (int k = 0; k < d; k++) printf("%d,%d ", idx[k] / n, idx[k] % n); printf("\n"); } }
            }
            int k = d - 1; while (k >= 0 && idx[k] == T - d + k) k--;
            if (k < 0) break; idx[k]++; for (int q = k + 1; q < d; q++) idx[q] = idx[q - 1] + 1;
        }
        printf("found %ld tested %ld\n", found, tested);
    }
}
