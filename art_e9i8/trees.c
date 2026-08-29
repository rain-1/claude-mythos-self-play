/* MO 514744: quadratic-residue interrogation of T(m,n) = # spanning trees
   of the m x n grid graph, 2 <= m <= n <= N, WITHOUT computing T.

   Identity: T(m,n) = Res(q_m, f_n) / m, where
     q_m(t) = det(tI - L_m)/t   (monic, deg m-1; roots = nonzero path-
                                 Laplacian eigenvalues mu_j = 2-2cos(j pi/m))
     f_n(t) = det(L_n + tI)     (roots -lambda_k <= 0: no root shared w/ q_m)
   Proof: matrix-tree + eigenvalue split of L_m (+) L_n: mn*T = m * n *
   (Res(q_m,f_n)/m); the j=0 slice contributes n, k=0 contributes m.

   Per odd prime p (48 primes ~1000..1321):
     q_m mod p by continuant recurrence;
     f_n in GF(p)[t]/(q_m) by 3-term recurrence;
     Res(q_m, f_n) mod p by Euclidean resultant (q_m monic);
     T mod p = Res * m^{-1}.
   chi(T mod p) = -1 kills the pair (T not a perfect square); record the
   first witness index.  Survivors of all 48 primes are printed.

   Output lines:
     V m n p T          verification values (small pairs)
     W m n w nz         w = 1-based first witness (0 = none), nz = # p with T!=0 mod p
     S m n nz           survivor (chi >= 0 for all primes, nz nonzero)
   gcc -O3 -march=native trees.c -o trees -lm ; ./trees N               */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define NP 48
#define NMAX 512
static const int64_t PRIMES[NP] = {
  1009,1013,1019,1021,1031,1033,1039,1049,1051,1061,1063,1069,
  1087,1091,1093,1097,1103,1109,1117,1123,1129,1151,1153,1163,
  1171,1181,1187,1193,1201,1213,1217,1223,1229,1231,1237,1249,
  1259,1277,1279,1283,1289,1291,1297,1301,1303,1307,1319,1321 };

static int64_t P;
static inline int64_t addm(int64_t a,int64_t b){int64_t s=a+b;return s>=P?s-P:s;}
static inline int64_t subm(int64_t a,int64_t b){int64_t s=a-b;return s<0?s+P:s;}
static inline int64_t mulm(int64_t a,int64_t b){return (a*b)%P;}
static int64_t powm(int64_t a,int64_t e){int64_t r=1;a%=P;while(e){if(e&1)r=mulm(r,a);a=mulm(a,a);e>>=1;}return r;}
static int64_t invm(int64_t a){return powm(a,P-2);}
static int legendre(int64_t a){ if(a==0) return 0; return powm(a,(P-1)/2)==1?1:-1; }

/* resultant of A (deg da, monic on entry) and B (deg db <= da-1), mod P */
static int64_t resultant(const int64_t *A,int da,const int64_t *B,int db){
    static int64_t U[NMAX],V[NMAX],W2[NMAX];
    memcpy(U,A,(da+1)*sizeof(int64_t));
    while(db>=0 && B[db]==0) db--;
    if(db<0) return 0;
    memcpy(V,B,(db+1)*sizeof(int64_t));
    int du=da, dv=db;
    int64_t res=1;
    for(;;){
        if(dv==0){ res=mulm(res,powm(V[0],du)); return res; }
        int64_t lcv=V[dv], il=invm(lcv);
        for(int dr=du; dr>=dv; dr--){
            if(U[dr]){
                int64_t c=mulm(U[dr],il);
                for(int i=0;i<=dv;i++) U[dr-dv+i]=subm(U[dr-dv+i],mulm(c,V[i]));
            }
        }
        int dn=dv-1; while(dn>=0 && U[dn]==0) dn--;
        if((du&1)&&(dv&1)) res=P-res;
        res=mulm(res,powm(lcv,du-(dn<0?0:dn)));
        if(dn<0) return dv>0?0:res;
        memcpy(W2,V,(dv+1)*sizeof(int64_t));
        memcpy(V,U,(dn+1)*sizeof(int64_t));
        memcpy(U,W2,(dv+1)*sizeof(int64_t));
        du=dv; dv=dn;
    }
}

static int8_t  wit[NMAX][NMAX];    /* 0 = alive */
static int16_t nzc[NMAX][NMAX];

