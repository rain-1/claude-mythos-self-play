// rast.c — additive anti-aliased segment rasteriser (bilinear splats along each segment).
// build: gcc -O3 -march=native -shared -fPIC -o librast.so rast.c
#include <math.h>
#include <stdint.h>

void raster_segs(const double *x0, const double *y0, const double *x1, const double *y1,
                 const double *w, int64_t n, int W, int H, double step, float *acc)
{
    for (int64_t i = 0; i < n; i++) {
        double dx = x1[i] - x0[i], dy = y1[i] - y0[i];
        double L = sqrt(dx * dx + dy * dy);
        int64_t ns = (int64_t)ceil(L / step); if (ns < 2) ns = 2;
        double wp = w[i] / (double)ns;
        for (int64_t k = 0; k < ns; k++) {
            double u = (k + 0.5) / (double)ns;
            double px = x0[i] + u * dx, py = y0[i] + u * dy;
            double fx = floor(px), fy = floor(py);
            int ix = (int)fx, iy = (int)fy;
            double ax = px - fx, ay = py - fy;
            if (ix < -1 || ix >= W || iy < -1 || iy >= H) continue;
            if (ix >= 0 && iy >= 0)           acc[(int64_t)iy * W + ix] += (float)(wp * (1 - ax) * (1 - ay));
            if (ix + 1 < W && iy >= 0)        acc[(int64_t)iy * W + ix + 1] += (float)(wp * ax * (1 - ay));
            if (ix >= 0 && iy + 1 < H)        acc[(int64_t)(iy + 1) * W + ix] += (float)(wp * (1 - ax) * ay);
            if (ix + 1 < W && iy + 1 < H)     acc[(int64_t)(iy + 1) * W + ix + 1] += (float)(wp * ax * ay);
        }
    }
}
