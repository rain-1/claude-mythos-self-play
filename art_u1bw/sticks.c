// studio.c — a small photo-studio path tracer: glass, brass and candy on a paper cyclorama,
// lit by a glowing lamp sphere (the orrery's sun) and a big soft key light.
//
// The backdrop is a seamless paper sweep (floor z = 0 for y < Y0, a concave quarter cylinder of radius RC,
// then a wall y = Y0 + RC). Lamp light that passes through glass is PHOTON-MAPPED onto the sweep in its own
// (x, u) chart (u = arc length along the sweep profile), so every glass planet throws a focused coloured
// spot of lamp light onto the paper. Direct lamp + key light by next-event estimation; glass counts as
// opaque for the lamp on the paper (the photon map carries that light) and as tinted elsewhere.
// OpenMP over rows.
//
// build: gcc -O3 -march=native -fopenmp studio.c -o studio -lm
// usage: ./studio scene.bin W H spp out.f32 [key=val ...]
//   scene.bin: int32 ns, int32 nc; ns rows float64 [x y z r mat R G B rough]; nc rows float64 [ax ay az bx by bz r mat R G B rough]
//   mat 0 glass (RGB = absorption per unit radius), 1 candy (albedo, clear coat), 2 metal (reflectance, rough),
//   3 emitter (radiance; the first one is the lamp), 4 matte (albedo)
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

static char pk[64][32]; static double pv[64]; static int npar = 0;
static double P(const char *k, double d) { for (int i = npar - 1; i >= 0; i--) if (!strcmp(pk[i], k)) return pv[i]; return d; }

typedef struct { uint64_t s; } R;
static inline double rnd(R *r) { r->s ^= r->s << 13; r->s ^= r->s >> 7; r->s ^= r->s << 17; return (r->s >> 11) * (1.0 / 9007199254740992.0); }

