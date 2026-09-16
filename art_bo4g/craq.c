/* craq.c — a drying film that cracks: triangular spring lattice on an elastic substrate.
 *
 * Nodes (i,j) on a triangular lattice, rest positions x0 = j + (i&1)/2, y0 = i*sqrt(3)/2.
 * Film bonds (6 neighbours) have spring constant 1 and a rest length l0 = 1 - eps(t) that shrinks
 * as the film dries; every node is also tied to its substrate anchor by a spring ks (Winkler
 * coupling), so stress is screened over a length ~ sqrt(1/ks) from every free edge (crack).
 * Quasi-static loading: eps grows in small steps; whenever any bond's strain exceeds its own
 * random threshold th_b, the most over-strained bond breaks and the lattice relaxes (SOR) in a
 * window around it before the next candidate is examined — so a crack propagates one bond at a
 * time from its tip, and turns to meet older cracks at right angles (the relieved direction).
 *
 * Output: node displacements, the break order of every bond (-1 = intact), and eps at each break.
 *   usage: ./craq W H ks th disorder deps seed out.bin
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

static int W, H;
static double ks, th0, dis, deps;
static double *ux, *uy;         /* displacements */
static double *thr;             /* thresholds per bond (3 per node) */
static int *brk;                /* break order per bond, -1 intact */
static double *brk_eps;
static double *L0;              /* natural length of each bond at eps = 0 (jittered lattice) */
static int nbroken = 0;

/* bond b of node (i,j): 0 -> (i, j+1); 1 -> (i+1, jl); 2 -> (i+1, jl+1) with jl = j - 1 + (i&1) */
static inline int nb(int i, int j, int b, int *ii, int *jj) {
    if (b == 0) { *ii = i; *jj = j + 1; }
    else { int jl = j - 1 + (i & 1); *ii = i + 1; *jj = jl + (b == 2); }
    return (*ii >= 0 && *ii < H && *jj >= 0 && *jj < W);
}
static double *RX, *RY;   /* jittered rest positions */
static inline double X0(int i, int j) { return RX[i * W + j]; }
static inline double Y0(int i, int j) { return RY[i * W + j]; }

static double rng_u(unsigned long long *s) { *s ^= *s << 13; *s ^= *s >> 7; *s ^= *s << 17; return (*s >> 11) * (1.0 / 9007199254740992.0); }

/* force on node (i,j) from all intact bonds + substrate; also returns effective stiffness */
static void force(int i, int j, double l0, double *fx, double *fy, double *kk) {
    double Fx = -ks * ux[i * W + j], Fy = -ks * uy[i * W + j], K = ks;
    for (int b = 0; b < 3; b++) {
        int ii, jj;
        if (!nb(i, j, b, &ii, &jj)) continue;
        if (brk[(i * W + j) * 3 + b] >= 0) continue;
        double dx = X0(ii, jj) + ux[ii * W + jj] - X0(i, j) - ux[i * W + j];
        double dy = Y0(ii, jj) + uy[ii * W + jj] - Y0(i, j) - uy[i * W + j];
        double d = sqrt(dx * dx + dy * dy);
        double f = (d - l0 * L0[(i * W + j) * 3 + b]);
        Fx += f * dx / d; Fy += f * dy / d; K += 1.0;
    }
    /* bonds pointing back: neighbours for which (i,j) is the second node */
    for (int b = 0; b < 3; b++) {
        int ii, jj;
        if (b == 0) { ii = i; jj = j - 1; }
        else { ii = i - 1; jj = (b == 1) ? j + (i & 1) : j - 1 + (i & 1); }
        /* (ii,jj) has bond b to (i,j)? check */
        if (ii < 0 || ii >= H || jj < 0 || jj >= W) continue;
        int ti, tj; nb(ii, jj, b, &ti, &tj);
        if (ti != i || tj != j) continue;
        if (brk[(ii * W + jj) * 3 + b] >= 0) continue;
        double dx = X0(ii, jj) + ux[ii * W + jj] - X0(i, j) - ux[i * W + j];
        double dy = Y0(ii, jj) + uy[ii * W + jj] - Y0(i, j) - uy[i * W + j];
        double d = sqrt(dx * dx + dy * dy);
        double f = (d - l0 * L0[(ii * W + jj) * 3 + b]);
        Fx += f * dx / d; Fy += f * dy / d; K += 1.0;
    }
    *fx = Fx; *fy = Fy; *kk = K;
}

static double TOL = 5e-6;
static void relax_window(int i0, int i1, int j0, int j1, double l0, int sweeps, double omega) {
    /* SOR until the largest displacement update in a sweep is below TOL (or `sweeps` sweeps) */
    if (i0 < 0) i0 = 0; if (j0 < 0) j0 = 0; if (i1 > H) i1 = H; if (j1 > W) j1 = W;
    for (int s = 0; s < sweeps; s++) {
        double mx = 0;
        for (int i = i0; i < i1; i++) for (int j = j0; j < j1; j++) {
            double fx, fy, k; force(i, j, l0, &fx, &fy, &k);
            double dx = omega * fx / k, dy = omega * fy / k;
            ux[i * W + j] += dx; uy[i * W + j] += dy;
            double a = fabs(dx) + fabs(dy); if (a > mx) mx = a;
        }
        if (mx < TOL) break;
    }
}

static double bond_strain(int i, int j, int b, double l0) {
    int ii, jj; if (!nb(i, j, b, &ii, &jj)) return -1;
    double dx = X0(ii, jj) + ux[ii * W + jj] - X0(i, j) - ux[i * W + j];
    double dy = Y0(ii, jj) + uy[ii * W + jj] - Y0(i, j) - uy[i * W + j];
    double r = l0 * L0[(i * W + j) * 3 + b];
    return (sqrt(dx * dx + dy * dy) - r) / r;
}

