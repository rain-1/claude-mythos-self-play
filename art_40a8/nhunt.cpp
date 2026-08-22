// Deep hunt for primitive solutions of x^4 + y^4 + z^4 = N t^4  (0<=x<=y<=z, t<=T)
// Meet-in-the-middle over value windows:
//   v2 = N t^4 - z^4 for z in [ceil((N/3)^{1/4} t), floor(N^{1/4} t)]  (z = largest)
//   v1 = x^4 + y^4 streamed against sorted per-window v2 table.
// Every hit is re-verified exactly and printed with gcd-primitivity flag.
// Build: g++ -O3 -march=native -o nhunt nhunt.cpp        (uint64, T<=32000 for N<=17)
//        g++ -O3 -march=native -DWIDE -o nhuntw nhunt.cpp (__int128, larger T)
// Run:   ./nhunt N T [K]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <cmath>
#include <vector>
#include <algorithm>
using namespace std;

#ifdef WIDE
typedef unsigned __int128 val_t;
#else
typedef uint64_t val_t;
#endif

static inline val_t p4(uint64_t v){ val_t s=(val_t)v*v; return s*s; }

// integer fourth root
static inline uint64_t iroot4(val_t v){
    double d = pow((double)v, 0.25);
    uint64_t r = (uint64_t)d;
    while (p4(r+1) <= v) r++;
    while (r > 0 && p4(r) > v) r--;
    return r;
}
static uint64_t g4(uint64_t a, uint64_t b){ while(b){uint64_t t=a%b;a=b;b=t;} return a; }

struct Ent { val_t v; uint32_t t; };

int main(int argc, char** argv){
    uint64_t N = argc>1 ? strtoull(argv[1],0,10) : 17;
    uint64_t T = argc>2 ? strtoull(argv[2],0,10) : 32000;
    int K = argc>3 ? atoi(argv[3]) : 48;
    val_t Vmax = (val_t)N * p4(T);
    fprintf(stderr, "nhunt N=%llu T=%llu K=%d\n",(unsigned long long)N,(unsigned long long)T,K);

    // window edges: sqrt-spaced so v1-count per window is roughly equal
    vector<val_t> edge(K+1);
    for (int k=0;k<=K;k++){
        double f = (double)k / K;
        edge[k] = (val_t)( (double)Vmax * f * f );
    }
    edge[0]=1; edge[K]=Vmax+1;

    uint64_t nhits=0, nprim=0;
    double t0 = 0;
    for (int k=0;k<K;k++){
        val_t A = edge[k], B = edge[k+1];
        if (B<=A) continue;
        // build v2 table for this window
        vector<Ent> tab;
        for (uint64_t t=1;t<=T;t++){
            val_t s = (val_t)N * p4(t);
            // z largest: z^4 >= s/3 and z^4 <= s-1; window: v2 = s-z^4 in [A,B)
            uint64_t zlo = iroot4((s + 2)/3);
            while (3*p4(zlo) < s) zlo++;
            uint64_t zhi = iroot4(s-1);
            // v2 < B  => z^4 > s-B ; v2 >= A => z^4 <= s-A
            if (s > A){
                uint64_t z2 = iroot4(s - A);
                if (z2 < zhi) zhi = z2;
            } else continue;
            if (s >= B){
                uint64_t z1 = iroot4(s - B);   // z must be > z1
                if (z1 + 1 > zlo) zlo = z1 + 1;
            }
            for (uint64_t z=zlo; z<=zhi; z++){
                val_t v2 = s - p4(z);
                if (v2 >= A && v2 < B) tab.push_back({v2,(uint32_t)t});
            }
        }
        sort(tab.begin(), tab.end(), [](const Ent&a, const Ent&b){return a.v<b.v;});
        size_t M = tab.size();
        if (!M) continue;
        // stream v1 = x^4 + y^4, x<=y
        uint64_t xmax = iroot4((B-1)/2);
        for (uint64_t x=0;x<=xmax;x++){
            val_t x4 = p4(x);
            if (x4*2 >= B) break;
            val_t ylo4 = (A > x4) ? (A - x4) : x4; // y>=x
            uint64_t ylo = iroot4(ylo4); if (p4(ylo) < ylo4) ylo++;
            if (ylo < x) ylo = x;
            uint64_t yhi = iroot4(B-1-x4);
            for (uint64_t y=ylo;y<=yhi;y++){
                val_t v = x4 + p4(y);
                // binary search
                size_t lo=0, hi=M;
                while (lo<hi){ size_t mid=(lo+hi)>>1; if (tab[mid].v < v) lo=mid+1; else hi=mid; }
                for (size_t i=lo; i<M && tab[i].v==v; i++){
                    uint64_t t = tab[i].t;
                    val_t s = (val_t)N * p4(t);
                    uint64_t z = iroot4(s - v);
                    if (p4(z) != s - v) continue;
                    if (y > z) continue;            // enforce ordering
                    if (p4(x)+p4(y)+p4(z) != s) continue;
                    uint64_t g = g4(g4(x,y), g4(z,t));
                    nhits++;
                    if (g==1){ nprim++;
                        printf("PRIMITIVE %llu^4 + %llu^4 + %llu^4 = %llu * %llu^4\n",
                          (unsigned long long)x,(unsigned long long)y,(unsigned long long)z,
                          (unsigned long long)N,(unsigned long long)t);
                    }
                    fflush(stdout);
                }
            }
        }
        fprintf(stderr,"window %d/%d done tab=%zu\n",k+1,K,M);
    }
    fprintf(stderr,"NHUNT_DONE N=%llu T=%llu hits=%llu primitive=%llu\n",
        (unsigned long long)N,(unsigned long long)T,
        (unsigned long long)nhits,(unsigned long long)nprim);
    return 0;
}