typedef struct { int kind, mat; V a, b; double r, rough; V col; V lo, hi; } Pr;
typedef struct { V lo, hi; int left, right, start, count; } Node;
static Pr *pr; static int npr; static Node *nodes; static int nn = 0; static int *idx;
static int ax_g;
static double cen(int i, int a) { V c = mul(add(pr[i].lo, pr[i].hi), 0.5); return a == 0 ? c.x : a == 1 ? c.y : c.z; }
static int cmpc(const void *a, const void *b) { double x = cen(*(int *)a, ax_g), y = cen(*(int *)b, ax_g); return (x > y) - (x < y); }
static int build(int s, int e) {
    int id = nn++; Node *n = &nodes[id]; n->lo = v3(1e30, 1e30, 1e30); n->hi = v3(-1e30, -1e30, -1e30);
    for (int i = s; i < e; i++) { Pr *q = &pr[idx[i]];
        n->lo = v3(fmin(n->lo.x, q->lo.x), fmin(n->lo.y, q->lo.y), fmin(n->lo.z, q->lo.z));
        n->hi = v3(fmax(n->hi.x, q->hi.x), fmax(n->hi.y, q->hi.y), fmax(n->hi.z, q->hi.z)); }
    if (e - s <= 4) { n->left = n->right = -1; n->start = s; n->count = e - s; return id; }
    V ext = sub(n->hi, n->lo); ax_g = ext.x > ext.y ? (ext.x > ext.z ? 0 : 2) : (ext.y > ext.z ? 1 : 2);
    qsort(idx + s, e - s, sizeof(int), cmpc); int m = (s + e) / 2;
    int l = build(s, m), r = build(m, e); nodes[id].left = l; nodes[id].right = r; nodes[id].count = 0; return id;
}
static inline int box(V o, V inv, V lo, V hi, double tmax) {
    double t0 = 0, t1 = tmax;
    double a = (lo.x - o.x) * inv.x, b = (hi.x - o.x) * inv.x; if (a > b) { double t = a; a = b; b = t; } t0 = fmax(t0, a); t1 = fmin(t1, b);
    a = (lo.y - o.y) * inv.y; b = (hi.y - o.y) * inv.y; if (a > b) { double t = a; a = b; b = t; } t0 = fmax(t0, a); t1 = fmin(t1, b);
    a = (lo.z - o.z) * inv.z; b = (hi.z - o.z) * inv.z; if (a > b) { double t = a; a = b; b = t; } t0 = fmax(t0, a); t1 = fmin(t1, b);
    return t0 <= t1;
}
static inline double isph(V o, V d, V c, double r) {
    V oc = sub(o, c); double b = dot(oc, d), cc = dot(oc, oc) - r * r, D = b * b - cc; if (D < 0) return 1e30;
    double s = sqrt(D), t = -b - s; if (t > 1e-7) return t; t = -b + s; return t > 1e-7 ? t : 1e30;
}
// capsule = convex body: entry/exit interval [*t0,*t1] along the ray (may be negative); returns 0 if missed
static inline int capint(V o, V d, V a, V b, double r, double *t0, double *t1) {
    V ba = sub(b, a), oa = sub(o, a); double baba = dot(ba, ba), bard = dot(ba, d), baoa = dot(ba, oa), rdoa = dot(d, oa), oaoa = dot(oa, oa);
    double A = baba - bard * bard, B = baba * rdoa - baoa * bard, C = baba * oaoa - baoa * baoa - r * r * baba, h = B * B - A * C;
    double lo = 1e30, hi = -1e30;
    if (h >= 0 && A > 1e-12) { double s = sqrt(h);
        for (int k = 0; k < 2; k++) { double t = (-B + (k ? s : -s)) / A, y = baoa + t * bard;
            if (y > 0 && y < baba) { lo = fmin(lo, t); hi = fmax(hi, t); } } }
    for (int e = 0; e < 2; e++) { V c = e ? b : a; V oc = sub(o, c); double bb = dot(oc, d), cc = dot(oc, oc) - r * r, D = bb * bb - cc;
        if (D < 0) continue; double s = sqrt(D);
        for (int k = 0; k < 2; k++) { double t = -bb + (k ? s : -s); V p = add(oc, mul(d, t)); double y = dot(add(p, sub(c, a)), ba);
            if ((e == 0 && y <= 0) || (e == 1 && y >= baba)) { lo = fmin(lo, t); hi = fmax(hi, t); } } }
    if (hi < lo) return 0; *t0 = lo; *t1 = hi; return 1;
}
static inline double icap(V o, V d, V a, V b, double r, V *nout) {
    double t0, t1; if (!capint(o, d, a, b, r, &t0, &t1)) return 1e30;
    double t = t0 > 1e-7 ? t0 : (t1 > 1e-7 ? t1 : 1e30); if (t > 1e29) return t;
    V p = add(o, mul(d, t)), ba = sub(b, a); double y = dot(sub(p, a), ba) / dot(ba, ba); y = fmin(1, fmax(0, y));
    *nout = nrm(sub(p, add(a, mul(ba, y)))); return t;
}
static int hit(V o, V d, double *tb, V *nout) {
    V inv = v3(1 / d.x, 1 / d.y, 1 / d.z); int st[128], sp = 0, who = -1; st[sp++] = 0;
    while (sp) { Node *n = &nodes[st[--sp]];
        if (!box(o, inv, n->lo, n->hi, *tb)) continue;
        if (n->left < 0) { for (int k = 0; k < n->count; k++) { int i = idx[n->start + k]; Pr *q = &pr[i];
                if (q->kind == 0) { double t = isph(o, d, q->a, q->r);
                    if (t < *tb) { *tb = t; who = i; *nout = nrm(sub(add(o, mul(d, t)), q->a)); } }
                else { V nn2; double t = icap(o, d, q->a, q->b, q->r, &nn2); if (t < *tb) { *tb = t; who = i; *nout = nn2; } } } }
        else { st[sp++] = n->left; st[sp++] = n->right; } }
    return who;
}
// transmittance along a segment of length tmax; glass tinted when glassT, else opaque; emitters ignored
static V shadowT(V o, V d, double tmax, int glassT) {
    V T = v3(1, 1, 1); V inv = v3(1 / d.x, 1 / d.y, 1 / d.z); int st[128], sp = 0; st[sp++] = 0;
    while (sp) { Node *n = &nodes[st[--sp]];
        if (!box(o, inv, n->lo, n->hi, tmax)) continue;
        if (n->left < 0) { for (int k = 0; k < n->count; k++) { Pr *q = &pr[idx[n->start + k]];
                if (q->mat == 3) continue;
                if (q->kind == 0) { V oc = sub(o, q->a); double b = dot(oc, d), c = dot(oc, oc) - q->r * q->r, D = b * b - c;
                    if (D <= 0) continue; double s = sqrt(D), t1 = -b - s, t2 = -b + s; if (t2 <= 1e-7 || t1 >= tmax) continue;
                    if (q->mat != 0 || !glassT) return v3(0, 0, 0);
                    double L = fmin(t2, tmax) - fmax(t1, 0); T = hm(T, mul(vexp(mul(q->col, -L / q->r)), 0.86)); }
                else { double t1, t2; if (!capint(o, d, q->a, q->b, q->r, &t1, &t2)) continue; if (t2 <= 1e-7 || t1 >= tmax) continue;
                    if (q->mat != 0 || !glassT) return v3(0, 0, 0);
                    double L = fmin(t2, tmax) - fmax(t1, 0); T = hm(T, mul(vexp(mul(q->col, -L / q->r)), 0.86)); } } }
        else { st[sp++] = n->left; st[sp++] = n->right; } }
    return T;
}

