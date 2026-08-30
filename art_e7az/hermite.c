/* MO 514763: can a fixed nonzero algebraic number be a root of infinitely
   many Hermite polynomials?  Certificate engine: for every pair m < n <= N,
   compute deg gcd(H_m, H_n) mod p (p odd prime, p > 2N so p never divides
   the leading coefficient 2^n or the recurrence coefficient 2k).
   Since deg gcd_Q <= deg gcd_p, a pair with deg gcd_p == [m,n both odd]
   certifies gcd_Q(H_m,H_n) = x^[both odd]: the ONLY root two distinct
   Hermite polynomials ever share (up to N) is x = 0.

   gcc -O2 hermite.c -o hermite -lm && ./hermite 500                        */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

static uint64_t P;
static inline uint64_t addm(uint64_t a, uint64_t b){ a+=b; return a>=P?a-P:a; }
static inline uint64_t subm(uint64_t a, uint64_t b){ return a>=b?a-b:a+P-b; }
static inline uint64_t mulm(uint64_t a, uint64_t b){ return (unsigned __int128)a*b%P; }
static uint64_t powm(uint64_t b, uint64_t e){ uint64_t r=1; while(e){ if(e&1) r=mulm(r,b); b=mulm(b,b); e>>=1;} return r; }
static inline uint64_t invm(uint64_t a){ return powm(a, P-2); }

int main(int argc, char** argv){
    int N = argc>1 ? atoi(argv[1]) : 500;
    /* primes > 2N, 62-bit safe */
    uint64_t primes[3] = {2147483659ULL, 2147483693ULL, 2147483713ULL};
    /* H_k mod p: physicists' Hermite, H_0=1, H_1=2x, H_{k+1}=2x H_k - 2k H_{k-1} */
    int64_t viol_total = 0, pairs = 0, xshared = 0;
    for (int pi = 0; pi < 1; pi++){          /* second prime only on violation */
        P = primes[pi];
        uint64_t **H = malloc((N+1)*sizeof(uint64_t*));
        for (int k=0;k<=N;k++){ H[k]=calloc(N+2,8); }
        H[0][0]=1; H[1][1]=2;
        for (int k=1;k<N;k++){
            for (int j=0;j<=k;j++) H[k+1][j+1] = mulm(2, H[k][j]);
            uint64_t c = mulm(2, k % P);
            for (int j=0;j<=k-1;j++) H[k+1][j] = subm(H[k+1][j], mulm(c, H[k-1][j]));
        }
        uint64_t *A = malloc((N+2)*8), *B = malloc((N+2)*8);
        for (int m=1;m<=N;m++){
            for (int n=m+1;n<=N;n++){
                memcpy(A, H[n], (n+1)*8); int da=n;
                memcpy(B, H[m], (m+1)*8); int db=m;
                while (db >= 0){
                    /* A = A mod B */
                    uint64_t inv = invm(B[db]);
                    while (da >= db){
                        uint64_t c = mulm(A[da], inv);
                        if (c){
                            int sh = da-db;
                            for (int j=0;j<=db;j++) A[j+sh] = subm(A[j+sh], mulm(c,B[j]));
                        }
                        da--;
                        while (da>=0 && !A[da]) da--;
                        if (da < 0) break;
                    }
                    if (da < 0) break;
                    /* swap */
                    uint64_t* t=A; A=B; B=t; int td=da; da=db; db=td;
                }
                int dg = da<0 ? db : (db<0 ? da : -1); /* one of them is the gcd */
                /* after loop: if da<0, gcd=B (deg db); this logic: loop exits when da<0 */
                int expected = (m&1) && (n&1) ? 1 : 0;
                pairs++;
                if (dg != expected){
                    viol_total++;
                    printf("VIOLATION? m=%d n=%d deg_gcd=%d expected=%d (p=%llu)\n",
                           m,n,dg,expected,(unsigned long long)P);
                } else if (expected==1) xshared++;
            }
            if (m%50==0){ fprintf(stderr,"m=%d done\n",m); }
        }
        for (int k=0;k<=N;k++) free(H[k]);
        free(H); free(A); free(B);
    }
    printf("pairs=%lld  gcd=x pairs (both odd)=%lld  violations=%lld\n",
           (long long)pairs,(long long)xshared,(long long)viol_total);
    if (!viol_total)
        printf("CERTIFIED: for all 1<=m<n<=%d, gcd(H_m,H_n) = x^[m,n both odd].\n"
               "No nonzero algebraic number is a root of two distinct H_k, k<=%d.\n", N, N);
    return viol_total ? 1 : 0;
}
