// Goethals–Seidel search for W(4v,k): four ternary circulants A,B,C,D of length v,
// total weight k, with sum of periodic autocorrelations = 0 at every nonzero shift.
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
static unsigned long long s_[2]={0x9E3779B97F4A7C15ULL,0xBF58476D1CE4E5B9ULL};
static inline unsigned long long rnd(void){unsigned long long s1=s_[0],s0=s_[1];s_[0]=s0;s1^=s1<<23;s_[1]=s1^s0^(s1>>17)^(s0>>26);return s_[1]+s0;}
static inline double ur(void){return (rnd()>>11)*(1.0/9007199254740992.0);}
int v,k; int X[4][128]; long P[128];
long cost(void){long c=0;for(int s=1;s<=v/2;s++)c+=P[s]*P[s];return c;}
void fullP(void){for(int s=0;s<v;s++){P[s]=0;for(int q=0;q<4;q++)for(int i=0;i<v;i++)P[s]+=X[q][i]*X[q][(i+s)%v];}}
// delta of P[s] when X[q][i] changes from a to b
static inline void dP(int q,int i,int a,int b,long*d){for(int s=1;s<=v/2;s++){int l=X[q][(i-s+v)%v],r=X[q][(i+s)%v];
 long dd=(long)(b-a)*(l+r); if(2*s==v) dd=(long)(b-a)*l; d[s]=dd;}}
int main(int argc,char**argv){v=atoi(argv[1]);k=atoi(argv[2]);long seed=argc>3?atol(argv[3]):time(0);s_[0]^=seed*0x1234567ULL;s_[1]^=seed;
 int zeros=4*v-k; double T0=argc>4?atof(argv[4]):3.0;
 for(long restart=0;;restart++){
  for(int q=0;q<4;q++)for(int i=0;i<v;i++)X[q][i]=(rnd()&1)?1:-1;
  for(int z=0;z<zeros;){int q=rnd()%4,i=rnd()%v;if(X[q][i]){X[q][i]=0;z++;}}
  fullP(); long c=cost(); double T=T0; long d1[128],d2[128];
  for(long it=0;it<40000000;it++){
   if(it%20000==0)T*=0.985; if(T<0.05)T=T0*0.3;
   int mv=rnd()%3; int q1=rnd()%4,i1=rnd()%v,a1=X[q1][i1],b1;
   int q2=-1,i2=-1,a2=0,b2=0;
   if(mv<2 || zeros==0){ if(!a1) continue; b1=-a1; dP(q1,i1,a1,b1,d1);
     long nc=0; for(int s=1;s<=v/2;s++){long p=P[s]+d1[s];nc+=p*p;}
     if(nc<=c || ur()<exp((c-nc)/T)){ X[q1][i1]=b1; for(int s=1;s<=v/2;s++)P[s]+=d1[s]; c=nc; }
   } else { // move a zero: (q1,i1) nonzero -> 0, (q2,i2) zero -> ±1
     if(!a1) continue; do{q2=rnd()%4;i2=rnd()%v;}while(X[q2][i2]!=0); b2=(rnd()&1)?1:-1;
     dP(q1,i1,a1,0,d1); X[q1][i1]=0; dP(q2,i2,0,b2,d2); X[q1][i1]=a1;
     // correction if same sequence and interacting: just recompute exactly in that case
     long nc=0; X[q1][i1]=0; X[q2][i2]=b2; long Pn[128];
     if(q1==q2){ for(int s=1;s<=v/2;s++){Pn[s]=0;for(int q=0;q<4;q++)for(int i=0;i<v;i++)Pn[s]+=X[q][i]*X[q][(i+s)%v];} }
     else for(int s=1;s<=v/2;s++)Pn[s]=P[s]+d1[s]+d2[s];
     for(int s=1;s<=v/2;s++)nc+=Pn[s]*Pn[s];
     if(nc<=c || ur()<exp((c-nc)/T)){ for(int s=1;s<=v/2;s++)P[s]=Pn[s]; c=nc; }
     else { X[q1][i1]=a1; X[q2][i2]=0; }
   }
   if(c==0){ fullP(); if(cost()!=0){fprintf(stderr,"bug\n");return 1;}
     printf("FOUND v=%d k=%d restart=%ld it=%ld\n",v,k,restart,it);
     for(int q=0;q<4;q++){for(int i=0;i<v;i++)printf("%c",X[q][i]>0?'+':X[q][i]<0?'-':'0');printf("\n");}
     return 0;}
  }
  fprintf(stderr,"restart %ld best c=%ld\n",restart,c);
 }}
