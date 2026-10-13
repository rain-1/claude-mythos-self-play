// beads.c — lampwork glass beads on white paper: a small path tracer with real refraction.
//
// Spheres resting on a table z = 0 are either clear tinted glass (Fresnel + Snell + Beer–Lambert) or
// glossy opaque candy (diffuse + clear coat). Silk thread = capsules through the bead centres, visible
// through the glass. The table is lit by a soft sun (next-event estimation, glass counted as opaque
// there) + a pastel sky dome (cosine sampled, occluded) + a PHOTON-MAPPED caustic layer: sun photons
// that pass through glass and land on the table are binned into a fine grid, so every bead throws
// a focused coloured spot of its own light. OpenMP over rows.
//
// build: gcc -O3 -march=native -fopenmp beads.c -o beads -lm
// usage: ./beads scene.bin W H spp out.f32 [key=val ...]
//   scene.bin: int32 ns, int32 nc; ns rows float64 [x y z r type R G B]  (type 0 glass: RGB = absorption/unit radius,
//              type 1 candy: RGB = albedo), nc rows float64 [ax ay az bx by bz r R G B] (capsules, albedo)
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
static inline V vexp(V a) { return v3(exp(a.x), exp(a.y), exp(a.z)); }

#define NP 96
static char pk[NP][32]; static double pv[NP]; static int npar = 0;
static double P(const char *k, double d) { for (int i = 0; i < npar; i++) if (!strcmp(pk[i], k)) return pv[i]; return d; }

// ---------------- rng ----------------
typedef struct { uint64_t s; } R;
static inline double rnd(R *r) { r->s ^= r->s << 13; r->s ^= r->s >> 7; r->s ^= r->s << 17; return (r->s >> 11) * (1.0 / 9007199254740992.0); }