// ---------------- backdrop: paper sweep ----------------
static double Y0, RC, XW;   // sweep start, radius, half width (beyond it: open studio)
static int sweep(V o, V d, double *t, V *n, double *u) {   // returns 1 if hit
    double best = 1e30; V bn = v3(0, 0, 1); double bu = 0;
    if (d.z < 0) { double tt = -o.z / d.z; V p = add(o, mul(d, tt)); if (tt > 1e-7 && p.y <= Y0) { best = tt; bn = v3(0, 0, 1); bu = p.y - Y0; } }
    if (d.y > 0) { double tt = (Y0 + RC - o.y) / d.y; V p = add(o, mul(d, tt)); if (tt > 1e-7 && tt < best && p.z >= RC) { best = tt; bn = v3(0, -1, 0); bu = RC * M_PI / 2 + p.z - RC; } }
    {   // cylinder (y - Y0)^2 + (z - RC)^2 = RC^2
        double oy = o.y - Y0, oz = o.z - RC; double A = d.y * d.y + d.z * d.z, B = oy * d.y + oz * d.z, C = oy * oy + oz * oz - RC * RC, D = B * B - A * C;
        if (D > 0 && A > 1e-12) { double s = sqrt(D);
            for (int k = 0; k < 2; k++) { double tt = (-B + (k ? s : -s)) / A; if (tt <= 1e-7 || tt >= best) continue;
                V p = add(o, mul(d, tt)); if (p.y >= Y0 && p.z <= RC) { best = tt; bn = nrm(v3(0, Y0 - p.y, RC - p.z)); bu = RC * atan2(p.y - Y0, RC - p.z); break; } } }
    }
    if (best > 1e29) return 0;
    V p = add(o, mul(d, best)); if (fabs(p.x) > XW) return 0;
    *t = best; *n = bn; *u = bu; return 1;
}

// ---------------- light ----------------
static V KEY, KEYC; static double KEYCOS, EKEY;   // soft key light (a big softbox as a direction disc)
static V AMBT, AMBB; static int KEYPH = 0;   // studio ambient (top / bottom)
static int LAMP = -1; static V LAMPP; static double LAMPR; static V LAMPL;
static V amb(V d) { double t = 0.5 + 0.5 * d.z; return add(mul(AMBB, 1 - t), mul(AMBT, t)); }
static void onb(V n, V *t, V *b) { V a = fabs(n.x) > 0.9 ? v3(0, 1, 0) : v3(1, 0, 0); *t = nrm(cross(a, n)); *b = cross(n, *t); }
static V cosdir(V n, R *rg) { double u = rnd(rg), v = rnd(rg), r = sqrt(u), ph = 2 * M_PI * v; V t, b; onb(n, &t, &b);
    return nrm(add(add(mul(t, r * cos(ph)), mul(b, r * sin(ph))), mul(n, sqrt(fmax(0, 1 - u))))); }
static V conedir(V axis, double cosmax, R *rg) { double u = rnd(rg), v = rnd(rg); double ct = 1 - u * (1 - cosmax), st = sqrt(fmax(0, 1 - ct * ct)), ph = 2 * M_PI * v; V t, b; onb(axis, &t, &b);
    return nrm(add(add(mul(t, st * cos(ph)), mul(b, st * sin(ph))), mul(axis, ct))); }

// ---------------- caustic map on the sweep chart (x, u) ----------------
static float *CM; static int CMW, CMH; static double CMX0, CMU0, CMS;
static V caus(double x, double u) {
    if (!CM) return v3(0, 0, 0);
    double gx = (x - CMX0) / CMS - 0.5, gy = (u - CMU0) / CMS - 0.5; int ix = (int)floor(gx), iy = (int)floor(gy);
    if (ix < 0 || iy < 0 || ix >= CMW - 1 || iy >= CMH - 1) return v3(0, 0, 0);
    double fx = gx - ix, fy = gy - iy; double r[3];
    for (int c = 0; c < 3; c++) {
        double a = CM[((size_t)iy * CMW + ix) * 3 + c], b = CM[((size_t)iy * CMW + ix + 1) * 3 + c];
        double e = CM[((size_t)(iy + 1) * CMW + ix) * 3 + c], f = CM[((size_t)(iy + 1) * CMW + ix + 1) * 3 + c];
        r[c] = (a * (1 - fx) + b * fx) * (1 - fy) + (e * (1 - fx) + f * fx) * fy; }
    return v3(r[0], r[1], r[2]);
}
static double IOR;
static inline double fresnel(double cosi, double eta) {
    double sint2 = eta * eta * (1 - cosi * cosi); if (sint2 >= 1) return 1;
    double cost = sqrt(1 - sint2);
    double rs = (eta * cosi - cost) / (eta * cosi + cost), rp = (cosi - eta * cost) / (cosi + eta * cost);
    return 0.5 * (rs * rs + rp * rp);
}
// paper albedo: cool white with a pastel wash rising up the wall
static V PAPF, PAPW; static double GRAIN;
static double hash2(int x, int y) { uint64_t h = (uint64_t)(x * 73856093) ^ (uint64_t)(y * 19349663) ^ 0x9e3779b97f4a7c15ull; h ^= h >> 33; h *= 0xff51afd7ed558ccdull; h ^= h >> 33; return (h & 0xffffff) / 16777216.0; }
static double vnoise(double x, double y) { int ix = floor(x), iy = floor(y); double fx = x - ix, fy = y - iy; fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy);
    return (hash2(ix, iy) * (1 - fx) + hash2(ix + 1, iy) * fx) * (1 - fy) + (hash2(ix, iy + 1) * (1 - fx) + hash2(ix + 1, iy + 1) * fx) * fy; }
