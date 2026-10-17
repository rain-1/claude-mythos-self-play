// density of each basin in bins of log2 n (B bins per octave), octaves 8..31
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
int main(int argc,char**argv){
  int B=atoi(argv[1]); FILE*f=fopen("basin.u8","rb");
  fseek(f,0,SEEK_END); long M=ftell(f); fseek(f,0,SEEK_SET);
  uint8_t*L=malloc(M); fread(L,1,M,f);
  FILE*o=fopen("dens.txt","w");
  for(int k=8;(1L<<(k+1))/2<=M;k++){
    long lo=(1L<<k)/2, hi=(1L<<(k+1))/2;
    long *cnt=calloc(4*B,sizeof(long));
    for(long i=lo;i<hi;i++){ double x=(log2(2.0*i+1)-k)*B; int b=(int)x; if(b>=B)b=B-1; cnt[4*b+L[i]]++; }
    for(int b=0;b<B;b++){ long t=cnt[4*b+1]+cnt[4*b+2]+cnt[4*b+3];
      fprintf(o,"%.8f %.6f %.6f %.6f %ld\n",k+(b+0.5)/B,(double)cnt[4*b+1]/t,(double)cnt[4*b+2]/t,(double)cnt[4*b+3]/t,t);}
    free(cnt);
  }
  fclose(o);
}
