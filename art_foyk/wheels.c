/* MO 513838: exact counts of cycle types of sigma*tau, sigma cyclic on S1, tau cyclic on S2.
   Orbit reduction: enumerate cyclic binary words (m ones among k) up to rotation for sigma,
   weight = #distinct rotations; enumerate ALL (k-1)! tau. Output: per-type weighted counts.
   Usage: ./wheels k m   -> lines "type_lengths...: count"  (count = sum over words weight*#tau hits)
   Exact probability = count * m!*(k-m)!/k / ((k-1)!)^2  -- computed by the Python wrapper. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int k, m, N;
#define MAXN 64
#define MAXP 4096   /* > p(24) = 1575 */

static int parts[MAXP][MAXN+1]; /* sorted desc, 0-terminated */
static int nparts = 0;
static uint64_t counts[MAXP];

static int cur[MAXN+1];
static void gen_parts(int rem, int maxp, int depth){
    if (rem == 0){ memcpy(parts[nparts], cur, sizeof(int)*(depth+1)); parts[nparts][depth]=0; nparts++; return; }
    for (int p = rem < maxp ? rem : maxp; p >= 1; p--){ cur[depth]=p; gen_parts(rem-p, p, depth+1); }
}
static int cmp_part(const int*a, const int*b){
    for (int i=0;;i++){ if (a[i]!=b[i]) return a[i]-b[i]; if (!a[i]) return 0; }
}
static int find_part(const int* t){
    int lo=0, hi=nparts-1;
    while (lo<=hi){ int mid=(lo+hi)/2; int c=cmp_part(parts[mid], t);
        if (c==0) return mid; if (c<0) lo=mid+1; else hi=mid-1; }
    fprintf(stderr,"part not found\n"); exit(1);
}
static int part_cmp_qsort(const void*a, const void*b){ return cmp_part((const int*)a,(const int*)b); }

int main(int argc, char** argv){
    k = atoi(argv[1]); m = atoi(argv[2]); N = 2*k - m;
    gen_parts(N, N, 0);
    qsort(parts, nparts, sizeof(parts[0]), part_cmp_qsort);
    memset(counts, 0, sizeof(counts));

    /* S1 = 0..k-1, A = k-m..k-1, S2 = k-m..N-1, B2 = k..N-1 */
    /* enumerate cyclic word classes: binary words w[0..k-1] with m ones, canonical = lexicographically
       minimal rotation; weight = number of distinct rotations */
    int w[MAXN];
    /* iterate all C(k,m) words via combinations of one-positions */
    int pos[MAXN];
    for (int i=0;i<m;i++) pos[i]=i;
    int sigma[MAXN], tau[MAXN], pi[MAXN], seen[MAXN], cyc[MAXN], perm[MAXN], ccc[MAXN];
    long long total_words=0;
    while (1){
        memset(w, 0, sizeof(int)*k);
        for (int i=0;i<m;i++) w[pos[i]]=1;
        /* canonical rotation check: is w the lexicographically minimal rotation? count distinct rotations */
        int minimal = 1, distinct = k;
        for (int r=1;r<k && minimal;r++){
            int c=0;
            for (int i=0;i<k;i++){ int a=w[(i+r)%k]-w[i]; if(a){c=a;break;} }
            if (c<0) minimal=0;
            else if (c==0){ distinct = r < distinct ? r : distinct; }
        }
        if (minimal){
            total_words++;
            /* build sigma: cycle over S1; positions with w=1 get A elements (k-m..k-1 in order),
               w=0 get B1 elements (0..k-m-1 in order) */
            int elems[MAXN]; int ia=k-m, ib=0;
            for (int i=0;i<k;i++) elems[i] = w[i] ? ia++ : ib++;
            for (int i=0;i<N;i++) sigma[i]=i;
            for (int i=0;i<k;i++) sigma[elems[i]] = elems[(i+1)%k];
            uint64_t weight = distinct;
            /* enumerate all tau: cycles on S2 = {k-m..N-1}, first elem s0=k-m fixed,
               permute the remaining k-1 elements via Heap's algorithm */
            int nrest = k-1;
            int rest[MAXN];
            for (int i=0;i<nrest;i++) rest[i] = k-m+1+i;
            int c_[MAXN]; memset(c_,0,sizeof(int)*nrest);
            /* pi differs from sigma only via tau on S2: pi[i]=sigma[tau[i]]; for i not in S2 pi[i]=sigma[i] */
            for (int i=0;i<N;i++) pi[i]=sigma[i];
            /* process a permutation */
            #define PROCESS() do { \
                cyc[0]=k-m; for(int i=0;i<nrest;i++) cyc[i+1]=rest[i]; \
                for (int i=0;i<k;i++) pi[cyc[i]] = sigma[cyc[(i+1)%k]]; \
                memset(seen,0,sizeof(int)*N); \
                int nc=0; \
                for (int s=0;s<N;s++) if(!seen[s]){ int l=0,j=s; while(!seen[j]){seen[j]=1;j=pi[j];l++;} ccc[nc++]=l; } \
                /* insertion sort desc */ \
                for (int i=1;i<nc;i++){ int v=ccc[i],j2=i-1; while(j2>=0&&ccc[j2]<v){ccc[j2+1]=ccc[j2];j2--;} ccc[j2+1]=v; } \
                ccc[nc]=0; \
                counts[find_part(ccc)] += weight; \
            } while(0)
            PROCESS();
            int i2=0;
            while (i2 < nrest){
                if (c_[i2] < i2){
                    int sw = (i2%2==0)?0:c_[i2];
                    int t2=rest[sw]; rest[sw]=rest[i2]; rest[i2]=t2;
                    PROCESS();
                    c_[i2]++; i2=0;
                } else { c_[i2]=0; i2++; }
            }
        }
        /* next combination */
        int j=m-1;
        while (j>=0 && pos[j]==k-m+j) j--;
        if (j<0) break;
        pos[j]++;
        for (int l=j+1;l<m;l++) pos[l]=pos[l-1]+1;
    }
    for (int K=0;K<nparts;K++) if (counts[K]){
        for (int i=0;parts[K][i];i++) printf("%d%c", parts[K][i], parts[K][i+1]?',':' ');
        printf(": %llu\n", (unsigned long long)counts[K]);
    }
    fprintf(stderr, "words=%lld\n", total_words);
    return 0;
}
