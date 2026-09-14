/* tripod.c — MO 497434: is there a snark with a chordless cycle C whose complement V-C is independent?
   Counting edges: a cubic graph with such a cycle of length c and n-c outside vertices (each with 3 neighbours
   on C, none of them adjacent to each other) has 3n/2 = c + 3(n-c) + chords, so chordless forces c = 3n/4:
   G = a cycle C_{3m} plus m "tripod" vertices, each joined to 3 cycle vertices, the triples partitioning V(C).
   (C is then a chordless DOMINATING cycle.)  So the question is: is any tripod graph 3-connected and NOT
   3-edge-colourable?  This program enumerates every partition of Z_{3m} into triples (optionally with all
   gaps >= g inside each triple, which for g = 3 is exactly girth >= 5) and tests 3-edge-colourability by
   backtracking; non-colourable graphs are printed with their connectivity.

   build: gcc -O2 -fopenmp -o tripod tripod.c      run: ./tripod m g */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>

#define MAXM 10
#define MAXN (4*MAXM)
#define MAXE (6*MAXM)

typedef struct { int n, ne; int adj[MAXN][3]; int eid[MAXN][3]; } Graph;

static int gap_ok(int a, int b, int c3m, int g) { int d = b - a; if (d < 0) d = -d; int e = c3m - d; if (e < d) d = e; return d >= g; }

/* 3-edge-colouring by backtracking over edges in order, colour of each vertex's incident edges must differ */
static int colour_rec(Graph *G, int *ecol, int (*vcol)[3], int e, int *eu, int *ev) {
    if (e == G->ne) return 1;
    int u = eu[e], v = ev[e];
    for (int c = 0; c < 3; c++) {
        int ok = 1;
        for (int i = 0; i < 3; i++) if (vcol[u][i] == c || vcol[v][i] == c) { ok = 0; break; }
        if (!ok) continue;
        int su = -1, sv = -1;
        for (int i = 0; i < 3; i++) if (G->eid[u][i] == e) su = i;
        for (int i = 0; i < 3; i++) if (G->eid[v][i] == e) sv = i;
        vcol[u][su] = c; vcol[v][sv] = c; ecol[e] = c;
        if (colour_rec(G, ecol, vcol, e + 1, eu, ev)) return 1;
        vcol[u][su] = -1; vcol[v][sv] = -1; ecol[e] = -1;
    }
    return 0;
}

static int colourable(Graph *G, int *eu, int *ev) {
    int ecol[MAXE]; int vcol[MAXN][3];
    for (int i = 0; i < MAXN; i++) vcol[i][0] = vcol[i][1] = vcol[i][2] = -1;
    for (int i = 0; i < MAXE; i++) ecol[i] = -1;
    /* fix the colour of edge 0 (symmetry) */
    return colour_rec(G, ecol, vcol, 0, eu, ev);
}

/* vertex connectivity >= 3 ? remove every pair of vertices and check connectivity (n <= 40 so cheap) */
static int connected_without(Graph *G, int x, int y) {
    int seen[MAXN] = {0}, st[MAXN], sp = 0, start = -1, cnt = 0;
    for (int v = 0; v < G->n; v++) if (v != x && v != y) { start = v; break; }
    if (start < 0) return 1;
    seen[start] = 1; st[sp++] = start;
    while (sp) { int v = st[--sp]; cnt++; for (int i = 0; i < 3; i++) { int w = G->adj[v][i]; if (w == x || w == y || seen[w]) continue; seen[w] = 1; st[sp++] = w; } }
    int need = G->n - (x >= 0) - (y >= 0 && y != x);
    return cnt == need;
}
static int three_connected(Graph *G) {
    for (int x = 0; x < G->n; x++) for (int y = x + 1; y < G->n; y++) if (!connected_without(G, x, y)) return 0;
    for (int x = 0; x < G->n; x++) if (!connected_without(G, x, -1)) return 0;
    return 1;
}

static void build(int m, int (*tri)[3], Graph *G, int *eu, int *ev) {
    int c = 3 * m; G->n = 4 * m; G->ne = 0;
    int deg[MAXN] = {0};
    #define ADD(a,b) do { eu[G->ne] = a; ev[G->ne] = b; G->adj[a][deg[a]] = b; G->eid[a][deg[a]++] = G->ne; G->adj[b][deg[b]] = a; G->eid[b][deg[b]++] = G->ne; G->ne++; } while (0)
    for (int i = 0; i < c; i++) ADD(i, (i + 1) % c);
    for (int t = 0; t < m; t++) for (int j = 0; j < 3; j++) ADD(c + t, tri[t][j]);
    #undef ADD
}

static long long total = 0, noncol = 0, snarks = 0;

/* enumerate partitions: the smallest unused element picks two larger partners b < c */
static void enumerate(int m, int g, int *used, int (*tri)[3], int t, int first_b, int first_c) {
    int c3m = 3 * m;
    if (t == m) {
        Graph G; int eu[MAXE], ev[MAXE];
        build(m, tri, &G, eu, ev);
        #pragma omp atomic
        total++;
        if (!colourable(&G, eu, ev)) {
            int tc = three_connected(&G);
            #pragma omp atomic
            noncol++;
            if (tc) {
                #pragma omp atomic
                snarks++;
            }
            #pragma omp critical
            {
                printf("NON-3-EDGE-COLOURABLE m=%d 3conn=%d triples:", m, tc);
                for (int i = 0; i < m; i++) printf(" (%d,%d,%d)", tri[i][0], tri[i][1], tri[i][2]);
                printf("\n"); fflush(stdout);
            }
        }
        return;
    }
    int a = -1; for (int i = 0; i < c3m; i++) if (!used[i]) { a = i; break; }
    used[a] = 1;
    for (int b = a + 1; b < c3m; b++) {
        if (used[b] || !gap_ok(a, b, c3m, g)) continue;
        if (t == 0 && first_b >= 0 && b != first_b) continue;
        used[b] = 1;
        for (int cc = b + 1; cc < c3m; cc++) {
            if (used[cc] || !gap_ok(a, cc, c3m, g) || !gap_ok(b, cc, c3m, g)) continue;
            if (t == 0 && first_c >= 0 && cc != first_c) continue;
            used[cc] = 1; tri[t][0] = a; tri[t][1] = b; tri[t][2] = cc;
            enumerate(m, g, used, tri, t + 1, -1, -1);
            used[cc] = 0;
        }
        used[b] = 0;
    }
    used[a] = 0;
}

int main(int argc, char **argv) {
    int m = atoi(argv[1]); int g = argc > 2 ? atoi(argv[2]) : 1;
    int c3m = 3 * m;
    /* parallelise over the first triple (0, b, c) */
    #pragma omp parallel for schedule(dynamic) collapse(2)
    for (int b = 1; b < MAXN; b++) for (int cc = 2; cc < MAXN; cc++) {
        if (b >= c3m || cc >= c3m || cc <= b) continue;
        int used[MAXN] = {0}; int tri[MAXM][3];
        enumerate(m, g, used, tri, 0, b, cc);
    }
    printf("m=%d n=%d gap>=%d: partitions=%lld non-3-edge-colourable=%lld of which 3-connected=%lld\n", m, 4 * m, g, total, noncol, snarks);
    return 0;
}