int main(int argc, char **argv) {
    if (argc < 10) { fprintf(stderr, "usage: W H ks th disorder deps seed out modamp\n"); return 1; }
    double modamp = atof(argv[9]);
    W = atoi(argv[1]); H = atoi(argv[2]); ks = atof(argv[3]); th0 = atof(argv[4]); dis = atof(argv[5]);
    deps = atof(argv[6]); unsigned long long seed = strtoull(argv[7], 0, 10) * 2654435761ULL + 88172645463325252ULL;
    const char *out = argv[8];
    int NN = W * H;
    ux = calloc(NN, sizeof(double)); uy = calloc(NN, sizeof(double));
    RX = malloc(NN * sizeof(double)); RY = malloc(NN * sizeof(double));
    double jit = (argc > 10) ? atof(argv[10]) : 0.25;
    for (int i = 0; i < H; i++) for (int j = 0; j < W; j++) {
        RX[i * W + j] = j + 0.5 * (i & 1) + jit * (2 * rng_u(&seed) - 1);
        RY[i * W + j] = i * 0.8660254037844386 + jit * (2 * rng_u(&seed) - 1);
    }
    thr = malloc(NN * 3 * sizeof(double)); brk = malloc(NN * 3 * sizeof(int)); brk_eps = malloc(NN * 3 * sizeof(double));
    L0 = malloc(NN * 3 * sizeof(double));
    for (int i = 0; i < H; i++) for (int j = 0; j < W; j++) for (int b = 0; b < 3; b++) {
        int ii, jj; L0[(i * W + j) * 3 + b] = 1.0;
        if (nb(i, j, b, &ii, &jj)) L0[(i * W + j) * 3 + b] = hypot(X0(ii, jj) - X0(i, j), Y0(ii, jj) - Y0(i, j));
    }
    for (int k = 0; k < NN * 3; k++) { thr[k] = th0 * (1 + dis * (2 * rng_u(&seed) - 1)); brk[k] = -1; brk_eps[k] = 0; }
    /* a soft large-scale modulation of the thresholds (paint is never uniform): smooth random field */
    {
        int cw = W / 6 + 1, ch = H / 6 + 1;
        double *coarse = malloc((W / cw + 2) * (H / ch + 2) * sizeof(double));
        for (int k = 0; k < (W / cw + 2) * (H / ch + 2); k++) coarse[k] = 2 * rng_u(&seed) - 1;
        for (int i = 0; i < H; i++) for (int j = 0; j < W; j++) {
            double fi = (double)i / ch, fj = (double)j / cw; int ci = (int)fi, cj = (int)fj; double ti = fi - ci, tj = fj - cj;
            int cwn = W / cw + 2;
            double v = (1 - ti) * ((1 - tj) * coarse[ci * cwn + cj] + tj * coarse[ci * cwn + cj + 1]) +
                       ti * ((1 - tj) * coarse[(ci + 1) * cwn + cj] + tj * coarse[(ci + 1) * cwn + cj + 1]);
            for (int b = 0; b < 3; b++) thr[(i * W + j) * 3 + b] *= (1 + modamp * v);
        }
        free(coarse);
    }
    double eps = 0.0;
    int R = (int)(1.2 / sqrt(ks)) + 4;   /* relaxation window ~ 3 screening lengths */
    long events = 0;
    fprintf(stderr, "W=%d H=%d ks=%g th=%g dis=%g deps=%g R=%d\n", W, H, ks, th0, dis, deps, R);
    for (int stage = 0; stage < 100000; stage++) {
        eps += deps;
        double l0 = 1.0 - eps;
        relax_window(0, H, 0, W, l0, 3000, 1.8);
        /* break loop */
        for (;;) {
            double best = 1.0; int bi = -1, bj = -1, bb = -1;
            for (int i = 0; i < H; i++) for (int j = 0; j < W; j++) for (int b = 0; b < 3; b++) {
                int k = (i * W + j) * 3 + b; if (brk[k] >= 0) continue;
                double e = bond_strain(i, j, b, l0); if (e < 0) continue;
                double r = e / thr[k]; if (r > best) { best = r; bi = i; bj = j; bb = b; }
            }
            if (bi < 0) break;
            int k = (bi * W + bj) * 3 + bb; brk[k] = nbroken; brk_eps[k] = eps; nbroken++; events++;
            /* propagate: relax a window around the new tip, then look again (the tip is the most strained) */
            relax_window(bi - R, bi + R + 1, bj - R, bj + R + 1, l0, 300, 1.8);
        }
        double frac = (double)nbroken / (3.0 * NN);
        if (stage % 5 == 0) fprintf(stderr, "stage %d eps=%.4f broken=%d (%.3f)\n", stage, eps, nbroken, frac);
        if (frac > 0.10 || eps > 0.6) break;
    }
    FILE *f = fopen(out, "wb");
    fwrite(&W, 4, 1, f); fwrite(&H, 4, 1, f); fwrite(&nbroken, 4, 1, f); fwrite(&eps, 8, 1, f);
    fwrite(ux, 8, NN, f); fwrite(uy, 8, NN, f); fwrite(brk, 4, NN * 3, f); fwrite(brk_eps, 8, NN * 3, f);
    fclose(f);
    fprintf(stderr, "done: %d bonds broken, eps=%.4f, written %s\n", nbroken, eps, out);
    return 0;
}
