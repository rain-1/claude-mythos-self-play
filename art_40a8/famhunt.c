/* Family-curve hunt for x^4+y^4+z^4 = 51 t^4 along genus-3 curves
   A^4 + N B^4 = 51 C^4 with N = u^4+v^4 (y:z = u:v in lowest terms).
   A hit gives 51 = (A/C)^4 + (uB/C)^4 + (vB/C)^4.
   Loops C=1..Cmax, B; r = 51C^4 - N B^4 checked as perfect 4th power via
   two residue bitmaps then exact integer 4th root.  __int128 throughout.
   gcc -O3 -march=native famhunt.c -o famhunt -lm
   ./famhunt Cmax                                                        */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
typedef unsigned __int128 u128;

static uint64_t NLIST[][3] = { /* {N, u, v} primitive u<=v */
    {2,1,1},{17,1,2},{82,1,3},{97,2,3},{257,1,4},{337,3,4},
    {626,1,5},{641,2,5},{706,3,5},{881,4,5},{1297,1,6},{1921,5,6},
    {2402,1,7},{2417,2,7},{2482,3,7},{2657,4,7},{3026,5,7},{3697,6,7},
    {4097,1,8},{4177,3,8},{4721,5,8},{6497,7,8},
    {6562,1,9},{6577,2,9},{6817,4,9},{7186,5,9},{8962,7,9},{10657,8,9}
};
enum { NFAM = sizeof(NLIST)/sizeof(NLIST[0]) };

static uint8_t m16mask[65536/8], m4095mask[4095/8+1];
static inline int bit(uint8_t*m,uint32_t i){ return m[i>>3]>>(i&7)&1; }
static inline void setb(uint8_t*m,uint32_t i){ m[i>>3]|=1u<<(i&7); }

static inline u128 p4(uint64_t x){ u128 s=(u128)x*x; return s*s; }
static inline uint64_t iroot4(u128 v){
    double d = pow((double)v, 0.25);
    uint64_t r = (uint64_t)d;
    while (p4(r+1) <= v) r++;
    while (r>0 && p4(r)>v) r--;
    return r;
}
static uint64_t gcd(uint64_t a,uint64_t b){while(b){uint64_t t=a%b;a=b;b=t;}return a;}

int main(int argc,char**argv){
    uint64_t Cmax = argc>1 ? strtoull(argv[1],0,10) : 200000;
    memset(m16mask,0,sizeof m16mask); memset(m4095mask,0,sizeof m4095mask);
    for (uint32_t x=0;x<65536;x++){ uint64_t r=( (u128)x*x*x*x ) & 65535; setb(m16mask,(uint32_t)r); }
    for (uint32_t x=0;x<4095;x++){ uint64_t r=( (u128)x*x*x*x ) % 4095; setb(m4095mask,(uint32_t)r); }
    for (int f=0; f<NFAM; f++){
        uint64_t N=NLIST[f][0], u=NLIST[f][1], v=NLIST[f][2];
        uint64_t hits=0;
        for (uint64_t C=1; C<=Cmax; C++){
            u128 lhs = (u128)51 * p4(C);
            uint64_t Bmax = iroot4(lhs/N);
            while ((u128)N*p4(Bmax) > lhs) Bmax--;
            for (uint64_t B=1; B<=Bmax; B++){
                u128 r = lhs - (u128)N*p4(B);
                if (!r) continue;
                if (!bit(m16mask,(uint32_t)((uint64_t)r & 65535))) continue;
                if (!bit(m4095mask,(uint32_t)((uint64_t)(r % 4095)))) continue;
                uint64_t A = iroot4(r);
                if (p4(A) == r){
                    uint64_t g = gcd(gcd(A,B),C);
                    hits++;
                    printf("FAMHIT N=%llu (u=%llu,v=%llu) A=%llu B=%llu C=%llu gcd=%llu => "
                           "%llu^4 + %llu^4 + %llu^4 = 51 * %llu^4\n",
                        (unsigned long long)N,(unsigned long long)u,(unsigned long long)v,
                        (unsigned long long)A,(unsigned long long)B,(unsigned long long)C,
                        (unsigned long long)g,
                        (unsigned long long)A,(unsigned long long)(u*B),(unsigned long long)(v*B),
                        (unsigned long long)C);
                    fflush(stdout);
                }
            }
        }
        fprintf(stderr,"family N=%llu done Cmax=%llu hits=%llu\n",
            (unsigned long long)N,(unsigned long long)Cmax,(unsigned long long)hits);
    }
    fprintf(stderr,"FAMHUNT_DONE Cmax=%llu\n",(unsigned long long)Cmax);
    return 0;
}