static float *TEX; static int TW, TH; static double TX0, TU0, TS;   // optional printed texture in the (x,u) chart (multiplies albedo)
static V paper(double x, double u) {
    double g = 1 + GRAIN * (vnoise(x * 2.3, u * 2.3) - 0.5) + 0.5 * GRAIN * (vnoise(x * 9, u * 9) - 0.5);
    double w = fmin(1, fmax(0, (u - P("wash0", 0)) / P("washL", 60))); w = w * w * (3 - 2 * w);
    V a = mul(add(mul(PAPF, 1 - w), mul(PAPW, w)), g);
    if (TEX) { int ix = (int)((x - TX0) / TS), iy = (int)((u - TU0) / TS);
        if (ix >= 0 && iy >= 0 && ix < TW && iy < TH) { size_t k = ((size_t)iy * TW + ix) * 3; a = hm(a, v3(TEX[k], TEX[k + 1], TEX[k + 2])); } }
    return a;
}
// direct light at a diffuse point. onpaper = 1: lamp shadows of glass are opaque (caustic map adds the light)
static V direct(V p, V n, int onpaper, double u, double xpos, R *rg) {
    V L = v3(0, 0, 0); V o = add(p, mul(n, 1e-6));
    // key softbox
    V kd = conedir(KEY, KEYCOS, rg); double c = dot(kd, n);
    if (c > 0) L = add(L, mul(hm(KEYC, shadowT(o, kd, 1e30, !(onpaper && KEYPH))), EKEY * c));
    // lamp sphere (sample the visible cone)
    if (LAMP >= 0) { V tl = sub(LAMPP, o); double dl2 = dot(tl, tl), dl = sqrt(dl2);
        if (dl > LAMPR * 1.001) { double cmax = sqrt(fmax(0, 1 - LAMPR * LAMPR / dl2)); V ld = conedir(mul(tl, 1 / dl), cmax, rg); double cl = dot(ld, n);
            if (cl > 0) { double omega = 2 * M_PI * (1 - cmax); double tl2 = dl - LAMPR;
                L = add(L, mul(hm(LAMPL, shadowT(o, ld, tl2, !onpaper)), omega * cl / M_PI)); } } }
    // ambient (one occluded cosine sample)
    V sd = cosdir(n, rg); V T = shadowT(o, sd, 1e30, 1); L = add(L, hm(T, amb(sd)));
    if (onpaper) L = add(L, mul(caus(xpos, u), 1.0 / M_PI));
    return L;
}
static V radiance(V o, V d, R *rg) {
    V T = v3(1, 1, 1), acc = v3(0, 0, 0); int inside = -1, spec = 1;
    for (int depth = 0; depth < 48; depth++) {
        double tb = 1e30; V n; int who = hit(o, d, &tb, &n);
        double ts, us; V ns; int hs = inside < 0 ? sweep(o, d, &ts, &ns, &us) : 0;
        if (hs && ts < tb) { V p = add(o, mul(d, ts)); V alb = paper(p.x, us);
            acc = add(acc, hm(T, hm(alb, direct(p, ns, 1, us, p.x, rg)))); return acc; }
        if (who < 0) { V c = amb(d); if (spec && dot(d, KEY) > KEYCOS) c = add(c, mul(KEYC, P("keyvis", 3.0))); return add(acc, hm(T, c)); }
        Pr *q = &pr[who]; V p = add(o, mul(d, tb));
        if (q->mat == 3) { return add(acc, hm(T, q->col)); }
        if (q->mat == 4) { return add(acc, hm(T, hm(q->col, direct(p, n, 0, 0, 0, rg)))); }
        if (q->mat == 1) {   // candy: clear coat + diffuse
            double ci = fabs(dot(d, n)); double F = 0.04 + 0.96 * pow(1 - ci, 5);
            if (rnd(rg) < F) { d = nrm(sub(d, mul(n, 2 * dot(d, n)))); o = add(p, mul(n, 1e-7)); continue; }
            return add(acc, hm(T, hm(q->col, direct(p, n, 0, 0, 0, rg)))); }
        if (q->mat == 2) {   // metal: tinted Schlick reflection with a fuzzy lobe
            double ci = fabs(dot(d, n)); V F0 = q->col; double f5 = pow(1 - ci, 5);
            V F = add(F0, mul(sub(v3(1, 1, 1), F0), f5)); T = hm(T, F);
            V rd = nrm(sub(d, mul(n, 2 * dot(d, n))));
            if (q->rough > 0) { V t, b; onb(rd, &t, &b); double rr = q->rough * sqrt(rnd(rg)), ph = 2 * M_PI * rnd(rg); rd = nrm(add(rd, add(mul(t, rr * cos(ph)), mul(b, rr * sin(ph))))); if (dot(rd, n) < 0) rd = nrm(sub(rd, mul(n, 2 * dot(rd, n)))); }
            // a little lamp glint for metal (lamp is small and bright: add explicit specular via NEE-ish lobe)
            d = rd; o = add(p, mul(n, 1e-7)); continue; }
        // glass
        int entering = dot(d, n) < 0; V nn2 = entering ? n : mul(n, -1);
        if (!entering) T = hm(T, vexp(mul(q->col, -tb / q->r)));
        double eta = entering ? 1.0 / IOR : IOR; double ci = -dot(d, nn2); double F = fresnel(ci, eta);
        if (rnd(rg) < F) { d = nrm(add(d, mul(nn2, 2 * ci))); o = add(p, mul(nn2, 1e-7)); inside = entering ? -1 : who; }
        else { double k = 1 - eta * eta * (1 - ci * ci); d = nrm(add(mul(d, eta), mul(nn2, eta * ci - sqrt(k)))); o = sub(p, mul(nn2, 1e-7)); inside = entering ? who : -1; }
        if (depth > 6) { double m = fmax(T.x, fmax(T.y, T.z)); if (m < 0.05) { if (rnd(rg) > m * 10) return acc; T = mul(T, 1 / (m * 10)); } }
    }
    return add(acc, hm(T, mul(amb(d), P("tirfill", 1.0))));
}
// ---------------- photon pass: lamp → glass → sweep ----------------
static void alloc_cm(void) {
    double x0 = P("cx0", -60), x1 = P("cx1", 60), u0 = P("cu0", -60), u1 = P("cu1", 80);
    CMS = P("cms", 0.05); CMW = (int)((x1 - x0) / CMS) + 1; CMH = (int)((u1 - u0) / CMS) + 1; CMX0 = x0; CMU0 = u0;
    CM = calloc((size_t)CMW * CMH * 3, sizeof(float));
}
static void photons(double nph) {
    double cell = CMS * CMS;
    // intensity of a lamp sphere of radiance L, radius r: I = L * pi r^2 per steradian
    V I = mul(LAMPL, M_PI * LAMPR * LAMPR);
    int ng = 0; for (int i = 0; i < npr; i++) if (pr[i].kind == 0 && pr[i].mat == 0) ng++;
    fprintf(stderr, "photons: %d glass spheres, grid %d x %d\n", ng, CMW, CMH);
    long per = (long)(nph / (ng > 0 ? ng : 1));
    for (int gi = 0; gi < npr; gi++) { Pr *g = &pr[gi]; if (g->kind != 0 || g->mat != 0) continue;
        V tg = sub(g->a, LAMPP); double dg = sqrt(dot(tg, tg)); if (dg <= g->r) continue;
        double cmax = sqrt(1 - g->r * g->r / (dg * dg)); double omega = 2 * M_PI * (1 - cmax); V ax = mul(tg, 1 / dg);
        V flux = mul(I, omega / per);
        #pragma omp parallel
        {
            float *loc = calloc((size_t)CMW * CMH * 3, sizeof(float));
            #pragma omp for schedule(static)
            for (long k = 0; k < per; k++) { R rg = {0x1234567ull + (uint64_t)k * 2654435761ull + (uint64_t)gi * 0x9e3779b97f4a7c15ull}; rnd(&rg);
                V d = conedir(ax, cmax, &rg);
                V o = add(LAMPP, mul(d, LAMPR * 1.001));
                // must hit this sphere first
                double tb = 1e30; V n; int who = hit(o, d, &tb, &n); if (who != gi) continue;
                V pw = flux; int bounced = 0;
                for (int depth = 0; depth < 16; depth++) {
                    if (depth > 0) { tb = 1e30; who = hit(o, d, &tb, &n); }
                    double ts, us; V ns; int hs = sweep(o, d, &ts, &ns, &us);
                    if (hs && ts < tb) { if (bounced) { V p = add(o, mul(d, ts)); int ix = (int)((p.x - CMX0) / CMS), iy = (int)((us - CMU0) / CMS);
                            if (ix >= 0 && iy >= 0 && ix < CMW && iy < CMH) { size_t kk = ((size_t)iy * CMW + ix) * 3; double cosf = fabs(dot(d, ns));
                                (void)cosf; loc[kk] += pw.x / cell; loc[kk + 1] += pw.y / cell; loc[kk + 2] += pw.z / cell; } }
                        break; }
                    if (who < 0) break;
                    Pr *q = &pr[who]; if (q->mat != 0) break;
                    V p = add(o, mul(d, tb));
                    int entering = dot(d, n) < 0; V nn2 = entering ? n : mul(n, -1);
                    if (!entering) pw = hm(pw, vexp(mul(q->col, -tb / q->r)));
                    double eta = entering ? 1.0 / IOR : IOR; double ci = -dot(d, nn2); double F = fresnel(ci, eta);
                    if (rnd(&rg) < F) { d = nrm(add(d, mul(nn2, 2 * ci))); o = add(p, mul(nn2, 1e-7)); }
                    else { double kk = 1 - eta * eta * (1 - ci * ci); d = nrm(add(mul(d, eta), mul(nn2, eta * ci - sqrt(kk)))); o = sub(p, mul(nn2, 1e-7)); }
                    bounced = 1;
                } }
            #pragma omp critical
            { for (size_t k = 0; k < (size_t)CMW * CMH * 3; k++) CM[k] += loc[k]; }
            free(loc);
        } }
}
static void blur_cm(void) {
    int br = (int)P("cblur", 2);
    for (int pass = 0; pass < br; pass++) {
        float *tmp = malloc((size_t)CMW * CMH * 3 * sizeof(float));
        for (int y = 0; y < CMH; y++) for (int x = 0; x < CMW; x++) for (int c = 0; c < 3; c++) {
            int xm = x > 0 ? x - 1 : x, xp = x < CMW - 1 ? x + 1 : x;
            tmp[((size_t)y * CMW + x) * 3 + c] = 0.25f * CM[((size_t)y * CMW + xm) * 3 + c] + 0.5f * CM[((size_t)y * CMW + x) * 3 + c] + 0.25f * CM[((size_t)y * CMW + xp) * 3 + c]; }
        for (int y = 0; y < CMH; y++) for (int x = 0; x < CMW; x++) for (int c = 0; c < 3; c++) {
            int ym = y > 0 ? y - 1 : y, yp = y < CMH - 1 ? y + 1 : y;
            CM[((size_t)y * CMW + x) * 3 + c] = 0.25f * tmp[((size_t)ym * CMW + x) * 3 + c] + 0.5f * tmp[((size_t)y * CMW + x) * 3 + c] + 0.25f * tmp[((size_t)yp * CMW + x) * 3 + c]; }
        free(tmp);
    }
}

