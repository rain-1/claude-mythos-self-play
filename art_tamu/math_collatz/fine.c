// counts of each basin label in bins of log2 n, B bins per octave, octaves 1..31 (chunked read)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
int main(int argc,char**argv){
  int B=atoi(argv[1]); FILE*f=fopen("basin.u8","rb");
  long M=1L<<31; int K=32;
  uint32_t *cnt=calloc((size_t)K*B*4,sizeof(uint32_t));
  size_t CH=1<<24; uint8_t*buf=malloc(CH);
  for(long s=0;s<M;s+=CH){
    size_t r=fread(buf,1,CH,f);
    for(size_t j=0;j<r;j++){ long i=s+j; double n=2.0*i+1; double x=log2(n);
      int k=(int)x; int b=(int)((x-k)*B); if(b>=B)b=B-1; cnt[((size_t)k*B+b)*4+buf[j]]++; }
  }
  FILE*o=fopen(argv[2],"wb"); fwrite(cnt,sizeof(uint32_t),(size_t)K*B*4,o); fclose(o);
}
