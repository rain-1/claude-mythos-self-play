// totfan.c M GX GY out — histogram of pairs a<b, phi(a)=phi(b), a+b=N<=M
// x = (b-a)/(a+b) in (0,1) -> GX bins ; y = log10 N in [1, log10 M] -> GY bins
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
int main(int argc,char**argv){
  int M=atoi(argv[1]), GX=atoi(argv[2]), GY=atoi(argv[3]);
  int *phi=malloc(sizeof(int)*(M+1));
  for(int i=0;i<=M;i++) phi[i]=i;
  for(int p=2;p<=M;p++) if(phi[p]==p) for(int q=p;q<=M;q+=p) phi[q]-=phi[q]/p;
  int *cnt=calloc(M+2,sizeof(int));
  for(int i=1;i<=M;i++) cnt[phi[i]+1]++;
  for(int v=1;v<=M+1;v++) cnt[v]+=cnt[v-1];
  int *pos=malloc(sizeof(int)*(M+2)); for(int v=0;v<=M+1;v++) pos[v]=cnt[v];
  int *arr=malloc(sizeof(int)*M);
  for(int i=1;i<=M;i++) arr[pos[phi[i]]++]=i;
  free(pos); free(phi);
  float *Hh=calloc((size_t)GX*GY,sizeof(float));
  // precompute row index per N
  int *row=malloc(sizeof(int)*(M+1)); double lM=log10((double)M);
  for(int N=1;N<=M;N++){ double y=(log10((double)N)-1.0)/(lM-1.0); int r=(int)(y*GY); row[N]= (r<0||r>=GY)?-1:r; }
  for(int v=1;v<=M;v++){
    int s=cnt[v], e=cnt[v+1];
    for(int x=s;x<e;x++){ int a=arr[x]; for(int y=x+1;y<e;y++){ int b=arr[y]; int N=a+b; if(N>M) break;
      int r=row[N]; if(r<0) continue; int c=(int)((double)(b-a)/N*GX); if(c>=GX) c=GX-1; Hh[(size_t)r*GX+c]+=1.f; } }
  }
  FILE*f=fopen(argv[4],"wb"); fwrite(Hh,4,(size_t)GX*GY,f); fclose(f);
  return 0;
}