// key light photons: a plane perpendicular to KEY over the glass bounding box
static void key_photons(double nph) {
    V lo = v3(1e30, 1e30, 1e30), hi = v3(-1e30, -1e30, -1e30); int ng = 0;
    for (int i = 0; i < npr; i++) if (pr[i].mat == 0) { ng++; lo = v3(fmin(lo.x, pr[i].lo.x), fmin(lo.y, pr[i].lo.y), fmin(lo.z, pr[i].lo.z)); hi = v3(fmax(hi.x, pr[i].hi.x), fmax(hi.y, pr[i].hi.y), fmax(hi.z, pr[i].hi.z)); }
    if (!ng) return;
    V t, b; onb(KEY, &t, &b); double umin = 1e30, umax = -1e30, vmin = 1e30, vmax = -1e30;
    for (int k = 0; k < 8; k++) { V c = v3(k & 1 ? hi.x : lo.x, k & 2 ? hi.y : lo.y, k & 4 ? hi.z : lo.z);
        double u = dot(c, t), v = dot(c, b); umin = fmin(umin, u); umax = fmax(umax, u); vmin = fmin(vmin, v); vmax = fmax(vmax, v); }
    double side = sqrt((umax - umin) * (vmax - vmin) / nph); int NU = (int)((umax - umin) / side) + 1, NV = (int)((vmax - vmin) / side) + 1;
    V flux = mul(KEYC, M_PI * EKEY * side * side); double cell = CMS * CMS;
    fprintf(stderr, "key photons %d x %d\n", NU, NV);
    #pragma omp parallel
    {
        float *loc = calloc((size_t)CMW * CMH * 3, sizeof(float));
        #pragma omp for schedule(dynamic, 4)
        for (int iv = 0; iv < NV; iv++) { R rg = {0x7654321ull + iv * 2654435761ull}; rnd(&rg);
            for (int iu = 0; iu < NU; iu++) {
                double u = umin + (iu + rnd(&rg)) * side, v = vmin + (iv + rnd(&rg)) * side;
                V d = mul(conedir(KEY, KEYCOS, &rg), -1); V o = add(add(mul(t, u), mul(b, v)), mul(KEY, 400));
                V pw = flux; int bounced = 0;
                for (int depth = 0; depth < 16; depth++) {
                    double tb = 1e30; V n; int who = hit(o, d, &tb, &n);
                    double ts, us; V ns; int hs = sweep(o, d, &ts, &ns, &us);
                    if (hs && ts < tb) { if (bounced) { V p = add(o, mul(d, ts)); int ix = (int)((p.x - CMX0) / CMS), iy = (int)((us - CMU0) / CMS);
                            if (ix >= 0 && iy >= 0 && ix < CMW && iy < CMH) { size_t kk = ((size_t)iy * CMW + ix) * 3;
                                loc[kk] += pw.x / cell; loc[kk + 1] += pw.y / cell; loc[kk + 2] += pw.z / cell; } }
                        break; }
                    if (who < 0) break;
                    Pr *q = &pr[who]; if (q->mat != 0) break;
                    V p = add(o, mul(d, tb));
                    int entering = dot(d, n) < 0; V nn2 = entering ? n : mul(n, -1);
                    if (!entering) pw = hm(pw, vexp(mul(q->col, -tb / q->r)));
                    double eta = entering ? 1.0 / IOR : IOR; double ci = -dot(d, nn2); double F = fresnel(ci, eta);
                    if (rnd(&rg) < F) { d = nrm(add(d, mul(nn2, 2 * ci))); o = add(p, mul(nn2, 1e-7)); }
                    else { double kk = 1 - eta * eta * (1 - ci * ci); d = nrm(add(mul(d, eta), mul(nn2, eta * ci - sqrt(kk)))); o = sub(p, mul(nn2, 1e-7)); }
                    bounced = 1;
                } } }
        #pragma omp critical
        { for (size_t k = 0; k < (size_t)CMW * CMH * 3; k++) CM[k] += loc[k]; }
        free(loc);
    }
}
int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage\n"); return 1; }
    for (int i = 6; i < argc; i++) { char *e = strchr(argv[i], '='); if (!e) continue; *e = 0; strncpy(pk[npar], argv[i], 31); pv[npar++] = atof(e + 1); }
    FILE *f = fopen(argv[1], "rb"); int32_t ns, nc; if (fread(&ns, 4, 1, f) != 1 || fread(&nc, 4, 1, f) != 1) return 1;
    npr = ns + nc; pr = calloc(npr, sizeof(Pr));
    for (int i = 0; i < ns; i++) { double r[9]; if (fread(r, 8, 9, f) != 9) return 1; Pr *q = &pr[i]; q->kind = 0; q->a = v3(r[0], r[1], r[2]); q->r = r[3]; q->mat = (int)r[4]; q->col = v3(r[5], r[6], r[7]); q->rough = r[8];
        q->lo = sub(q->a, v3(q->r, q->r, q->r)); q->hi = add(q->a, v3(q->r, q->r, q->r));
        if (q->mat == 3 && LAMP < 0) { LAMP = i; LAMPP = q->a; LAMPR = q->r; LAMPL = q->col; } }
    for (int i = 0; i < nc; i++) { double r[12]; if (fread(r, 8, 12, f) != 12) return 1; Pr *q = &pr[ns + i]; q->kind = 1; q->a = v3(r[0], r[1], r[2]); q->b = v3(r[3], r[4], r[5]); q->r = r[6]; q->mat = (int)r[7]; q->col = v3(r[8], r[9], r[10]); q->rough = r[11];
        q->lo = sub(v3(fmin(q->a.x, q->b.x), fmin(q->a.y, q->b.y), fmin(q->a.z, q->b.z)), v3(q->r, q->r, q->r));
        q->hi = add(v3(fmax(q->a.x, q->b.x), fmax(q->a.y, q->b.y), fmax(q->a.z, q->b.z)), v3(q->r, q->r, q->r)); }
    fclose(f);
    idx = malloc(npr * sizeof(int)); for (int i = 0; i < npr; i++) idx[i] = i; nodes = calloc(2 * npr + 8, sizeof(Node)); build(0, npr);
    int W = atoi(argv[2]), H = atoi(argv[3]), spp = atoi(argv[4]);
    IOR = P("ior", 1.5);
    Y0 = P("y0", 30); RC = P("rc", 25); XW = P("xw", 1e9);
    double kel = P("kel", 50) * M_PI / 180, kaz = P("kaz", 220) * M_PI / 180;
    KEY = v3(cos(kel) * cos(kaz), cos(kel) * sin(kaz), sin(kel)); KEYCOS = cos(P("krad", 14) * M_PI / 180);
    KEYC = v3(P("kr", 1.0), P("kg", 0.97), P("kb", 0.93)); EKEY = P("ekey", 1.0);
    AMBT = v3(P("atr", 0.62), P("atg", 0.62), P("atb", 0.70)); AMBB = v3(P("abr", 0.45), P("abg", 0.42), P("abb", 0.46));
    PAPF = v3(P("pfr", 0.97), P("pfg", 0.96), P("pfb", 0.955)); PAPW = v3(P("pwr", 0.95), P("pwg", 0.90), P("pwb", 0.96)); GRAIN = P("grain", 0.03);
    double cel = P("cel", 25) * M_PI / 180, caz = P("caz", -90) * M_PI / 180, dist = P("dist", 150), fov = P("fov", 30) * M_PI / 180;
    V look = v3(P("lx", 0), P("ly", 0), P("lz", 10)); V cam = add(look, mul(v3(cos(cel) * cos(caz), cos(cel) * sin(caz), sin(cel)), dist));
    V fw = nrm(sub(look, cam)), rt = nrm(cross(fw, v3(0, 0, 1))), up = cross(rt, fw);
    double th = tan(fov / 2); double AP = P("ap", 0), FD = P("fd", dist);
    if (P("tex", 0) > 0) { FILE *g = fopen("tex.f32", "rb"); if (g) { int32_t hd[2]; if (fread(hd, 4, 2, g) == 2) { TW = hd[0]; TH = hd[1]; double hh[3]; if (fread(hh, 8, 3, g) == 3) { TX0 = hh[0]; TU0 = hh[1]; TS = hh[2];
                TEX = malloc((size_t)TW * TH * 3 * 4); if (fread(TEX, 4, (size_t)TW * TH * 3, g) != (size_t)TW * TH * 3) { free(TEX); TEX = 0; } } } fclose(g); } }
    alloc_cm();
    if (LAMP >= 0 && P("nph", 2e7) > 0) photons(P("nph", 2e7));
    KEYPH = P("kph", 0) > 0; if (KEYPH) key_photons(P("kph", 0));
    blur_cm();
    if (P("dumpcm", 0) > 0 && CM) { FILE *g = fopen("caustic.f32", "wb"); int32_t hd[2] = {CMW, CMH}; fwrite(hd, 4, 2, g); fwrite(CM, 4, (size_t)CMW * CMH * 3, g); fclose(g); }
    float *img = malloc((size_t)W * H * 3 * sizeof(float));
    int ya = (int)P("ya", 0), yb = (int)P("yb", H);
    #pragma omp parallel for schedule(dynamic, 1)
    for (int y = ya; y < yb; y++) { R rg = {0x9e3779b97f4a7c15ull ^ (uint64_t)(y + 1) * 0xbf58476d1ce4e5b9ull};
        for (int x = 0; x < W; x++) { V acc = v3(0, 0, 0);
            for (int s = 0; s < spp; s++) {
                double sx = (2 * (x + rnd(&rg)) / W - 1) * th * W / H, sy = (1 - 2 * (y + rnd(&rg)) / H) * th;
                V d = nrm(add(fw, add(mul(rt, sx), mul(up, sy)))); V org = cam;
                if (AP > 0) { double fd = FD / dot(d, fw); V fp = add(cam, mul(d, fd)); double rr = AP * sqrt(rnd(&rg)), ph = 2 * M_PI * rnd(&rg);
                    org = add(cam, add(mul(rt, rr * cos(ph)), mul(up, rr * sin(ph)))); d = nrm(sub(fp, org)); }
                V c = radiance(org, d, &rg); double m = fmax(c.x, fmax(c.y, c.z)); if (!(m < 1e30) || fmin(c.x, fmin(c.y, c.z)) < 0) c = v3(0, 0, 0); else if (m > 40) c = mul(c, 40 / m);
                acc = add(acc, c); }
            acc = mul(acc, 1.0 / spp); size_t k = ((size_t)y * W + x) * 3; img[k] = acc.x; img[k + 1] = acc.y; img[k + 2] = acc.z; } }
    FILE *o = fopen(argv[5], "wb"); fwrite(img + (size_t)ya * W * 3, 4, (size_t)(yb - ya) * W * 3, o); fclose(o);
    return 0;
}
