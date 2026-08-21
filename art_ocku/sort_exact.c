/* MO 513971: alternating lexicographic row/column sorting of an n x n binary
   matrix.  T(A) = min{ t>=1 : A^(t) is both row- and column-lex-sorted }, where
   A^(1)=R(A), A^(2)=C(A^(1)), ...  (each sort counts one step).

   KEY REDUCTION: A^(1)=R(A) depends only on the MULTISET of rows of A, hence so
   does T.  So mu_n = 2^{-n^2} * sum over nondecreasing row tuples r_1<=...<=r_n
   of (n!/prod mult_i!) * T(multiset).  #multisets = C(2^n+n-1, n):
   n=5: 376,992   n=6: 119,877,472   n=7: 93,594,900,020  (vs 2^49 raw).

   Exact integer accumulation: SUM = sum w*T <= 2^{n^2} * (2n-3) < 2^63 for n<=7.
   Also tallies the exact weighted distribution of T and max T.

   gcc -O3 -march=native -fopenmp sort_exact.c -o sort_exact
   ./sort_exact n            (n <= 7)                                          */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>

static int N;               /* matrix size */
#define TMAXBUF 64

/* rows as integers, MSB = column 0: lex order on rows == integer order.      */

static inline void sortrows(uint32_t* r, int n){       /* insertion sort */
    for (int i=1;i<n;i++){ uint32_t x=r[i]; int j=i-1;
        while (j>=0 && r[j]>x){ r[j+1]=r[j]; j--; } r[j+1]=x; }
}
static inline void transpose(const uint32_t* r, uint32_t* t, int n){
    for (int j=0;j<n;j++) t[j]=0;
    for (int i=0;i<n;i++){
        uint32_t row = r[i];
        for (int j=0;j<n;j++)
            if (row & (1u<<(N-1-j))) t[j] |= (1u<<(N-1-i));
    }
}
static inline int nondecreasing(const uint32_t* r, int n){
    for (int i=1;i<n;i++) if (r[i-1]>r[i]) return 0;
    return 1;
}
/* T of the multiset (r need not be sorted; R is applied first) */
static inline int Tof(const uint32_t* r0, int n){
    uint32_t a[8], t[8];
    memcpy(a, r0, 4*n);
    sortrows(a, n);                       /* t = 1 : rows sorted */
    int step = 1;
    for (;;){
        if (step & 1){                    /* a is row-sorted; check columns */
            transpose(a, t, n);
            if (nondecreasing(t, n)) return step;
            sortrows(t, n);               /* column sort via transpose */
            memcpy(a, t, 4*n);            /* a now holds transposed matrix */
        } else {                          /* a holds transpose (col-sorted); check rows */
            transpose(a, t, n);           /* back to row orientation */
            if (nondecreasing(t, n)) return step;
            sortrows(t, n);
            memcpy(a, t, 4*n);            /* a row-sorted again */
        }
        step++;
        if (step > 4*N) { fprintf(stderr,"BUG: no convergence\n"); exit(1); }
    }
}

/* factorials up to 7 */
static const uint64_t FACT[9]={1,1,2,6,24,120,720,5040,40320};

/* weight = n!/prod(mult!) of a sorted tuple */
static inline uint64_t weight(const uint32_t* r, int n){
    uint64_t w = FACT[n]; int run=1;
    for (int i=1;i<n;i++){
        if (r[i]==r[i-1]) run++;
        else { w /= FACT[run]; run=1; }
    }
    w /= FACT[run];
    return w;
}

int main(int argc, char** argv){
    N = argc>1 ? atoi(argv[1]) : 5;
    if (N<1 || N>7){ fprintf(stderr,"n must be 1..7\n"); return 1; }
    const uint32_t M = 1u<<N;             /* row values 0..M-1 */
    uint64_t total = 0;                   /* sum w*T */
    uint64_t dist[TMAXBUF]; memset(dist,0,sizeof dist);
    int maxT = 0; uint32_t argmax[8]={0};

    double t0 = omp_get_wtime();
    /* parallel over first two rows (a<=b); serial odometer for the rest */
    long ntask = (long)M*(M+1)/2;
    #pragma omp parallel
    {
        uint64_t ltot=0, ldist[TMAXBUF]; memset(ldist,0,sizeof ldist);
        int lmax=0; uint32_t largmax[8]={0};
        #pragma omp for schedule(dynamic,1)
        for (long task=0; task<ntask; task++){
            /* decode task -> (a,b) with a<=b  (row-major over upper triangle) */
            uint32_t a=0; long rem=task;
            while (rem >= (long)(M - a)) { rem -= (M - a); a++; }
            uint32_t b = a + (uint32_t)rem;
            uint32_t r[8]; r[0]=a;
            if (N==1){
                int T=Tof(r,1); uint64_t w=1; ltot+=w*T; ldist[T]+=w;
                if(T>lmax){lmax=T; memcpy(largmax,r,4);}
                continue;
            }
            r[1]=b;
            if (N==2){
                int T=Tof(r,2); uint64_t w=weight(r,2); ltot+=w*T; ldist[T]+=w;
                if(T>lmax){lmax=T; memcpy(largmax,r,8);}
                continue;
            }
            /* odometer over r[2..N-1], nondecreasing, starting at b */
            for (int i=2;i<N;i++) r[i]=b;
            for (;;){
                int T = Tof(r,N);
                uint64_t w = weight(r,N);
                ltot += w*(uint64_t)T; ldist[T]+=w;
                if (T>lmax){ lmax=T; memcpy(largmax,r,4*N); }
                /* increment odometer */
                int k=N-1;
                while (k>=2 && r[k]==M-1) k--;
                if (k<2) break;
                uint32_t v = r[k]+1;
                for (int i=k;i<N;i++) r[i]=v;
            }
        }
        #pragma omp critical
        {
            total += ltot;
            for (int i=0;i<TMAXBUF;i++) dist[i]+=ldist[i];
            if (lmax>maxT){ maxT=lmax; memcpy(argmax,largmax,sizeof argmax); }
        }
    }
    double el = omp_get_wtime()-t0;
    /* denominator 2^{n^2} */
    fprintf(stderr,"n=%d done in %.1fs\n", N, el);
    printf("n=%d  SUM=%llu  DEN=2^%d\n", N,(unsigned long long)total, N*N);
    /* reduced fraction: strip common powers of 2 */
    uint64_t num=total; int e=N*N;
    while (!(num&1) && e>0){ num>>=1; e--; }
    printf("mu_%d = %llu / 2^%d  =  %.9f\n", N,(unsigned long long)num, e,
           (double)total / ldexp(1.0, N*N));
    printf("maxT = %d  (2n-3 = %d)  witness rows:", maxT, 2*N-3);
    for (int i=0;i<N;i++) printf(" %u", argmax[i]);
    printf("\nT distribution (weighted counts / 2^%d):\n", N*N);
    for (int t=1;t<TMAXBUF;t++) if (dist[t])
        printf("  T=%2d  %llu   (%.6e)\n", t,(unsigned long long)dist[t],
               (double)dist[t]/ldexp(1.0,N*N));
    return 0;
}
