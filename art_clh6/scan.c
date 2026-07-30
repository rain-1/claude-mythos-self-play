/* scan.c -- census of prime keys for the doors  t + s,  t = 2^^inf,
 * odd |s| <= SMAX, over all primes 2000 < p <= B.
 *
 * For each prime p:  r = t mod p = 2^(t mod (p-1)) mod p, where
 * t mod n is computed by the CRT / Carmichael-lambda chain:
 *     t = 0 mod 2^e,   t mod m = 2^(t mod lambda(m)) mod m   (m odd).
 * Hit:  r <= SMAX  -> p | t - r   (door s = -r), or
 *       p - r <= SMAX -> p | t + (p - r) (door s = p-r).
 * Tripwire: r == p-1 is provably impossible (t+1 is a unit in Zhat);
 * seeing it would mean a bug.
 *
 * gcc -O2 -march=native -pthread -o scan scan.c
 * ./scan B OUTPREFIX
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <stdatomic.h>

typedef unsigned __int128 u128;
typedef uint64_t u64;
typedef uint32_t u32;

#define SPF_N 1000000000ULL       /* SPF table covers [0, 1e9] */
#define SMAX 999
#define MEMO_N (1u<<25)           /* memoize t mod n for n < 2^25 */

static u32 *spf;                  /* smallest prime factor, 4GB */
static int32_t *memo;             /* t mod n for n < MEMO_N, -1 = unset */
static u32 *small_primes;         /* primes <= 100000 */
static int n_small_primes;

static u64 B;

/* ---------- modular arithmetic ---------- */
static inline u64 mulmod(u64 a, u64 b, u64 m){ return (u64)((u128)a*b % m); }
static u64 powmod(u64 b, u64 e, u64 m){
    if (m==1) return 0;
    u64 r=1; b%=m;
    while(e){ if(e&1) r=mulmod(r,b,m); b=mulmod(b,b,m); e>>=1; }
    return r;
}
static u64 gcd64(u64 a,u64 b){ while(b){u64 t=a%b;a=b;b=t;} return a; }

/* deterministic Miller-Rabin for u64 */
static int is_prime_u64(u64 n){
    if(n<2) return 0;
    for(u64 p=2;p<38;p++){ if(n%p==0) return n==p; if(p*p>n) return 1; }
    u64 d=n-1; int s=0; while(!(d&1)){d>>=1;s++;}
    static const u64 bases[12]={2,3,5,7,11,13,17,19,23,29,31,37};
    for(int i=0;i<12;i++){
        u64 a=bases[i]%n; if(!a) continue;
        u64 x=powmod(a,d,n);
        if(x==1||x==n-1) continue;
        int ok=0;
        for(int r=1;r<s;r++){ x=mulmod(x,x,n); if(x==n-1){ok=1;break;} }
        if(!ok) return 0;
    }
    return 1;
}

/* ---------- factoring (n <= ~1e10) ---------- */
/* returns k distinct primes q[] with exponents e[] */
static int factorize(u64 n, u64 q[64], int e[64]){
    int k=0;
    if(n<=1) return 0;
    while(!(n&1)){ if(k==0||q[k-1]!=2){q[k]=2;e[k]=0;k++;} e[k-1]++; n>>=1; }
    /* SPF walk when small enough */
    while(n>1){
        if(n<=SPF_N){
            while(n>1){
                u64 p=spf[n];
                if(k==0||q[k-1]!=p){q[k]=p;e[k]=0;k++;}
                e[k-1]++; n/=p;
            }
            return k;
        }
        /* n > SPF_N: trial divide by small primes, drop to SPF asap */
        int found=0;
        for(int i=1;i<n_small_primes;i++){       /* skip 2 (index 0) */
            u64 p=small_primes[i];
            if(p*p>n){ /* n is prime */ q[k]=n;e[k]=1;k++; return k; }
            if(n%p==0){
                if(k==0||q[k-1]!=p){q[k]=p;e[k]=0;k++;}
                while(n%p==0){ e[k-1]++; n/=p; }
                found=1;
                if(n<=SPF_N) break;
            }
        }
        if(n<=SPF_N) continue;
        if(!found){
            /* no factor <= 1e5, n <= ~1e10 < (1e5)^2 * 1e5 -> n must be prime
               (a composite with all factors >1e5 would exceed 1e10 only if
                it had >=2 such factors and were > 1e10; certify with MR) */
            if(!is_prime_u64(n)){ fprintf(stderr,"FATAL: unfactored composite %llu\n",(unsigned long long)n); exit(3); }
            q[k]=n;e[k]=1;k++; return k;
        }
    }
    return k;
}

