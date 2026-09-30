// totsum.c M — R(N) = #{a<b, a+b=N, phi(a)=phi(b)} for N <= M; prints N with R(N)=0 and stats
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
int main(int argc,char**argv){
  int M=atoi(argv[1]);
  int *phi=malloc(sizeof(int)*(M+1));
  for(int i=0;i<=M;i++) phi[i]=i;
  for(int p=2;p<=M;p++) if(phi[p]==p) for(int q=p;q<=M;q+=p) phi[q]-=phi[q]/p;
  // bucket numbers by phi value (phi <= M)
  int *cnt=calloc(M+2,sizeof(int));
  for(int i=1;i<=M;i++) cnt[phi[i]+1]++;
  for(int v=1;v<=M+1;v++) cnt[v]+=cnt[v-1];
  int *pos=malloc(sizeof(int)*(M+2)); for(int v=0;v<=M+1;v++) pos[v]=cnt[v];
  int *arr=malloc(sizeof(int)*M);
  for(int i=1;i<=M;i++) arr[pos[phi[i]]++]=i;   // ascending within bucket
  uint32_t *R=calloc(M+1,sizeof(uint32_t));
  for(int v=1;v<=M;v++){
    int s=cnt[v], e=cnt[v+1];
    for(int x=s;x<e;x++){ int a=arr[x]; for(int y=x+1;y<e;y++){ int b=arr[y]; if(a+b>M) break; R[a+b]++; } }
  }
  int z=0, last=0;
  for(int N=3;N<=M;N++) if(R[N]==0){ z++; last=N; if(z<=400) printf("%d ",N);} 
  printf("\nzeros %d last %d\n",z,last);
  FILE*f=fopen(argv[2],"wb"); fwrite(R,4,M+1,f); fclose(f);
  return 0;
}
