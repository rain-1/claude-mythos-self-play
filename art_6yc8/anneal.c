// anneal.c — the most nearly balanced hangings of the divisors on a k-gondola wheel.
// Minimises |sum_j c_j zeta^j| over permutations (c_0 = n pinned) by simulated annealing
// with swap moves, many restarts; prints the best R distinct hangings found (gap, perm).
// usage: anneal restarts steps keep d_1 ... d_k
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <string.h>
static uint64_t S = 0x9E3779B97F4A7C15ULL;
static inline uint64_t rng(void){ S ^= S << 13; S ^= S >> 7; S ^= S << 17; return S; }
static inline double U(void){ return (rng() >> 11) * (1.0 / 9007199254740992.0); }
typedef struct { double gap; int p[256]; } Rec;
int k; double d[256], cx[256], cy[256];
Rec best[4096]; int nb = 0, keep;
void offer(double gap, int *p){
    // canonical under mirror j -> -j: compare p with reversed, keep lexicographically smaller
    int q[256]; q[0] = p[0]; for (int j = 1; j < k; j++) q[j] = p[k - j];
    int *c = p; for (int j = 1; j < k; j++){ if (q[j] < p[j]){ c = q; break; } if (q[j] > p[j]) break; }
    for (int i = 0; i < nb; i++) if (memcmp(best[i].p, c, sizeof(int)*k) == 0) return;
    if (nb < keep){ best[nb].gap = gap; memcpy(best[nb].p, c, sizeof(int)*k); nb++; }
    else {
        int w = 0; for (int i = 1; i < nb; i++) if (best[i].gap > best[w].gap) w = i;
        if (gap < best[w].gap){ best[w].gap = gap; memcpy(best[w].p, c, sizeof(int)*k); }
    }
}
int main(int argc, char **argv){
    int restarts = atoi(argv[1]); long steps = atol(argv[2]); keep = atoi(argv[3]);
    k = argc - 4; for (int i = 0; i < k; i++) d[i] = atof(argv[4 + i]);
    for (int j = 0; j < k; j++){ cx[j] = cos(2*M_PI*j/k); cy[j] = sin(2*M_PI*j/k); }
    double n = d[k-1];
    for (int r = 0; r < restarts; r++){
        int p[256]; p[0] = k - 1; for (int j = 1; j < k; j++) p[j] = j - 1;
        for (int j = k - 1; j > 1; j--){ int i = 1 + rng() % j; int t = p[i]; p[i] = p[j]; p[j] = t; }
        double X = 0, Y = 0; for (int j = 0; j < k; j++){ X += d[p[j]]*cx[j]; Y += d[p[j]]*cy[j]; }
        double T0 = n * 0.2, T1 = 1e-3;
        double cur = sqrt(X*X + Y*Y);
        for (long s = 0; s < steps; s++){
            double T = T0 * pow(T1 / T0, (double)s / steps);
            int i = 1 + rng() % (k - 1), j = 1 + rng() % (k - 1); if (i == j) continue;
            double da = d[p[i]] - d[p[j]];
            double nX = X + da*(cx[j] - cx[i]), nY = Y + da*(cy[j] - cy[i]);
            double nw = sqrt(nX*nX + nY*nY);
            if (nw < cur || U() < exp((cur - nw) / T)){
                int t = p[i]; p[i] = p[j]; p[j] = t; X = nX; Y = nY; cur = nw;
                if (cur < n * 0.02) offer(cur, p);
            }
        }
        // periodic exact re-sum to kill drift
        X = 0; Y = 0; for (int j = 0; j < k; j++){ X += d[p[j]]*cx[j]; Y += d[p[j]]*cy[j]; }
        offer(sqrt(X*X+Y*Y), p);
    }
    // sort
    for (int a = 0; a < nb; a++) for (int b = a + 1; b < nb; b++) if (best[b].gap < best[a].gap){ Rec t = best[a]; best[a] = best[b]; best[b] = t; }
    for (int a = 0; a < nb; a++){
        // recompute exactly
        double X = 0, Y = 0; for (int j = 0; j < k; j++){ X += d[best[a].p[j]]*cx[j]; Y += d[best[a].p[j]]*cy[j]; }
        printf("%.12g", sqrt(X*X+Y*Y));
        for (int j = 0; j < k; j++) printf(" %.0f", d[best[a].p[j]]);
        printf("\n");
    }
    return 0;
}
