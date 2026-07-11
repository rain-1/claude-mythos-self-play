/* Subtract-a-prime-divisor game (MO 2026-07): L(0)=L(1)=lose.
 * L(n) <=> every prime divisor p of n has L(n-p) false.
 * Sieve to N via SPF (linear sieve). Outputs:
 *   - losing.bits  : bitmap of losing positions (bit n set = loss)
 *   - wild.txt     : even losses not of form 2p, 4p, 2^k, with omega_odd
 *   - census printed
 * cc -O2 -o game game.c && ./game 536870912
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

int main(int argc, char **argv) {
    uint64_t N = argc > 1 ? strtoull(argv[1], 0, 10) : 536870912ULL; /* 2^29 */
    uint32_t *spf = malloc(N * 4);
    uint8_t  *L   = calloc(N, 1);
    if (!spf || !L) { fprintf(stderr, "alloc fail\n"); return 1; }

    /* linear sieve for smallest prime factor */
    uint32_t *primes = malloc((N / 10 + 1000) * 4);
    uint64_t np = 0;
    memset(spf, 0, N * 4);
    for (uint64_t i = 2; i < N; i++) {
        if (!spf[i]) { spf[i] = i; primes[np++] = i; }
        for (uint64_t j = 0; j < np && primes[j] <= spf[i] && i * primes[j] < N; j++)
            spf[i * primes[j]] = primes[j];
    }
    fprintf(stderr, "sieve done, %llu primes\n", (unsigned long long)np);

    L[0] = 1; L[1] = 1;
    for (uint64_t n = 2; n < N; n++) {
        uint64_t m = n;
        uint8_t lose = 1;
        while (m > 1) {
            uint32_t p = spf[m];
            if (L[n - p]) { lose = 0; break; }
            while (m % p == 0) m /= p;
        }
        L[n] = lose;
    }
    fprintf(stderr, "game table done\n");

    /* census + wild extraction */
    FILE *fw = fopen("cache/wild.txt", "w");
    uint64_t c2p = 0, c4p = 0, c2k = 0, cwild = 0, coddL = 0, cevenL = 0;
    for (uint64_t n = 1; n < N; n++) {
        if (!L[n]) continue;
        if (n & 1) { coddL++; continue; }
        cevenL++;
        uint64_t h = n >> 1;
        if (h > 1 && spf[h] == h) { c2p++; continue; }          /* n = 2p */
        if (n % 4 == 0) {
            uint64_t q = n >> 2;
            if (q > 1 && spf[q] == q) { c4p++; continue; }      /* n = 4p */
        }
        if ((n & (n - 1)) == 0) { c2k++; continue; }            /* n = 2^k */
        /* wild: count distinct odd prime divisors */
        uint64_t m = n; int oodd = 0;
        while (m > 1) { uint32_t p = spf[m]; if (p != 2) oodd++; while (m % p == 0) m /= p; }
        fprintf(fw, "%llu %d\n", (unsigned long long)n, oodd);
        cwild++;
    }
    fclose(fw);
    printf("N=%llu  oddL=%llu evenL=%llu  [2p]=%llu [4p]=%llu [2^k]=%llu wild=%llu\n",
           (unsigned long long)N, (unsigned long long)coddL, (unsigned long long)cevenL,
           (unsigned long long)c2p, (unsigned long long)c4p, (unsigned long long)c2k,
           (unsigned long long)cwild);

    /* first losses for verification vs MO post */
    printf("first losses: ");
    int k = 0;
    for (uint64_t n = 1; n < N && k < 20; n++) if (L[n]) { printf("%llu,", (unsigned long long)n); k++; }
    printf("\n");

    /* bitmap out */
    FILE *fb = fopen("cache/losing.bits", "wb");
    uint8_t *bits = calloc(N / 8 + 1, 1);
    for (uint64_t n = 0; n < N; n++) if (L[n]) bits[n >> 3] |= 1 << (n & 7);
    fwrite(bits, 1, N / 8 + 1, fb);
    fclose(fb);
    return 0;
}