/* ---------- Carmichael lambda from factorization ---------- */
static u64 carm(u64 n){
    if(n<=1) return 1;
    u64 q[64]; int e[64];
    int k=factorize(n,q,e);
    u64 lam=1;
    for(int i=0;i<k;i++){
        u64 l;
        if(q[i]==2) l = (e[i]==1)?1:(e[i]==2)?2:(1ULL<<(e[i]-2));
        else { l=q[i]-1; for(int j=1;j<e[i];j++) l*=q[i]; }
        lam = lam/gcd64(lam,l)*l;
    }
    return lam;
}

/* ---------- t mod n ---------- */
static u64 tmod(u64 n){
    if(n<=1) return 0;
    if(n<MEMO_N){ int32_t v=memo[n]; if(v>=0) return (u64)v; }
    int ez=0; u64 m=n;
    while(!(m&1)){ ez++; m>>=1; }
    u64 res;
    if(m==1) res=0;
    else{
        u64 lam=carm(m);
        u64 x=tmod(lam);
        u64 rm=powmod(2,x,m);
        if(ez==0) res=rm;
        else{
            /* CRT: 0 mod 2^ez, rm mod m ; n = 2^ez * m */
            u64 pw=1ULL<<ez;
            /* inv of pw mod m */
            u64 inv=powmod(pw%m, carm(m)-1, m); /* m odd, gcd=1; lam exponent works: pw^(lam-1) */
            u64 t=mulmod(rm,inv,m);
            res=(u128)pw*t % n;
        }
    }
    if(n<MEMO_N) memo[n]=(int32_t)res;
    return res;
}

/* ---------- hit recording ---------- */
typedef struct { long long s; u64 p; } hit_t;
#define MAXHITS_PER_THREAD 4000000
typedef struct {
    hit_t *hits; long nhits;
    u64 *uhist;              /* 8192-bin histogram of r/p */
    u64 v2hist[40];          /* v2(p-1) tally */
    u64 nprimes;
    u64 checksum;            /* xor of r values, order-independent */
} tstate_t;

#define NTHREADS 4
static tstate_t TS[NTHREADS];
static _Atomic long long next_block = 0;
#define BLOCK 20000000ULL     /* numbers per work unit */
static u64 START = 2001;

static void process_prime(u64 p, tstate_t *ts){
    u64 r = powmod(2, tmod(p-1), p);
    ts->nprimes++;
    ts->checksum ^= r*p;
    ts->uhist[(u64)((u128)r*8192/p)]++;
    u64 pm=p-1; int v2=0; while(!(pm&1)){v2++;pm>>=1;}
    ts->v2hist[v2<40?v2:39]++;
    if(r==p-1){ fprintf(stderr,"TRIPWIRE: r==p-1 at p=%llu (impossible!)\n",(unsigned long long)p); exit(4); }
    if(r<=SMAX && (r&1)){
        ts->hits[ts->nhits++] = (hit_t){ -(long long)r, p };
    } else if(p-r<=SMAX){
        ts->hits[ts->nhits++] = (hit_t){ (long long)(p-r), p };
    }
}

/* segment sieve for primes in [lo, hi) */
static void scan_range(u64 lo, u64 hi, tstate_t *ts){
    if(hi<=SPF_N){
        for(u64 n=lo;n<hi;n++) if(spf[n]==n) process_prime(n,ts);
        return;
    }
    static __thread unsigned char *seg=NULL;
    static const u64 SEG=1u<<22;
    if(!seg) seg=malloc(SEG);
    for(u64 base=lo;base<hi;base+=SEG){
        u64 top = base+SEG<hi?base+SEG:hi;
        u64 len = top-base;
        memset(seg,1,len);
        for(int i=0;i<n_small_primes;i++){
            u64 p=small_primes[i];
            if(p*p>=top) break;
            u64 st = (base+p-1)/p*p; if(st<p*p) st=p*p;
            for(u64 j=st;j<top;j+=p) seg[j-base]=0;
        }
        for(u64 j=0;j<len;j++)
            if(seg[j] && ((base+j)&1)) process_prime(base+j,ts);
    }
}

