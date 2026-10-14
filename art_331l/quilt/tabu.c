// Tabu search for Goethals–Seidel W(4v,k): four ternary circulants with total weight k and zero PAF sum.
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
static unsigned long long s_[2]={0x9E3779B97F4A7C15ULL,0xBF58476D1CE4E5B9ULL};
static inline unsigned long long rnd(void){unsigned long long s1=s_[0],s0=s_[1];s_[0]=s0;s1^=s1<<23;s_[1]=s1^s0^(s1>>17)^(s0>>26);return s_[1]+s0;}
int v,k,h; int X[4][64]; long P[64]; long tabu[4][64];
void fullP(void){for(int s=1;s<=h;s++){P[s]=0;for(int q=0;q<4;q++)for(int i=0;i<v;i++)P[s]+=X[q][i]*X[q][(i+s)%v];}}
static inline void dP(int q,int i,int a,int b,long*d){for(int s=1;s<=h;s++){int l=X[q][(i-s+v)%v],r=X[q][(i+s)%v];d[s]=(long)(b-a)*(2*s==v?l:(l+r));}}
int main(int argc,char**argv){v=atoi(argv[1]);k=atoi(argv[2]);long seed=atol(argv[3]);int ten=argc>4?atoi(argv[4]):12;long maxit=argc>5?atol(argv[5]):200000;
 s_[0]^=seed*0x9E37ULL+1;s_[1]^=seed*7+3;for(int j=0;j<20;j++)rnd();h=v/2;int zeros=4*v-k;
 for(long rs=0;;rs++){
  for(int q=0;q<4;q++)for(int i=0;i<v;i++){X[q][i]=(rnd()&1)?1:-1;tabu[q][i]=0;}
  for(int z=0;z<zeros;){int q=rnd()%4,i=rnd()%v;if(X[q][i]){X[q][i]=0;z++;}}
  fullP(); long best=1L<<60;
  for(long it=1;it<=maxit;it++){
   long c=0;for(int s=1;s<=h;s++)c+=P[s]*P[s];
   if(c==0){printf("FOUND v=%d k=%d rs=%ld it=%ld\n",v,k,rs,it);for(int q=0;q<4;q++){for(int i=0;i<v;i++)putchar(X[q][i]>0?'+':X[q][i]<0?'-':'0');putchar('\n');}return 0;}
   if(c<best)best=c;
   long bc=1L<<60;int bq1=-1,bi1=0,bq2=-1,bi2=0,bb2=0,nties=0; long d1[64],d2[64];
   // flips
   for(int q=0;q<4;q++)for(int i=0;i<v;i++){int a=X[q][i];if(!a||tabu[q][i]>it)continue;dP(q,i,a,-a,d1);long nc=0;for(int s=1;s<=h;s++){long p=P[s]+d1[s];nc+=p*p;}
     if(nc<bc||(nc==bc&&rnd()%(++nties)==0)){if(nc<bc)nties=1;bc=nc;bq1=q;bi1=i;bq2=-1;}}
   // zero moves: nonzero (q1,i1) -> 0, zero (q2,i2) -> ±1   (q1!=q2 for exact incremental; same q handled exactly)
   for(int q2=0;q2<4;q2++)for(int i2=0;i2<v;i2++){if(X[q2][i2]||tabu[q2][i2]>it)continue;
    for(int b=-1;b<=1;b+=2){ dP(q2,i2,0,b,d2);
     for(int q1=0;q1<4;q1++)for(int i1=0;i1<v;i1++){int a=X[q1][i1];if(!a||tabu[q1][i1]>it)continue;
      long nc=0;
      if(q1!=q2){dP(q1,i1,a,0,d1);for(int s=1;s<=h;s++){long p=P[s]+d1[s]+d2[s];nc+=p*p;}}
      else{X[q2][i2]=b;dP(q1,i1,a,0,d1);X[q2][i2]=0;for(int s=1;s<=h;s++){long p=P[s]+d1[s]+d2[s];nc+=p*p;}}
      if(nc<bc||(nc==bc&&rnd()%(++nties)==0)){if(nc<bc)nties=1;bc=nc;bq1=q1;bi1=i1;bq2=q2;bi2=i2;bb2=b;}}}}
   if(bq1<0)continue;
   if(bq2<0){X[bq1][bi1]=-X[bq1][bi1];tabu[bq1][bi1]=it+ten+rnd()%5;}
   else{X[bq2][bi2]=bb2;X[bq1][bi1]=0;tabu[bq1][bi1]=it+ten+rnd()%5;tabu[bq2][bi2]=it+ten+rnd()%5;}
   fullP();
  }
  fprintf(stderr,"rs %ld best %ld\n",rs,best);
 }}
