/* MO 514690: exhaustive DFS for good permutations of {1..n}.
   good = every proper consecutive block (length 2..n-1) has sum not
   divisible by its length.
   Incremental check: placing a_i (1-based i), test all windows ending at i.
   Dyadic candidate filter: a_i must be congruent to a_{i-2^j} mod 2^j
   (consequence of the window conditions; used as a fast pre-filter).
   Prints every solution found (up to CAP) + total count + node stats.
   gcc -O3 -march=native good_dfs.c -o good_dfs
   ./good_dfs n [cap]                                                    */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

static int n, cap;
static long long count_sol = 0;
static unsigned long long nodes = 0;
static int a[300];        /* 1-based values */
static long long pre[300];/* prefix sums */
static uint8_t used[300];
static time_t t0;

static void rec(int i){   /* i = next position to fill, 1-based */
    if (i > n){
        count_sol++;
        if (cap && count_sol <= cap){
            printf("SOL");
            for (int k=1;k<=n;k++) printf(" %d", a[k]);
            printf("\n"); fflush(stdout);
        }
        return;
    }
    /* dyadic pre-filter: find the largest 2^j <= i-1 (so a_{i-2^j} exists
       and windows of length 2^j are proper, 2^j <= n-1) */
    int P = 0;
    for (int p2 = 2; p2 <= i-1 && p2 <= n-1; p2 <<= 1) P = p2;
    for (int v = 1; v <= n; v++){
        if (used[v]) continue;
        if (P){
            /* residue must match a_{i-P} mod P */
            if (((v - a[i-P]) & (P-1)) != 0) continue;
        }
        long long s = pre[i-1] + v;
        int ok = 1;
        int Lmax = i < n ? i : n-1;   /* windows ending at i, proper */
        for (int L = 2; L <= Lmax; L++){
            if ((s - pre[i-L]) % L == 0){ ok = 0; break; }
        }
        if (!ok) continue;
        nodes++;
        if ((nodes & 0xFFFFFFFULL) == 0){
            fprintf(stderr, "nodes=%llu depth=%d count=%lld elapsed=%lds\n",
                    nodes, i, count_sol, (long)(time(0)-t0));
        }
        used[v] = 1; a[i] = v; pre[i] = s;
        rec(i+1);
        used[v] = 0;
    }
}

int main(int argc, char** argv){
    n = argc>1 ? atoi(argv[1]) : 7;
    cap = argc>2 ? atoi(argv[2]) : 100;
    t0 = time(0);
    pre[0] = 0;
    rec(1);
    printf("n=%d total_good=%lld nodes=%llu elapsed=%lds\n",
           n, count_sol, nodes, (long)(time(0)-t0));
    return 0;
}
