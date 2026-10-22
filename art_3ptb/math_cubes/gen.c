/* General meet-in-the-middle search: n = sum_{i=1}^6 (A_i x + B_i)^3, A_i != 0,
 * all |A_i|,|B_i| <= H.  Split 3+3; triple T has key K=(sum A^3, sum A^2 B, sum A B^2)
 * and value g = sum B^3.  Since the list is closed under negation, n = g(T) - g(T')
 * with key(T)=key(T') (T' gets negated).  Only keys K >= 0 lexicographically are stored.
 * usage: gen H N  -> prints "n A1 B1 ... A6 B6" for every |n|<=N found (one rep each).
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

typedef struct { uint64_t kg; uint32_t idx; } T;
static int cmpT(const void *a, const void *b) {
    uint64_t x = ((const T *)a)->kg, y = ((const T *)b)->kg;
    return x < y ? -1 : x > y;
}
int LA[2000], LB[2000], L;

int main(int argc, char **argv) {
    int H = atoi(argv[1]), N = atoi(argv[2]);
    L = 0;
    for (int a = -H; a <= H; a++) if (a) for (int b = -H; b <= H; b++) { LA[L] = a; LB[L] = b; L++; }
    long cap = (long)L * (L + 1) * (L + 2) / 6 / 2 + 1000;
    T *arr = malloc(sizeof(T) * cap);
    long m = 0;
    const int OFF = 32768;
    for (int i = 0; i < L; i++) for (int j = i; j < L; j++) for (int k = j; k < L; k++) {
        long a1 = LA[i], b1 = LB[i], a2 = LA[j], b2 = LB[j], a3 = LA[k], b3 = LB[k];
        long k1 = a1*a1*a1 + a2*a2*a2 + a3*a3*a3;
        long k2 = a1*a1*b1 + a2*a2*b2 + a3*a3*b3;
        long k3 = a1*b1*b1 + a2*b2*b2 + a3*b3*b3;
        long g = b1*b1*b1 + b2*b2*b2 + b3*b3*b3;
        if (k1 < 0) continue;
        if (k1 == 0 && k2 < 0) continue;
        if (k1 == 0 && k2 == 0 && k3 < 0) continue;
        uint64_t kg = ((uint64_t)(k1 + OFF) << 48) | ((uint64_t)(k2 + OFF) << 32) |
                      ((uint64_t)(k3 + OFF) << 16) | (uint64_t)(g + OFF);
        if (m >= cap) { fprintf(stderr, "cap\n"); return 1; }
        arr[m].kg = kg; arr[m].idx = (uint32_t)((i * L + j) * L + k); m++;
    }
    qsort(arr, m, sizeof(T), cmpT);
    char *found = calloc(2 * N + 1, 1);
    uint32_t *ra = malloc(sizeof(uint32_t) * (2 * N + 1)), *rb = malloc(sizeof(uint32_t) * (2 * N + 1));
    long s = 0;
    while (s < m) {
        long e = s; uint64_t key = arr[s].kg >> 16;
        while (e < m && (arr[e].kg >> 16) == key) e++;
        /* distinct g within [s,e) sorted ascending */
        for (long p = s; p < e; p++) {
            if (p > s && arr[p].kg == arr[p - 1].kg) continue;
            long gp = (long)(arr[p].kg & 0xffff) - OFF;
            for (long q = p + 1; q < e; q++) {
                long gq = (long)(arr[q].kg & 0xffff) - OFF;
                long n = gq - gp;
                if (n == 0) continue;
                if (n > N) break;
                if (!found[n + N]) { found[n + N] = 1; ra[n + N] = arr[q].idx; rb[n + N] = arr[p].idx; }
                if (!found[-n + N]) { found[-n + N] = 1; ra[-n + N] = arr[p].idx; rb[-n + N] = arr[q].idx; }
            }
        }
        s = e;
    }
    for (int n = -N; n <= N; n++) if (found[n + N]) {
        uint32_t x = ra[n + N], y = rb[n + N];
        int t[3] = { x / (L * L), (x / L) % L, x % L }, u[3] = { y / (L * L), (y / L) % L, y % L };
        printf("%d", n);
        for (int c = 0; c < 3; c++) printf(" %d %d", LA[t[c]], LB[t[c]]);
        for (int c = 0; c < 3; c++) printf(" %d %d", -LA[u[c]], -LB[u[c]]);
        printf("\n");
    }
    return 0;
}
