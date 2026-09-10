/* snow.c — Gravner–Griffeath snow-crystal growth (Modeling snow crystal growth II, 2008)
 * on a hexagonal lattice in axial coordinates, with a SCHEDULED vapour density rho(t)
 * (the cloud the crystal falls through).  Exactly 12-fold symmetric: every neighbour sum
 * is computed as a sorted (order-independent) sum, so the deterministic dynamics respects
 * the lattice symmetries to the last bit.
 *
 * usage: snow N steps out_prefix  beta alpha theta kappa mu gamma  nsched  t1 rho1  t2 rho2 ...
 *   rho(t) = rho_k for t in [t_k, t_{k+1}), t_1 = 0; a NEGATIVE t_k means: switch when the crystal radius reaches |t_k|.
 * outputs (raw, N*N, row-major): out_prefix.t (int32 attachment step, -1 = vapour),
 *   out_prefix.c (float32 crystal mass), out_prefix.b (float32 boundary mass), out_prefix.d (float32 vapour)
 * log to stdout every 500 steps: step, crystal count, radius (hex distance), rho.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <omp.h>

static int N, R;
static unsigned char *a;   /* crystal indicator */
static double *b, *c, *d, *dn;
static int *tat;
static unsigned char *dom; /* inside hexagonal domain */

static inline int idx(int i, int j) { return i * N + j; }

static inline void sort6(double *v) {
    /* simple insertion sort of 6 doubles */
    for (int k = 1; k < 6; k++) { double x = v[k]; int m = k - 1; while (m >= 0 && v[m] > x) { v[m + 1] = v[m]; m--; } v[m + 1] = x; }
}

