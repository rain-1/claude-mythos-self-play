/* Search ternary identities  sum_{i=1}^6 (A_i x + B_i y + C_i z)^3 = alpha y^3 + 3 beta y^2 z,
 * A_i != 0, |A|,|B|,|C| <= h.  Meet in the middle on triples keyed by the 8 coefficients
 * (x^3, x^2y, x^2z, xy^2, xyz, xz^2, yz^2, z^3).  Prints (beta, alpha, forms) for |beta| <= BM.
 * Setting y=1, z=t: n = alpha + 3 beta t, all t in Z.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef struct { uint64_t k1, k2; int32_t al, be; uint32_t idx; } T;
static int cmpT(const void *a, const void *b) {
    const T *x = a, *y = b;
    if (x->k1 != y->k1) return x->k1 < y->k1 ? -1 : 1;
    if (x->k2 != y->k2) return x->k2 < y->k2 ? -1 : 1;
    if (x->be != y->be) return x->be < y->be ? -1 : 1;
    return (x->al > y->al) - (x->al < y->al);
}
int FA[2000], FB[2000], FC[2000], L;
int main(int argc, char **argv) {
    int h = atoi(argv[1]); int BM = atoi(argv[2]);
    for (int a = -h; a <= h; a++) if (a) for (int b = -h; b <= h; b++) for (int c = -h; c <= h; c++) { FA[L] = a; FB[L] = b; FC[L] = c; L++; }
    long cap = (long)L * (L + 1) * (L + 2) / 6 / 2 + 100000;
    T *arr = malloc(sizeof(T) * cap); long m = 0;
    for (int i = 0; i < L; i++) for (int j = i; j < L; j++) for (int k = j; k < L; k++) {
        int id[3] = {i, j, k}; long s[10] = {0};
        for (int q = 0; q < 3; q++) {
            long a = FA[id[q]], b = FB[id[q]], c = FC[id[q]];
            s[0] += a*a*a; s[1] += a*a*b; s[2] += a*a*c; s[3] += a*b*b; s[4] += a*b*c;
            s[5] += a*c*c; s[6] += b*c*c; s[7] += c*c*c; s[8] += b*b*b; s[9] += b*b*c;
        }
        int sg = 0; for (int q = 0; q < 8 && !sg; q++) if (s[q]) sg = s[q] > 0 ? 1 : -1;
        if (sg < 0) continue;
        T t;
        t.k1 = ((uint64_t)(s[0]+32768) << 48) | ((uint64_t)(s[1]+32768) << 32) | ((uint64_t)(s[2]+32768) << 16) | (uint64_t)(s[3]+32768);
        t.k2 = ((uint64_t)(s[4]+32768) << 48) | ((uint64_t)(s[5]+32768) << 32) | ((uint64_t)(s[6]+32768) << 16) | (uint64_t)(s[7]+32768);
        t.al = s[8]; t.be = s[9]; t.idx = (uint32_t)(((long)i * L + j) * L + k);
        if (m >= cap) { fprintf(stderr, "cap\n"); return 1; }
        arr[m++] = t;
    }
    fprintf(stderr, "triples %ld\n", m);
    qsort(arr, m, sizeof(T), cmpT);
    long out = 0;
    for (long s0 = 0; s0 < m;) {
        long e = s0; while (e < m && arr[e].k1 == arr[s0].k1 && arr[e].k2 == arr[s0].k2) e++;
        for (long p = s0; p < e; p++) {
            if (p > s0 && arr[p].be == arr[p-1].be && arr[p].al == arr[p-1].al) continue;
            for (long q = p + 1; q < e; q++) {
                if (arr[q].be == arr[q-1].be && arr[q].al == arr[q-1].al) continue;
                long be = (long)arr[q].be - arr[p].be;
                if (be == 0 || be > BM) continue;
                long al = (long)arr[q].al - arr[p].al;
                uint32_t x = arr[q].idx, y = arr[p].idx;
                int a3[3] = { x / (L*L), (x / L) % L, x % L }, b3[3] = { y / (L*L), (y / L) % L, y % L };
                printf("%ld %ld", be, al);
                for (int c = 0; c < 3; c++) printf("  %d %d %d", FA[a3[c]], FB[a3[c]], FC[a3[c]]);
                for (int c = 0; c < 3; c++) printf("  %d %d %d", -FA[b3[c]], -FB[b3[c]], -FC[b3[c]]);
                printf("\n"); out++;
            }
        }
        s0 = e;
    }
    fprintf(stderr, "identities %ld\n", out);
    return 0;
}
