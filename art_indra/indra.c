// indra.c — Indra's net of pastel pearls: a path tracer for many mutually tangent mirror spheres.
//
// Each pearl is a tinted mirror with a thin nacre layer (diffuse pastel colour + optional soft glow),
// so a ray that bounces between pearls picks up one tint per reflection: the colour of a point in a gap
// is the WORD of reflections that led there (the Kleinian-group colouring of Indra's Pearls, done by
// physics). Table z = 0 with sorbet polka dots, soft sun, pastel sky with a rainbow around the
// antisolar point, thin-lens depth of field. BVH over spheres, OpenMP over rows.
//
// build: gcc -O3 -march=native -fopenmp indra.c -o indra -lm
// usage: ./indra spheres.bin W H spp out.f32 [key=val ...]   (spheres.bin: float64 rows x y z r R G B gl)
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct { double x, y, z; } V;
static inline V v3(double a, double b, double c) { V r = {a, b, c}; return r; }
static inline V add(V a, V b) { return v3(a.x + b.x, a.y + b.y, a.z + b.z); }
static inline V sub(V a, V b) { return v3(a.x - b.x, a.y - b.y, a.z - b.z); }
static inline V mul(V a, double s) { return v3(a.x * s, a.y * s, a.z * s); }
static inline V hm(V a, V b) { return v3(a.x * b.x, a.y * b.y, a.z * b.z); }
static inline double dot(V a, V b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
static inline V cross(V a, V b) { return v3(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x); }
static inline V nrm(V a) { double l = sqrt(dot(a, a)); return mul(a, 1.0 / l); }

// ---------------- params ----------------
#define NP 64
static char pk[NP][32]; static double pv[NP]; static int npar = 0;
static double P(const char *k, double d) { for (int i = 0; i < npar; i++) if (!strcmp(pk[i], k)) return pv[i]; return d; }

// ---------------- spheres + BVH ----------------
typedef struct { V c; double r; V tint; double glow; } S;
static S *sp; static int ns;
typedef struct { V lo, hi; int left, right, start, count; } Node;
static Node *nodes; static int nn = 0; static int *idx;

static void bounds(int s, int e, V *lo, V *hi) {
    *lo = v3(1e30, 1e30, 1e30); *hi = v3(-1e30, -1e30, -1e30);
    for (int i = s; i < e; i++) { S *q = &sp[idx[i]];
        lo->x = fmin(lo->x, q->c.x - q->r); lo->y = fmin(lo->y, q->c.y - q->r); lo->z = fmin(lo->z, q->c.z - q->r);
        hi->x = fmax(hi->x, q->c.x + q->r); hi->y = fmax(hi->y, q->c.y + q->r); hi->z = fmax(hi->z, q->c.z + q->r); }
}
static int ax_g;
static int cmpc(const void *a, const void *b) {
    double x = ax_g == 0 ? sp[*(int *)a].c.x : ax_g == 1 ? sp[*(int *)a].c.y : sp[*(int *)a].c.z;
    double y = ax_g == 0 ? sp[*(int *)b].c.x : ax_g == 1 ? sp[*(int *)b].c.y : sp[*(int *)b].c.z;
    return (x > y) - (x < y);
}
static int build(int s, int e) {
    int id = nn++; Node *n = &nodes[id];
    bounds(s, e, &n->lo, &n->hi);
    if (e - s <= 4) { n->left = n->right = -1; n->start = s; n->count = e - s; return id; }
    V d = sub(n->hi, n->lo);
    ax_g = (d.x > d.y && d.x > d.z) ? 0 : (d.y > d.z ? 1 : 2);
    qsort(idx + s, e - s, sizeof(int), cmpc);
    int m = (s + e) / 2;
    int l = build(s, m), r = build(m, e);
    nodes[id].left = l; nodes[id].right = r; nodes[id].count = 0;
    return id;
}
static inline int box(V o, V inv, V lo, V hi, double tmax) {
    double t0 = (lo.x - o.x) * inv.x, t1 = (hi.x - o.x) * inv.x; double tmin = fmin(t0, t1), tm = fmax(t0, t1);
    t0 = (lo.y - o.y) * inv.y; t1 = (hi.y - o.y) * inv.y; tmin = fmax(tmin, fmin(t0, t1)); tm = fmin(tm, fmax(t0, t1));
    t0 = (lo.z - o.z) * inv.z; t1 = (hi.z - o.z) * inv.z; tmin = fmax(tmin, fmin(t0, t1)); tm = fmin(tm, fmax(t0, t1));
    return tm >= fmax(tmin, 0) && tmin < tmax;
}
static int hit(V o, V d, double *tbest, int skip) {   // nearest sphere, -1 if none
    V inv = v3(1 / d.x, 1 / d.y, 1 / d.z); int st[128], sp_ = 0, who = -1; st[sp_++] = 0;
    while (sp_) { Node *n = &nodes[st[--sp_]];
        if (!box(o, inv, n->lo, n->hi, *tbest)) continue;
        if (n->left < 0) { for (int k = 0; k < n->count; k++) { int i = idx[n->start + k]; if (i == skip) continue;
                V oc = sub(o, sp[i].c); double b = dot(oc, d), c = dot(oc, oc) - sp[i].r * sp[i].r, D = b * b - c;
                if (D > 0) { double t = -b - sqrt(D); if (t > 1e-9 * (1 + sp[i].r) && t < *tbest) { *tbest = t; who = i; } } } }
        else { st[sp_++] = n->left; st[sp_++] = n->right; } }
    return who;
}

// ---------------- environment ----------------
static V SUN, SUNC;
static double rnd(uint64_t *s) { *s ^= *s << 13; *s ^= *s >> 7; *s ^= *s << 17; return (*s >> 11) * (1.0 / 9007199254740992.0); }
static V sky(V d) {
    double z = fmax(-1, fmin(1, d.z)), t = pow(fmax(z, 0), 0.6);
    V hor = v3(1.0, 0.91, 0.90), zen = v3(0.66, 0.80, 1.0);
    V c = add(mul(hor, 1 - t), mul(zen, t));
    if (z < 0) c = v3(1.0, 0.95, 0.88);
    double ang = acos(fmax(-1, fmin(1, -dot(d, SUN)))) * 180 / M_PI;
    double u = (ang - P("rb0", 39)) / P("rbw", 4.0);
    double env = exp(-pow((u - 0.5) / 0.42, 8));
    double xs[6] = {0, .2, .4, .6, .8, 1}, R[6] = {.75, .55, .55, .85, 1, 1}, G[6] = {.6, .75, .95, .95, .8, .55}, B[6] = {1, 1, .75, .55, .5, .6};
    double uu = fmax(0, fmin(1, u)); int k = (int)fmin(4, floor(uu * 5)); double f = (uu - xs[k]) / 0.2;
    V hue = v3(R[k] * (1 - f) + R[k + 1] * f, G[k] * (1 - f) + G[k + 1] * f, B[k] * (1 - f) + B[k + 1] * f);
    double rb = P("rbk", 0.6) * env * fmin(1, fmax(0, z * 8 + 0.3));
    c = add(mul(c, 1 - rb), mul(hue, rb * 1.15));
    double cs = dot(d, SUN);
    c = add(c, mul(SUNC, P("sunk", 9.0) * exp(-(1 - cs) / 0.0009) + 0.25 * exp(-(1 - cs) / 0.02)));
    return mul(c, P("skyk", 1.05));
}
static V DOT[9];
static V table_albedo(double x, double y) {
    double per = P("per", 0.9), rad = P("drad", 0.17) * per;
    int row = (int)floor(y / (per * 0.866)); double cxf = x / per - 0.5 * (row & 1); int col = (int)floor(cxf + 0.5);
    double best = 1e9; long hid = 0;
    for (int dr = -1; dr <= 1; dr++) for (int dc = -1; dc <= 1; dc++) {
        int r2 = row + dr, c2 = col + dc; double px = (c2 + 0.5 * (r2 & 1)) * per, py = (r2 + 0.5) * per * 0.866;
        double dd = hypot(x - px, y - py); if (dd < best) { best = dd; hid = (((long)r2 * 7919 + (long)c2 * 104729) % 9973 + 9973) % 9973; } }
    double cov = 1 / (1 + exp((best - rad) / 0.012)) * P("gk", 0.8);
    V a = DOT[hid % 9]; V paper = v3(0.985, 0.975, 0.965);
    return v3(paper.x * exp(-cov * a.x), paper.y * exp(-cov * a.y), paper.z * exp(-cov * a.z));
}
static V sun_dir(uint64_t *s) {
    V u = nrm(cross(SUN, v3(0, 0, 1))), w = cross(SUN, u); double a = P("sunrad", 0.03);
    double r = a * sqrt(rnd(s)), th = 2 * M_PI * rnd(s);
    return nrm(add(SUN, add(mul(u, r * cos(th)), mul(w, r * sin(th)))));
}
static V cos_hemi(V n, uint64_t *s) {
    double r1 = rnd(s), r2 = rnd(s), r = sqrt(r1), th = 2 * M_PI * r2;
    V u = nrm(fabs(n.x) > 0.5 ? cross(n, v3(0, 1, 0)) : cross(n, v3(1, 0, 0))), w = cross(n, u);
    return nrm(add(mul(n, sqrt(1 - r1)), add(mul(u, r * cos(th)), mul(w, r * sin(th)))));
}
static double TABLE;   // table on (1) / off (0)

// light arriving at a diffuse point p with normal n (sun + one sky sample)
static V diffuse_light(V p, V n, int self, uint64_t *s) {
    V L = v3(0, 0, 0);
    if (P("lightmode", 0) == 1) {   // window light from a point (the oculus), unshadowed, + soft ambient
        V lp = v3(P("lpx", 0), P("lpy", 0), P("lpz", 6));
        V l = nrm(sub(lp, p)); double c = fmax(0, dot(n, l));
        double a = P("wamb", 0.35) + P("wk", 0.9) * c;
        V R = v3(a * 1.0, a * 0.98, a * 0.96);
        if (P("wsun", 0) > 0) { V sd = sun_dir(s); double cs = dot(n, sd); double tt = 1e30;
            if (cs > 0 && hit(p, sd, &tt, self) < 0) R = add(R, mul(SUNC, P("wsun", 0) * cs)); }
        return R;
    }
    V sd = sun_dir(s); double c = dot(n, sd);
    if (c > 0) { double t = 1e30; if (hit(p, sd, &t, self) < 0) L = add(L, mul(SUNC, c * P("ksun", 0.95))); }
    V hd = cos_hemi(n, s); double t = 1e30; int w = hit(p, hd, &t, self);
    if (w < 0) { if (hd.z > 0 || !TABLE) L = add(L, mul(sky(hd), P("kamb", 0.55))); else L = add(L, mul(v3(0.95, 0.93, 0.92), P("kamb", 0.55) * 0.7)); }
    else L = add(L, mul(sp[w].tint, P("kamb", 0.55) * P("bounce", 0.45)));
    return L;
}

static V trace(V o, V d, uint64_t *s) {
    V L = v3(0, 0, 0), T = v3(1, 1, 1); int last = -1;
    int maxd = (int)P("maxd", 40);
    double nacre = P("nacre", 0.22), glowk = P("glowk", 0.0), F0 = P("F0", 0.55);
    for (int dep = 0; dep < maxd; dep++) {
        double t = 1e30; int w = hit(o, d, &t, last);
        if (dep == 0 && P("fog", 0) > 0) {     // single scattering of the sun along the primary segment
            int nst = (int)P("fogn", 24); double tm = fmin(t, P("fogmax", 6.0)), dt = tm / nst, acc = 0;
            double j0 = rnd(s);
            for (int k = 0; k < nst; k++) { V q = add(o, mul(d, (k + j0) * dt)); V sd = sun_dir(s); double tt = 1e30;
                if (hit(q, sd, &tt, -1) < 0) acc += dt; }
            double g = P("fogg", 0.6), mu = dot(d, SUN); double ph = (1 - g * g) / pow(1 + g * g - 2 * g * mu, 1.5) / (4 * M_PI) * 4 * M_PI;
            L = add(L, mul(v3(1.0, 0.95, 0.88), P("fog", 0) * acc * fmin(ph, 8.0)));
            if (P("fogonly", 0)) return L;
        }
        double tp = (TABLE && d.z < -1e-12) ? -o.z / d.z : 1e30;
        if (w < 0 && tp >= 1e30) { L = add(L, hm(T, sky(d))); return L; }
        if (tp < t) {   // table
            V p = add(o, mul(d, tp));
            V alb = table_albedo(p.x, p.y);
            V Li = diffuse_light(p, v3(0, 0, 1), -1, s);
            double fog = fmin(1, fmax(0, (tp - P("fog0", 30)) / P("fogw", 40)));
            V col = add(mul(hm(alb, Li), 1 - fog), mul(sky(nrm(v3(d.x, d.y, 0.02))), fog));
            L = add(L, hm(T, col)); return L;
        }
        S *q = &sp[w]; V p = add(o, mul(d, t)); V n = nrm(sub(p, q->c));
        double cs = fmax(0, -dot(d, n));
        double fr = F0 + (1 - F0) * pow(1 - cs, 5);            // mirror weight (Schlick-like, high base)
        // nacre: diffuse pastel layer + optional self glow
        V Li = diffuse_light(add(p, mul(n, 1e-9 * (1 + q->r))), n, w, s);
        V dif = add(hm(q->tint, Li), mul(q->tint, glowk * q->glow));
        L = add(L, mul(hm(T, dif), nacre * (1 - fr)));
        // mirror, tinted towards the pearl's colour
        double mt = P("mtint", 0.55);
        V spec = v3(fr * (1 - mt + mt * q->tint.x), fr * (1 - mt + mt * q->tint.y), fr * (1 - mt + mt * q->tint.z));
        T = hm(T, spec);
        if (fmax(T.x, fmax(T.y, T.z)) < 0.004) return L;
        d = nrm(sub(d, mul(n, 2 * dot(d, n)))); o = p; last = w;
    }
    // ran out of bounces deep in a gap: fall back to a soft pastel average
    V fb = v3(P("fbr", 0.92), P("fbg", 0.88), P("fbb", 0.95));
    return add(L, hm(T, fb));
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage\n"); return 1; }
    for (int i = 6; i < argc && npar < NP; i++) { char *e = strchr(argv[i], '='); if (!e) continue; *e = 0; strncpy(pk[npar], argv[i], 31); pv[npar++] = atof(e + 1); }
    FILE *f = fopen(argv[1], "rb"); fseek(f, 0, SEEK_END); long sz = ftell(f); fseek(f, 0, SEEK_SET);
    ns = sz / (8 * 8); double *buf = malloc(sz); fread(buf, 1, sz, f); fclose(f);
    sp = malloc(sizeof(S) * ns); idx = malloc(sizeof(int) * ns); nodes = malloc(sizeof(Node) * 2 * ns + 16);
    for (int i = 0; i < ns; i++) { double *b = buf + 8 * i; sp[i].c = v3(b[0], b[1], b[2]); sp[i].r = b[3]; sp[i].tint = v3(b[4], b[5], b[6]); sp[i].glow = b[7]; idx[i] = i; }
    build(0, ns);
    int W = atoi(argv[2]), H = atoi(argv[3]), spp = atoi(argv[4]);
    SUN = nrm(v3(P("sx", -0.17), P("sy", 0.97), P("sz", 0.25))); SUNC = v3(1.0, 0.97, 0.90);
    TABLE = P("table", 1);
    double dw[9][3] = {{1.00, 0.55, 0.65}, {1.0, 0.72, 0.52}, {1.0, 0.88, 0.45}, {0.75, 0.94, 0.50}, {0.52, 0.92, 0.78},
                       {0.52, 0.82, 1.0}, {0.64, 0.66, 1.0}, {0.80, 0.60, 1.0}, {1.0, 0.60, 0.90}};
    for (int i = 0; i < 9; i++) DOT[i] = v3(-log(dw[i][0]), -log(dw[i][1]), -log(dw[i][2]));
    V eye = v3(P("ex", 0), P("ey", -10), P("ez", 4)), look = v3(P("lx", 0), P("ly", 0), P("lz", 1));
    V fw = nrm(sub(look, eye)), rt = nrm(cross(fw, v3(0, 0, 1))), up = cross(rt, fw);
    double fov = P("fov", 0.35), ap = P("ap", 0.0), focus = P("focus", sqrt(dot(sub(look, eye), sub(look, eye))));
    int r0 = (int)P("r0", 0), r1 = (int)P("r1", H);
    float *img = calloc((size_t)W * (r1 - r0) * 3, sizeof(float));
    fprintf(stderr, "spheres %d nodes %d  %dx%d rows %d..%d spp %d\n", ns, nn, W, H, r0, r1, spp);
    int done = 0;
#pragma omp parallel for schedule(dynamic, 1)
    for (int y = r0; y < r1; y++) {
        uint64_t s = 0x9E3779B97F4A7C15ULL ^ ((uint64_t)y * 0x2545F4914F6CDD1DULL);
        for (int k = 0; k < 4; k++) rnd(&s);
        for (int x = 0; x < W; x++) {
            V acc = v3(0, 0, 0);
            for (int k = 0; k < spp; k++) {
                double sx = ((x + rnd(&s)) / W - 0.5) * 2 * tan(fov), sy = -((y + rnd(&s)) / W - 0.5 * H / W) * 2 * tan(fov);
                V d = nrm(add(fw, add(mul(rt, sx), mul(up, sy)))); V o = eye;
                if (ap > 0) { V tg = add(eye, mul(d, focus / dot(d, fw))); double rr = ap * sqrt(rnd(&s)), th = 2 * M_PI * rnd(&s);
                    o = add(eye, add(mul(rt, rr * cos(th)), mul(up, rr * sin(th)))); d = nrm(sub(tg, o)); }
                acc = add(acc, trace(o, d, &s));
            }
            size_t q = ((size_t)(y - r0) * W + x) * 3;
            img[q] = acc.x / spp; img[q + 1] = acc.y / spp; img[q + 2] = acc.z / spp;
        }
#pragma omp atomic
        done++;
        if (done % 64 == 0) { fprintf(stderr, "rows %d/%d\n", done, r1 - r0); }
    }
    FILE *o = fopen(argv[5], "wb"); fwrite(img, sizeof(float), (size_t)W * (r1 - r0) * 3, o); fclose(o);
    return 0;
}
