// harvest zero-sum 8-subsets: keep quads with sum mod M in [0,D) ("low") or (M-D,M) ("high"), match low+high == M
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <omp.h>
#define N 629
static const uint64_t M=1179926954263ULL;static uint64_t r[N];
typedef struct{uint64_t s;uint64_t id;}Q;
static int cmp(const void*a,const void*b){uint64_t x=((Q*)a)->s,y=((Q*)b)->s;return x<y?-1:x>y;}
int main(int argc,char**argv){double frac=atof(argv[1]);uint64_t D=(uint64_t)(frac*M);
 FILE*f=fopen("res.txt","r");for(int i=0;i<N;i++)if(fscanf(f,"%lu",&r[i])!=1)return 1;fclose(f);
 size_t cap=(size_t)(6.4e9*frac*1.15)+1000000;Q*lo=malloc(cap*sizeof(Q)),*hi=malloc(cap*sizeof(Q));size_t nl=0,nh=0;
 #pragma omp parallel
 {size_t bc=1<<16;Q*bl=malloc(bc*sizeof(Q)),*bh=malloc(bc*sizeof(Q));size_t kl=0,kh=0;
  #pragma omp for schedule(dynamic,1)
  for(int a=0;a<N;a++)for(int b=a+1;b<N;b++){uint64_t sab=r[a]+r[b];for(int c=b+1;c<N;c++){uint64_t sabc=sab+r[c];for(int d=c+1;d<N;d++){
    uint64_t s=(sabc+r[d])%M;uint64_t id=(uint64_t)a|((uint64_t)b<<10)|((uint64_t)c<<20)|((uint64_t)d<<30);
    if(s<D){bl[kl].s=s;bl[kl].id=id;if(++kl==bc){size_t p;
      #pragma omp atomic capture
      {p=nl;nl+=kl;}
      for(size_t i=0;i<kl;i++)lo[p+i]=bl[i];kl=0;}}
    else if(s>M-D){bh[kh].s=M-s;bh[kh].id=id;if(++kh==bc){size_t p;
      #pragma omp atomic capture
      {p=nh;nh+=kh;}
      for(size_t i=0;i<kh;i++)hi[p+i]=bh[i];kh=0;}}
  }}}
  size_t p;
  #pragma omp atomic capture
  {p=nl;nl+=kl;}
  for(size_t i=0;i<kl;i++)lo[p+i]=bl[i];
  #pragma omp atomic capture
  {p=nh;nh+=kh;}
  for(size_t i=0;i<kh;i++)hi[p+i]=bh[i];}
 fprintf(stderr,"lo %zu hi %zu\n",nl,nh);
 qsort(lo,nl,sizeof(Q),cmp);qsort(hi,nh,sizeof(Q),cmp);
 FILE*o=fopen("sets8.txt","w");size_t i=0,j=0;long c=0;
 while(i<nl&&j<nh){if(lo[i].s<hi[j].s)i++;else if(lo[i].s>hi[j].s)j++;else{size_t i2=i,j2=j;while(i2<nl&&lo[i2].s==lo[i].s)i2++;while(j2<nh&&hi[j2].s==hi[j].s)j2++;
   for(size_t x=i;x<i2;x++)for(size_t y=j;y<j2;y++){int e[8];for(int k=0;k<4;k++){e[k]=(lo[x].id>>(10*k))&1023;e[4+k]=(hi[y].id>>(10*k))&1023;}
     int ok=1;for(int u=0;u<4;u++)for(int v=4;v<8;v++)if(e[u]==e[v])ok=0;
     if(ok){for(int u=0;u<8;u++)for(int v=u+1;v<8;v++)if(e[v]<e[u]){int t=e[u];e[u]=e[v];e[v]=t;}
       fprintf(o,"8");for(int u=0;u<8;u++)fprintf(o," %d",e[u]);fprintf(o,"\n");c++;}}
   i=i2;j=j2;}}
 fclose(o);fprintf(stderr,"found %ld (with duplicates)\n",c);}