int main(int argc, char **argv) {
    if (argc < 12) { fprintf(stderr, "args\n"); return 1; }
    N = atoi(argv[1]); long steps = atol(argv[2]); const char *pre = argv[3];
    double beta = atof(argv[4]), alpha = atof(argv[5]), theta = atof(argv[6]), kappa = atof(argv[7]), mu = atof(argv[8]), gamma_ = atof(argv[9]);
    int nsched = atoi(argv[10]);
    long *ts = malloc(sizeof(long) * (nsched + 1)); double *rhos = malloc(sizeof(double) * (nsched + 1));
    for (int k = 0; k < nsched; k++) { ts[k] = atol(argv[11 + 2 * k]); rhos[k] = atof(argv[12 + 2 * k]); }
    ts[nsched] = steps + 1;
    R = (N - 1) / 2;
    size_t M = (size_t)N * N;
    a = calloc(M, 1); dom = calloc(M, 1); b = calloc(M, sizeof(double)); c = calloc(M, sizeof(double));
    d = calloc(M, sizeof(double)); dn = calloc(M, sizeof(double)); tat = malloc(M * sizeof(int));
    for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) {
        int di = i - R, dj = j - R;
        int Rd = R - 40;   /* the domain stops 40 cells short of the array so the reservoir is symmetric */
        dom[idx(i, j)] = (abs(di) <= Rd && abs(dj) <= Rd && abs(di + dj) <= Rd) ? 1 : 0;
        tat[idx(i, j)] = -1;
    }
    double rho = rhos[0];
    for (size_t k = 0; k < M; k++) d[k] = rho;
    a[idx(R, R)] = 1; c[idx(R, R)] = 1.0; d[idx(R, R)] = 0; tat[idx(R, R)] = 0;
    long ncry = 1; int rad = 0; int sk = 0;
    /* active bounding box in axial coordinates (crystal + margin) to save work early on */
    int lo = R - 3, hi = R + 3;
    /* neighbour offsets */
    const int oi[6] = {1, -1, 0, 0, 1, -1}, oj[6] = {0, 0, 1, -1, -1, 1};
    unsigned char *newa = calloc(M, 1);
    for (long t = 1; t <= steps; t++) {
        while (sk + 1 < nsched && ((ts[sk + 1] >= 0 && t >= ts[sk + 1]) || (ts[sk + 1] < 0 && rad >= -ts[sk + 1]))) {
            printf("cloud change at step %ld radius %d\n", t, rad); double old = rho; sk++; rho = rhos[sk];
            /* the cloud changes: the whole vapour field rescales (depletion profile kept, far field = new rho) */
            for (size_t k = 0; k < M; k++) if (!a[k]) d[k] *= rho / old; }
        /* the disturbed region spreads at most one cell per step */
        lo--; hi++; if (lo < 1) lo = 1; if (hi > N - 2) hi = N - 2;
        int L0 = lo > 1 ? lo : 1, L1 = hi < N - 2 ? hi : N - 2;
        /* (i) diffusion for non-crystal cells inside domain; outside domain = reservoir */
        #pragma omp parallel for schedule(static)
        for (int i = L0; i <= L1; i++) for (int j = L0; j <= L1; j++) {
            size_t k = idx(i, j);
            if (!dom[k]) { dn[k] = rho; continue; }
            if (a[k]) { dn[k] = 0; continue; }
            double v[6]; double dk = d[k];
            for (int q = 0; q < 6; q++) { size_t kk = idx(i + oi[q], j + oj[q]); v[q] = a[kk] ? dk : d[kk]; }
            sort6(v);
            dn[k] = (dk + ((v[0] + v[1]) + (v[2] + v[3]) + (v[4] + v[5]))) / 7.0;
        }
        /* (ii) freezing, (iii) attachment decision, (iv) melting — boundary cells */
        long added = 0; int newlo = R, newhi = R;
        #pragma omp parallel for schedule(static) reduction(+:added) reduction(min:newlo) reduction(max:newhi)
        for (int i = L0; i <= L1; i++) for (int j = L0; j <= L1; j++) {
            size_t k = idx(i, j);
            newa[k] = 0;
            if (!dom[k] || a[k]) { d[k] = dn[k]; continue; }
            int n = 0; double v[6];
            for (int q = 0; q < 6; q++) { size_t kk = idx(i + oi[q], j + oj[q]); n += a[kk]; v[q] = dn[kk]; }
            if (n == 0) { d[k] = dn[k]; continue; }
            /* freezing */
            double dk = dn[k];
            b[k] += (1 - kappa) * dk; c[k] += kappa * dk; dk = 0;
            /* attachment (synchronous: uses crystal state before this step) */
            int att = 0;
            if (n <= 2) { if (b[k] >= beta) att = 1; }
            else if (n == 3) {
                if (b[k] >= 1.0) att = 1;
                else { sort6(v); double s = ((v[0] + v[1]) + (v[2] + v[3]) + (v[4] + v[5])) + dn[k];
                       /* dn of crystal neighbours is 0; the diffusive mass in the neighbourhood */
                       if (s < theta && b[k] >= alpha) att = 1; }
            } else att = 1;
            if (att) { newa[k] = 1; added++; if (i < newlo) newlo = i; if (i > newhi) newhi = i; if (j < newlo) newlo = j; if (j > newhi) newhi = j; d[k] = 0; continue; }
            /* melting */
            double mb = mu * b[k], mc = gamma_ * c[k];
            b[k] -= mb; c[k] -= mc; dk += mb + mc;
            d[k] = dk;
        }
        if (added) {
            #pragma omp parallel for schedule(static)
            for (int i = L0; i <= L1; i++) for (int j = L0; j <= L1; j++) {
                size_t k = idx(i, j);
                if (newa[k]) { a[k] = 1; c[k] += b[k]; b[k] = 0; d[k] = 0; tat[k] = (int)t; }
            }
            ncry += added; if (newlo - 4 < lo) lo = newlo - 4 < 1 ? 1 : newlo - 4; if (newhi + 4 > hi) hi = newhi + 4 > N - 2 ? N - 2 : newhi + 4;
            int r1 = R - newlo > newhi - R ? R - newlo : newhi - R; if (r1 > rad) rad = r1;
        }
        if (t % 500 == 0 || t == steps) { printf("step %ld crystals %ld bbox_radius %d rho %.4f\n", t, ncry, rad, rho); fflush(stdout); }
        if (rad >= R - 40 - 30) { printf("crystal reached the edge at step %ld\n", t); break; }
    }
    char fn[512]; FILE *f;
    sprintf(fn, "%s.t", pre); f = fopen(fn, "wb"); fwrite(tat, sizeof(int), M, f); fclose(f);
    float *tmp = malloc(M * sizeof(float));
    for (size_t k = 0; k < M; k++) tmp[k] = (float)c[k];
    sprintf(fn, "%s.c", pre); f = fopen(fn, "wb"); fwrite(tmp, sizeof(float), M, f); fclose(f);
    for (size_t k = 0; k < M; k++) tmp[k] = (float)b[k];
    sprintf(fn, "%s.b", pre); f = fopen(fn, "wb"); fwrite(tmp, sizeof(float), M, f); fclose(f);
    for (size_t k = 0; k < M; k++) tmp[k] = (float)d[k];
    sprintf(fn, "%s.d", pre); f = fopen(fn, "wb"); fwrite(tmp, sizeof(float), M, f); fclose(f);
    printf("done crystals %ld\n", ncry);
    return 0;
}