int main(int argc,char**argv){
    int N = argc>1 ? atoi(argv[1]) : 200;
    if(N>=NMAX){fprintf(stderr,"N too big\n");return 1;}
    static int64_t qm[NMAX],c0[NMAX],c1[NMAX],c2[NMAX];
    static int64_t e0[NMAX],e1[NMAX],e2[NMAX],fn[NMAX],tp[NMAX];

    for(int pi=0;pi<NP;pi++){
        P=PRIMES[pi];
        for(int m=2;m<=N;m++){
            int dq=m-1;
            /* q_m = det(tI - L_m)/t: continuants c_k, k x k top-left of
               (tI - L_m): c_0=1, c_1=t-1, c_k=(t-2)c_{k-1}-c_{k-2} (k<m),
               c_m=(t-1)c_{m-1}-c_{m-2}; q_m = c_m/t.                    */
            memset(c0,0,(m+1)*sizeof(int64_t)); c0[0]=1;
            memset(c1,0,(m+1)*sizeof(int64_t)); c1[1]=1; c1[0]=P-1;
            for(int k=2;k<=m;k++){
                int64_t a0=(k==m)?P-1:P-2;
                memset(c2,0,(m+1)*sizeof(int64_t));
                for(int i=0;i<k;i++) if(c1[i]){
                    c2[i+1]=addm(c2[i+1],c1[i]);
                    c2[i]=addm(c2[i],mulm(a0,c1[i]));
                }
                if(c1[k]){ /* deg k term (i=k) */
                    c2[k+1<=m?k+1:m]= (k+1<=m)? addm(c2[k+1],c1[k]) : c2[m];
                    c2[k]=addm(c2[k],mulm(a0,c1[k]));
                }
                for(int i=0;i<=m;i++) c2[i]=subm(c2[i],c0[i]);
                memcpy(c0,c1,(m+1)*sizeof(int64_t));
                memcpy(c1,c2,(m+1)*sizeof(int64_t));
            }
            if(c1[0]!=0){fprintf(stderr,"c_m(0)!=0 m=%d\n",m);return 1;}
            for(int i=0;i<m;i++) qm[i]=c1[i+1];
            if(qm[dq]!=1){fprintf(stderr,"qm not monic m=%d\n",m);return 1;}

            /* multiply-by-t mod qm macro (deg < dq arrays) */
            #define MULT(src,out) do{ \
                int64_t hi=(dq>0)?src[dq-1]:0; \
                for(int i=dq-1;i>=1;i--) out[i]=src[i-1]; \
                out[0]=0; \
                if(hi) for(int i=0;i<dq;i++) out[i]=subm(out[i],mulm(hi,qm[i])); \
            }while(0)

            /* E_0=1, E_1=1+t; E_k=(2+t)E_{k-1}-E_{k-2};
               f_n=(1+t)E_{n-1}-E_{n-2}.  All reduced mod (p, qm). */
            memset(e0,0,dq*sizeof(int64_t)); e0[0]=1;
            memset(e1,0,dq*sizeof(int64_t));
            if(dq==1){ e1[0]=subm(1,qm[0]); }        /* t = -qm[0] */
            else { e1[0]=1; e1[1]=1; }
            int64_t im=invm(m%P);
            for(int n=2;n<=N;n++){
                /* f_n from (e0,e1)=(E_{n-2},E_{n-1}) */
                if(n>=m){
                    MULT(e1,tp);
                    for(int i=0;i<dq;i++) fn[i]=subm(addm(tp[i],e1[i]),e0[i]);
                    int64_t r=resultant(qm,dq,fn,dq-1);
                    int64_t T=mulm(r,im);
                    if(pi==0 && m<=3 && n<=6) printf("V %d %d %lld %lld\n",m,n,(long long)P,(long long)T);
                    if(T){ nzc[m][n]++; if(!wit[m][n] && legendre(T)<0) wit[m][n]=pi+1; }
                }
                /* advance E */
                MULT(e1,tp);
                for(int i=0;i<dq;i++) e2[i]=subm(addm(tp[i],mulm(2,e1[i])),e0[i]);
                memcpy(e0,e1,dq*sizeof(int64_t));
                memcpy(e1,e2,dq*sizeof(int64_t));
            }
            #undef MULT
        }
        fprintf(stderr,"prime %d/%d done\n",pi+1,NP);
    }
    for(int m=2;m<=N;m++) for(int n=m;n<=N;n++){
        printf("W %d %d %d %d\n",m,n,wit[m][n],nzc[m][n]);
        if(!wit[m][n]) printf("S %d %d %d\n",m,n,nzc[m][n]);
    }
    return 0;
}
