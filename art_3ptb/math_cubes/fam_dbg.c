/* Search for ternary identities  sum_{i=1}^6 (A_i x + B_i y + C_i z)^3 = alpha y^3 + 3 beta y^2 z
 * with all A_i != 0.  Setting y=1, z=t gives n(t) = alpha + 3 beta t: a whole residue class.
 * Method: (A,C) must itself be a representation of 0 (sum (A x + C z)^3 == 0).  Enumerate
 * nontrivial zero reps via meet in the middle (height <= h), then for each solve the linear
 * conditions  sum A^2 B = sum A B C = sum B C^2 = 0  for B in a box, check sum A B^2 = 0,
 * print alpha = sum B^3, beta = sum B^2 C  when beta != 0.
 * usage: fam h K   (prints lines: beta alpha A1 B1 C1 ... A6 B6 C6)
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct { uint64_t key; uint32_t idx; } T;
static int cmpT(const void *a, const void *b) {
    uint64_t x = ((const T *)a)->key, y = ((const T *)b)->key;
    return x < y ? -1 : x > y;
}
int LA[4000], LC[4000], L;
long det3(long m[3][3]) {
    return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1]) - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
         + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]);
}
int main(int argc, char **argv) {
    int h = atoi(argv[1]), K = atoi(argv[2]);
    L = 0;
    for (int a = -h; a <= h; a++) if (a) for (int c = -h; c <= h; c++) { LA[L] = a; LC[L] = c; L++; }
    long cap = (long)L * (L + 1) * (L + 2) / 6 + 10;
    T *arr = malloc(sizeof(T) * cap); long m = 0;
    const long OFF = 32768;
    for (int i = 0; i < L; i++) for (int j = i; j < L; j++) for (int k = j; k < L; k++) {
        long a[3] = {LA[i], LA[j], LA[k]}, c[3] = {LC[i], LC[j], LC[k]};
        long k1 = 0, k2 = 0, k3 = 0, k4 = 0;
        for (int q = 0; q < 3; q++) { k1 += a[q]*a[q]*a[q]; k2 += a[q]*a[q]*c[q]; k3 += a[q]*c[q]*c[q]; k4 += c[q]*c[q]*c[q]; }
        arr[m].key = ((uint64_t)(k1+OFF) << 48) | ((uint64_t)(k2+OFF) << 32) | ((uint64_t)(k3+OFF) << 16) | (uint64_t)(k4+OFF);
        arr[m].idx = (uint32_t)((i * L + j) * L + k); m++;
    }
    qsort(arr, m, sizeof(T), cmpT);
    long nzero = 0, nfam = 0;
    for (long s = 0; s < m;) {
        long e = s; while (e < m && arr[e].key == arr[s].key) e++;
        for (long p = s; p < e; p++) for (long q = p + 1; q < e; q++) {
            uint32_t x = arr[p].idx, y = arr[q].idx;
            int id[6] = { x / (L*L), (x / L) % L, x % L, y / (L*L), (y / L) % L, y % L };
            long A[6], C[6];
            for (int r = 0; r < 6; r++) { A[r] = LA[id[r]]; C[r] = LC[id[r]]; if (r >= 3) { A[r] = -A[r]; C[r] = -C[r]; } }
            /* skip if some form cancels against another (f and -f): reduces to 4 terms */
            int triv = 0;
            for (int r = 0; r < 3; r++) for (int u = 3; u < 6; u++) if (A[r] == -A[u] && C[r] == -C[u]) triv = 1;
            if (triv) continue;
            nzero++; if (nzero<=8) { for(int r=0;r<6;r++) fprintf(stderr,"(%ld,%ld) ",A[r],C[r]); fprintf(stderr,"\n"); }
            /* rows: A^2, A C, C^2 ; choose 3 pivot columns with nonzero det */
            long M[3][6];
            for (int r = 0; r < 6; r++) { M[0][r] = A[r]*A[r]; M[1][r] = A[r]*C[r]; M[2][r] = C[r]*C[r]; }
            int piv[3] = {-1,-1,-1}, fr[3]; long D = 0;
            for (int a0 = 0; a0 < 6 && !D; a0++) for (int a1 = a0+1; a1 < 6 && !D; a1++) for (int a2 = a1+1; a2 < 6 && !D; a2++) {
                long S[3][3];
                for (int r = 0; r < 3; r++) { S[r][0] = M[r][a0]; S[r][1] = M[r][a1]; S[r][2] = M[r][a2]; }
                D = det3(S); if (D) { piv[0] = a0; piv[1] = a1; piv[2] = a2; }
            }
            if (!D) continue; /* rank-deficient; skip */
            int nf = 0; for (int r = 0; r < 6; r++) if (r != piv[0] && r != piv[1] && r != piv[2]) fr[nf++] = r;
            long S[3][3]; for (int r = 0; r < 3; r++) for (int cc = 0; cc < 3; cc++) S[r][cc] = M[r][piv[cc]];
            for (long f0 = -K; f0 <= K; f0++) for (long f1 = -K; f1 <= K; f1++) for (long f2 = -K; f2 <= K; f2++) {
                long rhs[3];
                for (int r = 0; r < 3; r++) rhs[r] = -(M[r][fr[0]]*f0 + M[r][fr[1]]*f1 + M[r][fr[2]]*f2);
                long B[6]; int ok = 1;
                B[fr[0]] = f0; B[fr[1]] = f1; B[fr[2]] = f2;
                for (int cc = 0; cc < 3 && ok; cc++) {
                    long Sc[3][3];
                    for (int r = 0; r < 3; r++) for (int t = 0; t < 3; t++) Sc[r][t] = (t == cc) ? rhs[r] : S[r][t];
                    long Dc = det3(Sc);
                    if (Dc % D) ok = 0; else B[piv[cc]] = Dc / D;
                }
                if (!ok) continue;
                long q2 = 0, al = 0, be = 0, maxb = 0;
                for (int r = 0; r < 6; r++) { q2 += A[r]*B[r]*B[r]; al += B[r]*B[r]*B[r]; be += B[r]*B[r]*C[r]; if (labs(B[r]) > maxb) maxb = labs(B[r]); }
                if (q2 || !be || maxb > K) continue;
                nfam++;
                printf("%ld %ld", be, al);
                for (int r = 0; r < 6; r++) printf("  %ld %ld %ld", A[r], B[r], C[r]);
                printf("\n");
            }
        }
        s = e;
    }
    fprintf(stderr, "zero reps %ld, families %ld\n", nzero, nfam);
    return 0;
}