// ---------------- primitives ----------------
// kind 0 sphere, 1 capsule
typedef struct { int kind, type; V a, b; double r; V col; V lo, hi; } Pr;
static Pr *pr; static int npr;
typedef struct { V lo, hi; int left, right, start, count; } Node;
static Node *nodes; static int nn = 0; static int *idx;
static int ax_g;
static double cen(int i, int a) { V c = mul(add(pr[i].lo, pr[i].hi), 0.5); return a == 0 ? c.x : a == 1 ? c.y : c.z; }
static int cmpc(const void *a, const void *b) { double x = cen(*(int *)a, ax_g), y = cen(*(int *)b, ax_g); return (x > y) - (x < y); }
static int build(int s, int e) {
    int id = nn++; Node *n = &nodes[id];
    n->lo = v3(1e30, 1e30, 1e30); n->hi = v3(-1e30, -1e30, -1e30);
    for (int i = s; i < e; i++) { Pr *q = &pr[idx[i]];
        n->lo = v3(fmin(n->lo.x, q->lo.x), fmin(n->lo.y, q->lo.y), fmin(n->lo.z, q->lo.z));
        n->hi = v3(fmax(n->hi.x, q->hi.x), fmax(n->hi.y, q->hi.y), fmax(n->hi.z, q->hi.z)); }
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
// sphere: nearest t > eps (both roots, so rays from inside work)
static inline double isph(V o, V d, V c, double r) {
    V oc = sub(o, c); double b = dot(oc, d), cc = dot(oc, oc) - r * r, D = b * b - cc;
    if (D < 0) return 1e30; double s = sqrt(D), eps = 1e-7 * (1 + r);
    double t = -b - s; if (t > eps) return t; t = -b + s; if (t > eps) return t; return 1e30;
}
// capsule (outside hits only)
static inline double icap(V o, V d, V a, V b, double r, V *nout) {
    V ba = sub(b, a), oa = sub(o, a);
    double baba = dot(ba, ba), bard = dot(ba, d), baoa = dot(ba, oa), rdoa = dot(d, oa), oaoa = dot(oa, oa);
    double A = baba - bard * bard, B = baba * rdoa - baoa * bard, C = baba * oaoa - baoa * baoa - r * r * baba;
    double h = B * B - A * C, best = 1e30;
    if (h >= 0 && A > 1e-12) { double t = (-B - sqrt(h)) / A; double y = baoa + t * bard;
        if (t > 1e-7 && y > 0 && y < baba) { best = t; V p = add(o, mul(d, t)); V q = add(a, mul(ba, y / baba)); *nout = nrm(sub(p, q)); return best; } }
    // caps
    for (int k = 0; k < 2; k++) { V c = k ? b : a; double t = isph(o, d, c, r);
        if (t < best) { V oc = sub(add(o, mul(d, t)), c); if (dot(oc, oc) < r * r * 1.0001 && dot(sub(o, c), sub(o, c)) > r * r) { best = t; *nout = nrm(oc); } } }
    return best;
}
static int hit(V o, V d, double *tb, V *nout, int mask) {   // mask bit0 spheres, bit1 capsules
    V inv = v3(1 / d.x, 1 / d.y, 1 / d.z); int st[128], sp = 0, who = -1; st[sp++] = 0;
    while (sp) { Node *n = &nodes[st[--sp]];
        if (!box(o, inv, n->lo, n->hi, *tb)) continue;
        if (n->left < 0) { for (int k = 0; k < n->count; k++) { int i = idx[n->start + k]; Pr *q = &pr[i];
                if (q->kind == 0) { if (!(mask & 1)) continue; double t = isph(o, d, q->a, q->r);
                    if (t < *tb) { *tb = t; who = i; *nout = nrm(sub(add(o, mul(d, t)), q->a)); } }
                else { if (!(mask & 2)) continue; V nn2; double t = icap(o, d, q->a, q->b, q->r, &nn2);
                    if (t < *tb) { *tb = t; who = i; *nout = nn2; } } } }
        else { st[sp++] = n->left; st[sp++] = n->right; } }
    return who;
}
// shadow transmittance toward a light: glass counts as tinted (cheap) when glassT = 1, opaque when 0
static V shadowT(V o, V d, int glassT) {
    V T = v3(1, 1, 1); V inv = v3(1 / d.x, 1 / d.y, 1 / d.z); int st[128], sp = 0; st[sp++] = 0;
    while (sp) { Node *n = &nodes[st[--sp]];
        if (!box(o, inv, n->lo, n->hi, 1e30)) continue;
        if (n->left < 0) { for (int k = 0; k < n->count; k++) { Pr *q = &pr[idx[n->start + k]];
                if (q->kind == 0) { V oc = sub(o, q->a); double b = dot(oc, d), c = dot(oc, oc) - q->r * q->r, D = b * b - c;
                    if (D <= 0) continue; double s = sqrt(D), t1 = -b - s, t2 = -b + s; if (t2 <= 1e-7) continue;
                    if (q->type == 1 || !glassT) return v3(0, 0, 0);
                    double L = t2 - fmax(t1, 0); T = hm(T, mul(vexp(mul(q->col, -L / q->r)), 0.82)); }
                else { V nn2; if (icap(o, d, q->a, q->b, q->r, &nn2) < 1e29) return v3(0, 0, 0); } } }
        else { st[sp++] = n->left; st[sp++] = n->right; } }
    return T;
}

// ---------------- light ----------------
static V SUN, SUNC; static double SUNCOS, ESUN;
static V SKYZ, SKYH, SKYG;     // zenith, horizon, ground-bounce
static double WINX0, WINX1, WINY0, WINY1, WINB;  // window glint (direction box in az/el)
static int NOWIN=0;
static V sky(V d) {
    double z = fmax(d.z, 0); double t = pow(1 - z, 2.2);
    V c = add(mul(SKYZ, 1 - t), mul(SKYH, t));
    if (d.z < 0) c = SKYG;
    // soft window (big bright rectangle) for glints
    double az = atan2(d.y, d.x), el = asin(fmax(-1, fmin(1, d.z)));
    if (!NOWIN && az > WINX0 && az < WINX1 && el > WINY0 && el < WINY1) {
        double mx = fmin(az - WINX0, WINX1 - az), my = fmin(el - WINY0, WINY1 - el);
        double bar = 1.0;
        c = add(c, mul(v3(1, 0.99, 0.96), WINB * bar * fmin(1, fmin(mx, my) / 0.06)));
    }
    if (dot(d, SUN) > SUNCOS) c = add(c, mul(SUNC, P("sunvis", 40.0)));
    return c;
}
static V paper(double x, double y);
// ---------------- caustic map ----------------
static float *CM; static int CMN; static double CMX0, CMY0, CMS;   // grid origin, cell size
static V caus(double x, double y) {
    if (!CM) return v3(0, 0, 0);
    double gx = (x - CMX0) / CMS - 0.5, gy = (y - CMY0) / CMS - 0.5; int ix = (int)floor(gx), iy = (int)floor(gy);
    if (ix < 0 || iy < 0 || ix >= CMN - 1 || iy >= CMN - 1) return v3(0, 0, 0);
    double fx = gx - ix, fy = gy - iy; V r = v3(0, 0, 0);
    for (int c = 0; c < 3; c++) {
        double a = CM[((size_t)iy * CMN + ix) * 3 + c], b = CM[((size_t)iy * CMN + ix + 1) * 3 + c];
        double e = CM[((size_t)(iy + 1) * CMN + ix) * 3 + c], f = CM[((size_t)(iy + 1) * CMN + ix + 1) * 3 + c];
        double v = (a * (1 - fx) + b * fx) * (1 - fy) + (e * (1 - fx) + f * fx) * fy;
        if (c == 0) r.x = v; else if (c == 1) r.y = v; else r.z = v; }
    return r;
}
static double IOR, AP, FD;
static inline double fresnel(double cosi, double eta) {   // eta = n1/n2
    double sint2 = eta * eta * (1 - cosi * cosi); if (sint2 >= 1) return 1;
    double cost = sqrt(1 - sint2);
    double rs = (eta * cosi - cost) / (eta * cosi + cost), rp = (cosi - eta * cost) / (cosi + eta * cost);
    return 0.5 * (rs * rs + rp * rp);
}
static void onb(V n, V *t, V *b) { V a = fabs(n.x) > 0.9 ? v3(0, 1, 0) : v3(1, 0, 0); *t = nrm(cross(a, n)); *b = cross(n, *t); }
static V cosdir(V n, R *rg) { double u = rnd(rg), v = rnd(rg), r = sqrt(u), ph = 2 * M_PI * v; V t, b; onb(n, &t, &b);
    return nrm(add(add(mul(t, r * cos(ph)), mul(b, r * sin(ph))), mul(n, sqrt(fmax(0, 1 - u))))); }
static V sundir(R *rg) {   // sample within the sun disc
    double u = rnd(rg), v = rnd(rg); double ct = 1 - u * (1 - SUNCOS), st = sqrt(1 - ct * ct), ph = 2 * M_PI * v; V t, b; onb(SUN, &t, &b);
    return nrm(add(add(mul(t, st * cos(ph)), mul(b, st * sin(ph))), mul(SUN, ct)));
}
// diffuse shading at a point with normal n, albedo alb; table=1 adds caustic & uses opaque-glass shadows
static V diffuse(V p, V n, V alb, int table, R *rg) {
    V L = v3(0, 0, 0); V o = add(p, mul(n, 1e-6));
    V ld = sundir(rg); double c = dot(ld, n);
    if (c > 0) L = add(L, mul(hm(SUNC, shadowT(o, ld, !table)), ESUN * c / M_PI));
    // sky (one occluded cosine sample)
    V sd = cosdir(n, rg); V T = shadowT(o, sd, 1);
    double z = fmax(sd.z, 0), tt = pow(1 - z, 2.2); V sk = sd.z < 0 ? SKYG : add(mul(SKYZ, 1 - tt), mul(SKYH, tt));
    L = add(L, hm(T, sk));
    // bounce floor approximation for upward-facing surfaces missing: add a little ambient
    L = add(L, mul(SKYG, P("amb", 0.04)));
    if (table) L = add(L, mul(caus(p.x, p.y), 1.0 / M_PI));
    return hm(L, alb);
}
static V radiance(V o, V d, R *rg) {
    V T = v3(1, 1, 1), acc = v3(0, 0, 0); int inside = -1;
    for (int depth = 0; depth < 14; depth++) {
        double tb = 1e30; V n; int who = hit(o, d, &tb, &n, 3);
        double tz = (d.z < 0 && inside < 0) ? -o.z / d.z : 1e30;
        if (tz < tb && tz > 1e-9) {   // table
            V p = add(o, mul(d, tz)); V alb = paper(p.x, p.y);
            acc = add(acc, hm(T, diffuse(p, v3(0, 0, 1), alb, 1, rg))); return acc;
        }
        if (who < 0) { acc = add(acc, hm(T, sky(d))); return acc; }
        Pr *q = &pr[who]; V p = add(o, mul(d, tb));
        if (q->kind == 1) {   // silk thread with a little sheen
            V c = diffuse(p, n, q->col, 0, rg);
            if (inside >= 0) { /* seen through glass: lit by the transmitted light, already approximated */ }
            V h = nrm(sub(SUN, d)); double sp = pow(fmax(0, dot(h, n)), 30) * 0.15 * ESUN;
            acc = add(acc, hm(T, add(c, mul(SUNC, sp)))); return acc;
        }
        if (q->type == 1) {   // candy: clear coat + diffuse
            double ci = fabs(dot(d, n)); double F = 0.04 + 0.96 * pow(1 - ci, 5);
            if (rnd(rg) < F) { d = nrm(sub(d, mul(n, 2 * dot(d, n)))); o = add(p, mul(n, 1e-7)); continue; }
            acc = add(acc, hm(T, diffuse(p, n, q->col, 0, rg))); return acc;
        }
        // glass
        int entering = dot(d, n) < 0; V nn2 = entering ? n : mul(n, -1);
        if (!entering) { T = hm(T, vexp(mul(q->col, -tb / q->r))); }
        double eta = entering ? 1.0 / IOR : IOR; double ci = -dot(d, nn2);
        double F = fresnel(ci, eta);
        if (rnd(rg) < F) { d = nrm(add(d, mul(nn2, 2 * ci))); o = add(p, mul(nn2, 1e-7)); /* stays on same side */
            if (!entering) inside = who; else inside = -1; }
        else { double k = 1 - eta * eta * (1 - ci * ci); d = nrm(add(mul(d, eta), mul(nn2, eta * ci - sqrt(k)))); o = sub(p, mul(nn2, 1e-7));
            inside = entering ? who : -1; }
        if (depth > 6) { double m = fmax(T.x, fmax(T.y, T.z)); if (m < 0.05) { if (rnd(rg) > m * 10) return acc; T = mul(T, 1 / (m * 10)); } }
    }
    return acc;
}
// ---------------- paper ----------------
static double hash2(int x, int y) { uint64_t h = (uint64_t)(x * 73856093) ^ (uint64_t)(y * 19349663) ^ 0x9e3779b97f4a7c15ull; h ^= h >> 33; h *= 0xff51afd7ed558ccdull; h ^= h >> 33; return (h & 0xffffff) / 16777216.0; }
static double vnoise(double x, double y) { int ix = floor(x), iy = floor(y); double fx = x - ix, fy = y - iy; fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy);
    return (hash2(ix, iy) * (1 - fx) + hash2(ix + 1, iy) * fx) * (1 - fy) + (hash2(ix, iy + 1) * (1 - fx) + hash2(ix + 1, iy + 1) * fx) * fy; }
