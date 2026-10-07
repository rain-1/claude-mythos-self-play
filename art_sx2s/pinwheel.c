// Pinwheel squares (MO 515784): n x n binary matrix, quarter-turn symmetric, read row-major
// MSB first, leading bit 1 (so all four corners are 1). Is the number a perfect square?
// Gray-code walk over free orbits; residues mod several moduli filter; survivors checked exactly.
// usage: pinwheel n part nparts   (also counts pinwheel PRIMES? no: squares only)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
typedef unsigned __int128 u128;
#define NM 9
static const uint32_t MODS[NM]={64*63*65/ (64*63*65) * 4096, 63*65*11, 17*19*23, 29*31*37, 41*43*47, 53*59*61, 67*71*73, 79*83*89, 97*101*103};
static uint8_t *qr[NM];
int n, nb; int orb[80][4]; int osz[80]; int norb=0;
// bit value of cell (i,j): 2^(nb-1 - (i*n+j))
int main(int argc,char**argv){
  n=atoi(argv[1]); int part=argc>2?atoi(argv[2]):0, nparts=argc>3?atoi(argv[3]):1;
  nb=n*n; int seen[400]={0};
  for(int i=0;i<n;i++)for(int j=0;j<n;j++){int c=i*n+j; if(seen[c])continue; int k=0,a=i,b=j;
    do{int cc=a*n+b; if(!seen[cc]){seen[cc]=1; orb[norb][k++]=cc;} int t=a; a=b; b=n-1-t;}while(!(a==i&&b==j));
    osz[norb]=k; norb++;}
  for(int m=0;m<NM;m++){qr[m]=calloc(MODS[m],1); for(uint64_t x=0;x<MODS[m];x++) qr[m][(x*x)%MODS[m]]=1;}
  // orbit values mod each modulus, and exact 128-bit (nb<=128) -- use two u128 halves if nb>128
  static uint32_t ov[80][NM]; static u128 oex[80][2];
  for(int o=0;o<norb;o++){ for(int m=0;m<NM;m++){uint64_t s=0; for(int k=0;k<osz[o];k++){int e=nb-1-orb[o][k]; uint64_t p=1%MODS[m],bse=2; while(e){if(e&1)p=p*bse%MODS[m]; bse=bse*bse%MODS[m]; e>>=1;} s=(s+p)%MODS[m];} ov[o][m]=s;}
    oex[o][0]=oex[o][1]=0; for(int k=0;k<osz[o];k++){int e=nb-1-orb[o][k]; if(e<128) oex[o][0]+=((u128)1)<<e; else oex[o][1]+=((u128)1)<<(e-128);} }
  // forced: orbit of cell 0 (corner) =1. low bits: odd square = 1 mod 8 -> cells nb-2, nb-3 are 0.
  int forced[80]; for(int o=0;o<norb;o++)forced[o]=-1;
  for(int o=0;o<norb;o++)for(int k=0;k<osz[o];k++){int c=orb[o][k]; if(c==0)forced[o]=1; if(c==nb-2||c==nb-3)forced[o]=0;}
  int fr[80],nf=0; uint32_t base[NM]={0}; u128 bex[2]={0,0};
  for(int o=0;o<norb;o++){ if(forced[o]<0) fr[nf++]=o; else if(forced[o]==1){for(int m=0;m<NM;m++)base[m]=(base[m]+ov[o][m])%MODS[m]; bex[0]+=oex[o][0]; bex[1]+=oex[o][1];} }
  fprintf(stderr,"n=%d orbits=%d free=%d\n",n,norb,nf);
  // split on top 'sb' free bits for parallelism
  int sb=0; while((1<<sb)<nparts*64 && sb<nf) sb++;
  long long tested=0, surv=0, found=0;
  {printf("FREE"); for(int f=0;f<nf;f++)printf(" %d",fr[f]); printf("\n");}
  for(uint64_t hi=part; hi<(1ULL<<sb); hi+=nparts){
    uint32_t r[NM]; memcpy(r,base,sizeof r); u128 ex0=bex[0],ex1=bex[1]; int st[80]={0};
    for(int b=0;b<sb;b++) if(hi>>b&1){int o=fr[nf-1-b]; st[o]=1; for(int m=0;m<NM;m++) r[m]=(r[m]+ov[o][m])%MODS[m]; ex0+=oex[o][0]; ex1+=oex[o][1];}
    int lowbits=nf-sb; uint64_t N=1ULL<<lowbits;
    for(uint64_t g=0; g<N; g++){
      if(g){ int b=__builtin_ctzll(g); int o=fr[b]; int s=st[o]^=1;
        for(int m=0;m<NM;m++){ uint32_t v=ov[o][m]; r[m]= s? (r[m]+v>=MODS[m]? r[m]+v-MODS[m]: r[m]+v) : (r[m]>=v? r[m]-v: r[m]+MODS[m]-v);} }
      tested++;
      int ok=1; for(int m=0;m<NM;m++) if(!qr[m][r[m]]){ok=0;break;}
      if(!ok) continue; surv++;
      // exact: rebuild number
      u128 a0=bex[0],a1=bex[1]; for(int o=0;o<norb;o++) if(forced[o]<0 && st[o]){a0+=oex[o][0];a1+=oex[o][1];}
      // only nb<=128 exact check here via long double sqrt + fix
      if(nb<=128){ long double x=sqrtl((long double)a0); u128 s=(u128)x; while(s*s>a0)s--; while((s+1)*(s+1)<=a0)s++;
        if(s*s==a0){found++; printf("SQUARE n=%d: %llx%016llx\n",n,(unsigned long long)(a0>>64),(unsigned long long)a0); fflush(stdout);} }
      else { unsigned long long mk=0; for(int f=0;f<nf;f++) if(st[fr[f]]) mk|=1ULL<<f; printf("SURV %llu\n",mk); }
    }
  }
  fprintf(stderr,"part %d: tested %lld survivors %lld squares %lld\n",part,tested,surv,found);
  return 0;
}
