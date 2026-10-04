// bored.c — the "easily bored" binary sequence (MO 377105, OEIS): b_1 = 0, then b_n is the digit x minimising
// R(x) = (a, len) lexicographically, a = largest exponent of a suffix repetition v^a of b_1..b_{n-1}x,
// len = longest |v| attaining it.  One Z-function on the reversed word per candidate: O(n) per digit.
// usage: bored n  -> writes bored.bin (digits) and bored_R.bin (int32 a, len of the chosen digit; and of the rejected)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void R(const unsigned char *r, int m, int *Z, int *ea, int *el) {
    // r = reversed word of length m (r[0] = newest digit). Z-function; period p repetition length = Z[p] + p
    Z[0] = m; int l = 0, rr = 0; int A = 1, L = m;     // whole word as v^1: len m
    for (int i = 1; i < m; i++) {
        int z = 0;
        if (i < rr) { z = rr - i; if (Z[i - l] < z) z = Z[i - l]; }
        while (i + z < m && r[z] == r[i + z]) z++;
        Z[i] = z; if (i + z > rr) { l = i; rr = i + z; }
        int a = (z + i) / i;
        if (a > A || (a == A && i > L)) { A = a; L = i; }   // larger exponent wins; tie -> longest v
    }
    // for exponent 1 the longest v is the whole word (len m); for a>=2, L is the largest period with that exponent
    if (A == 1) L = m;
    *ea = A; *el = L;
}
int main(int argc, char **argv) {
    int n = atoi(argv[1]);
    unsigned char *b = malloc(n + 1), *r = malloc(n + 2);
    int *Z = malloc(sizeof(int) * (n + 2)), *out = malloc(sizeof(int) * 4 * (n + 1));
    // keep reversed word in r with r[0] free for the candidate: store word reversed at r[1..]
    for (int t = 0; t < n; t++) {
        int a0, l0, a1, l1;
        // reversed word: r[0] = candidate, r[1+i] = b[t-1-i]
        r[0] = 0; R(r, t + 1, Z, &a0, &l0);
        r[0] = 1; R(r, t + 1, Z, &a1, &l1);
        int x;
        if (t == 0) x = 0;
        else x = (a0 < a1 || (a0 == a1 && l0 < l1)) ? 0 : 1;
        b[t] = x;
        out[4 * t] = x ? a1 : a0; out[4 * t + 1] = x ? l1 : l0; out[4 * t + 2] = x ? a0 : a1; out[4 * t + 3] = x ? l0 : l1;
        memmove(r + 2, r + 1, t); r[1] = x;   // shift: O(n) anyway
    }
    FILE *f = fopen("bored.bin", "wb"); fwrite(b, 1, n, f); fclose(f);
    f = fopen("bored_R.bin", "wb"); fwrite(out, sizeof(int), 4 * n, f); fclose(f);
    for (int t = 0; t < 40 && t < n; t++) printf("%d", b[t]); printf("\n");
}