static V PAPER; static double GRAIN;
static float *DOTS; static int DOTN; static double DOTX0, DOTY0, DOTS_;   // optional albedo texture (printed motif)
static V paper(double x, double y) {
    double g = 1 + GRAIN * (vnoise(x * 3.1, y * 3.1) - 0.5) + 0.5 * GRAIN * (vnoise(x * 11, y * 11) - 0.5);
    V a = mul(PAPER, g);
    if (DOTS) { int ix = (int)((x - DOTX0) / DOTS_), iy = (int)((y - DOTY0) / DOTS_);
        if (ix >= 0 && iy >= 0 && ix < DOTN && iy < DOTN) { size_t k = ((size_t)iy * DOTN + ix) * 3; a = hm(a, v3(DOTS[k], DOTS[k + 1], DOTS[k + 2])); } }
    return a;
}

// ---------------- photon pass ----------------
static void photons(double x0, double y0, double x1, double y1, double nph) {
    CMN = (int)P("cmn", 2048); CMX0 = x0; CMY0 = y0; CMS = fmax(x1 - x0, y1 - y0) / CMN;
    CM = calloc((size_t)CMN * CMN * 3, sizeof(float));
    // photons on a plane perpendicular to SUN, covering the bead bounding box (z in [0, zmax])
    V t, b; onb(SUN, &t, &b);
    double zmax = 0; for (int i = 0; i < npr; i++) zmax = fmax(zmax, pr[i].hi.z);
    // project box corners
    double umin = 1e30, umax = -1e30, vmin = 1e30, vmax = -1e30;
    for (int k = 0; k < 8; k++) { V c = v3(k & 1 ? x1 : x0, k & 2 ? y1 : y0, k & 4 ? zmax : 0);
        double u = dot(c, t), v = dot(c, b); umin = fmin(umin, u); umax = fmax(umax, u); vmin = fmin(vmin, v); vmax = fmax(vmax, v); }
    double area = (umax - umin) * (vmax - vmin); double side = sqrt(area / nph);
    int NU = (int)((umax - umin) / side) + 1, NV = (int)((vmax - vmin) / side) + 1;
    double flux = ESUN * side * side;   // power per photon (per unit sun radiance colour)
    double cell = CMS * CMS;
    fprintf(stderr, "photons %d x %d\n", NU, NV);
    #pragma omp parallel
    {
        float *loc = calloc((size_t)CMN * CMN * 3, sizeof(float));   // per-thread to avoid atomics
        #pragma omp for schedule(dynamic, 4)
        for (int iv = 0; iv < NV; iv++) { R rg = {0x1234567ull + iv * 2654435761ull};
            for (int iu = 0; iu < NU; iu++) {
                double u = umin + (iu + rnd(&rg)) * side, v = vmin + (iv + rnd(&rg)) * side;
                V d = mul(sundir(&rg), -1); V o = add(add(mul(t, u), mul(b, v)), mul(SUN, 50 + 2 * zmax));
                // quick reject: must hit a glass sphere first
                V pw = SUNC; int bounced = 0;
                for (int depth = 0; depth < 16; depth++) {
                    double tb = 1e30; V n; int who = hit(o, d, &tb, &n, 3);
                    double tz = d.z < 0 ? -o.z / d.z : 1e30;
                    if (tz < tb) { if (bounced) { V p = add(o, mul(d, tz)); int ix = (int)((p.x - CMX0) / CMS), iy = (int)((p.y - CMY0) / CMS);
                            if (ix >= 0 && iy >= 0 && ix < CMN && iy < CMN) { size_t kk = ((size_t)iy * CMN + ix) * 3;
                                loc[kk] += pw.x * flux / cell; loc[kk + 1] += pw.y * flux / cell; loc[kk + 2] += pw.z * flux / cell; } }
                        break; }
                    if (who < 0) break;
                    Pr *q = &pr[who]; if (q->kind == 1 || q->type == 1) break;
                    V p = add(o, mul(d, tb));
                    int entering = dot(d, n) < 0; V nn2 = entering ? n : mul(n, -1);
                    if (!entering) pw = hm(pw, vexp(mul(q->col, -tb / q->r)));
                    double eta = entering ? 1.0 / IOR : IOR; double ci = -dot(d, nn2); double F = fresnel(ci, eta);
                    if (rnd(&rg) < F) { d = nrm(add(d, mul(nn2, 2 * ci))); o = add(p, mul(nn2, 1e-7)); }
                    else { double k = 1 - eta * eta * (1 - ci * ci); d = nrm(add(mul(d, eta), mul(nn2, eta * ci - sqrt(k)))); o = sub(p, mul(nn2, 1e-7)); }
                    bounced = 1;
                }
            } }
        #pragma omp critical
        { for (size_t k = 0; k < (size_t)CMN * CMN * 3; k++) CM[k] += loc[k]; }
        free(loc);
    }
    // small blur (separable binomial, radius br)
    int br = (int)P("cblur", 1);
    for (int pass = 0; pass < br; pass++) {
        float *tmp = malloc((size_t)CMN * CMN * 3 * sizeof(float));
        for (int y = 0; y < CMN; y++) for (int x = 0; x < CMN; x++) for (int c = 0; c < 3; c++) {
            int xm = x > 0 ? x - 1 : x, xp = x < CMN - 1 ? x + 1 : x;
            tmp[((size_t)y * CMN + x) * 3 + c] = 0.25f * CM[((size_t)y * CMN + xm) * 3 + c] + 0.5f * CM[((size_t)y * CMN + x) * 3 + c] + 0.25f * CM[((size_t)y * CMN + xp) * 3 + c]; }
        for (int y = 0; y < CMN; y++) for (int x = 0; x < CMN; x++) for (int c = 0; c < 3; c++) {
            int ym = y > 0 ? y - 1 : y, yp = y < CMN - 1 ? y + 1 : y;
            CM[((size_t)y * CMN + x) * 3 + c] = 0.25f * tmp[((size_t)ym * CMN + x) * 3 + c] + 0.5f * tmp[((size_t)y * CMN + x) * 3 + c] + 0.25f * tmp[((size_t)yp * CMN + x) * 3 + c]; }
        free(tmp);
    }
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage\n"); return 1; }
    for (int i = 6; i < argc; i++) { char *e = strchr(argv[i], '='); if (!e) continue; *e = 0; strncpy(pk[npar], argv[i], 31); pv[npar++] = atof(e + 1); }
    FILE *f = fopen(argv[1], "rb"); int32_t ns, nc; fread(&ns, 4, 1, f); fread(&nc, 4, 1, f);
    npr = ns + nc; pr = calloc(npr, sizeof(Pr));
    for (int i = 0; i < ns; i++) { double r[8]; fread(r, 8, 8, f); Pr *q = &pr[i]; q->kind = 0; q->a = v3(r[0], r[1], r[2]); q->r = r[3]; q->type = (int)r[4]; q->col = v3(r[5], r[6], r[7]);
        q->lo = sub(q->a, v3(q->r, q->r, q->r)); q->hi = add(q->a, v3(q->r, q->r, q->r)); }
    for (int i = 0; i < nc; i++) { double r[10]; fread(r, 8, 10, f); Pr *q = &pr[ns + i]; q->kind = 1; q->a = v3(r[0], r[1], r[2]); q->b = v3(r[3], r[4], r[5]); q->r = r[6]; q->col = v3(r[7], r[8], r[9]);
        q->lo = sub(v3(fmin(q->a.x, q->b.x), fmin(q->a.y, q->b.y), fmin(q->a.z, q->b.z)), v3(q->r, q->r, q->r));
        q->hi = add(v3(fmax(q->a.x, q->b.x), fmax(q->a.y, q->b.y), fmax(q->a.z, q->b.z)), v3(q->r, q->r, q->r)); }
    fclose(f);
    idx = malloc(npr * sizeof(int)); for (int i = 0; i < npr; i++) idx[i] = i; nodes = calloc(2 * npr + 8, sizeof(Node)); build(0, npr);
    int W = atoi(argv[2]), H = atoi(argv[3]), spp = atoi(argv[4]);
    IOR = P("ior", 1.52);
    double sel = P("sunel", 42) * M_PI / 180, saz = P("sunaz", 125) * M_PI / 180;
    SUN = v3(cos(sel) * cos(saz), cos(sel) * sin(saz), sin(sel)); SUNCOS = cos(P("sunrad", 1.6) * M_PI / 180);
    SUNC = v3(P("sr", 1.0), P("sg", 0.96), P("sb", 0.88)); ESUN = P("esun", 3.0);
    SKYZ = v3(P("zr", 0.62), P("zg", 0.70), P("zb", 0.95)); SKYH = v3(P("hr", 1.0), P("hg", 0.86), P("hb", 0.84)); SKYG = v3(0.9, 0.88, 0.86);
    WINX0 = P("wx0", -1.2); WINX1 = P("wx1", -0.5); WINY0 = P("wy0", 0.45); WINY1 = P("wy1", 0.95); WINB = P("winb", 4.0);
    PAPER = v3(P("pr", 0.97), P("pg", 0.955), P("pb", 0.94)); GRAIN = P("grain", 0.04);
    // camera: looks at (lx,ly,0) from distance dist, elevation cel, azimuth caz; vertical fov
    double cel = P("cel", 70) * M_PI / 180, caz = P("caz", -90) * M_PI / 180, dist = P("dist", 200), fov = P("fov", 30) * M_PI / 180;
    V look = v3(P("lx", 0), P("ly", 0), 0); V cam = add(look, mul(v3(cos(cel) * cos(caz), cos(cel) * sin(caz), sin(cel)), dist));
    V fw = nrm(sub(look, cam)), rt = nrm(cross(fw, v3(0, 0, 1))), up = cross(rt, fw);
    double th = tan(fov / 2); AP = P("ap", 0); FD = P("fd", dist);
    // optional printed-paper texture
    if (P("dots", 0) > 0) { FILE *g = fopen("dots.f32", "rb"); if (g) { int32_t hd[1]; fread(hd, 4, 1, g); DOTN = hd[0]; double hh[3]; fread(hh, 8, 3, g); DOTX0 = hh[0]; DOTY0 = hh[1]; DOTS_ = hh[2];
            DOTS = malloc((size_t)DOTN * DOTN * 3 * 4); fread(DOTS, 4, (size_t)DOTN * DOTN * 3, g); fclose(g); } }
    // photon map over the bead bounding box (+ margin)
    V lo = nodes[0].lo, hi = nodes[0].hi; double mg = P("cmarg", 30);
    if (P("nph", 2e7) > 0) photons(lo.x - mg, lo.y - mg, hi.x + mg, hi.y + mg, P("nph", 2e7));
    float *img = malloc((size_t)W * H * 3 * sizeof(float));
    int ya = (int)P("ya", 0), yb = (int)P("yb", H);
    #pragma omp parallel for schedule(dynamic, 1)
    for (int y = ya; y < yb; y++) { R rg = {0x9e3779b97f4a7c15ull ^ (uint64_t)(y + 1) * 0xbf58476d1ce4e5b9ull};
        for (int x = 0; x < W; x++) { V acc = v3(0, 0, 0);
            for (int s = 0; s < spp; s++) {
                double sx = (2 * (x + rnd(&rg)) / W - 1) * th * W / H, sy = (1 - 2 * (y + rnd(&rg)) / H) * th;
                V d = nrm(add(fw, add(mul(rt, sx), mul(up, sy))));
                V org = cam;
                if (AP > 0) { double fd = FD / dot(d, fw); V fp = add(cam, mul(d, fd)); double rr = AP * sqrt(rnd(&rg)), ph = 2 * M_PI * rnd(&rg);
                    org = add(cam, add(mul(rt, rr * cos(ph)), mul(up, rr * sin(ph)))); d = nrm(sub(fp, org)); }
                V c = radiance(org, d, &rg); double m = fmax(c.x, fmax(c.y, c.z)); if (m > 30) c = mul(c, 30 / m);
                acc = add(acc, c); }
            acc = mul(acc, 1.0 / spp); size_t k = ((size_t)y * W + x) * 3; img[k] = acc.x; img[k + 1] = acc.y; img[k + 2] = acc.z; } }
    FILE *o = fopen(argv[5], "wb"); fwrite(img + (size_t)ya * W * 3, 4, (size_t)(yb - ya) * W * 3, o); fclose(o);
    return 0;
}