static void *worker(void *arg){
    tstate_t *ts=arg;
    for(;;){
        long long b = atomic_fetch_add(&next_block,1);
        u64 lo = START + (u64)b*BLOCK;
        if(lo>B) break;
        u64 hi = lo+BLOCK<B+1?lo+BLOCK:B+1;
        scan_range(lo,hi,ts);
        if(b%25==0){ fprintf(stderr,"block %lld (p~%.2e) hits so far t0=%ld\n",b,(double)lo,TS[0].nhits); }
    }
    return NULL;
}

int main(int argc,char**argv){
    B = argc>1?strtoull(argv[1],0,10):10000000000ULL;
    const char *pref = argc>2?argv[2]:"scan";
    fprintf(stderr,"B=%llu\n",(unsigned long long)B);

    /* SPF sieve */
    spf = malloc((SPF_N+1)*sizeof(u32));
    if(!spf){perror("spf");return 1;}
    for(u64 i=0;i<=SPF_N;i++) spf[i]=0;
    for(u64 i=2;i<=SPF_N;i++){
        if(!spf[i]){
            spf[i]=i;
            if(i*i<=SPF_N)
                for(u64 j=i*i;j<=SPF_N;j+=i) if(!spf[j]) spf[j]=i;
        }
    }
    fprintf(stderr,"SPF sieve done\n");

    /* small primes <= 1e5 */
    small_primes=malloc(20000*sizeof(u32));
    n_small_primes=0;
    for(u32 i=2;i<=100000;i++) if(spf[i]==i) small_primes[n_small_primes++]=i;
    fprintf(stderr,"%d small primes\n",n_small_primes);

    memo=malloc(MEMO_N*sizeof(int32_t));
    memset(memo,-1,MEMO_N*sizeof(int32_t));

    pthread_t th[NTHREADS];
    for(int i=0;i<NTHREADS;i++){
        TS[i].hits=malloc(MAXHITS_PER_THREAD*sizeof(hit_t));
        TS[i].nhits=0;
        TS[i].uhist=calloc(8192,sizeof(u64));
        TS[i].nprimes=0; TS[i].checksum=0;
        memset(TS[i].v2hist,0,sizeof(TS[i].v2hist));
        pthread_create(&th[i],0,worker,&TS[i]);
    }
    for(int i=0;i<NTHREADS;i++) pthread_join(th[i],0);

    char fn[256];
    snprintf(fn,256,"%s_hits.txt",pref);
    FILE *f=fopen(fn,"w");
    u64 tot=0, cks=0;
    for(int i=0;i<NTHREADS;i++){
        tot+=TS[i].nprimes; cks^=TS[i].checksum;
        for(long j=0;j<TS[i].nhits;j++)
            fprintf(f,"%lld %llu\n",TS[i].hits[j].s,(unsigned long long)TS[i].hits[j].p);
    }
    fclose(f);
    snprintf(fn,256,"%s_stats.txt",pref);
    f=fopen(fn,"w");
    fprintf(f,"B %llu\nnprimes %llu\nchecksum %llu\n",(unsigned long long)B,(unsigned long long)tot,(unsigned long long)cks);
    fprintf(f,"uhist");
    for(int b=0;b<8192;b++){ u64 s=0; for(int i=0;i<NTHREADS;i++) s+=TS[i].uhist[b]; fprintf(f," %llu",(unsigned long long)s);}
    fprintf(f,"\nv2hist");
    for(int b=0;b<40;b++){ u64 s=0; for(int i=0;i<NTHREADS;i++) s+=TS[i].v2hist[b]; fprintf(f," %llu",(unsigned long long)s);}
    fprintf(f,"\n");
    fclose(f);
    fprintf(stderr,"done: %llu primes\n",(unsigned long long)tot);
    return 0;
}
