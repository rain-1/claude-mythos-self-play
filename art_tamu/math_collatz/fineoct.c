// counts of basin labels in B bins of log2 n for odd n in one octave [2^k, 2^(k+1)), k<=30
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
int main(int argc,char**argv){
  int k=atoi(argv[1]); int B=atoi(argv[2]); FILE*f=fopen("basin.u8","rb");
  long lo=(1L<<k)/2, hi=(1L<<(k+1))/2;
  uint32_t *cnt=calloc((size_t)B*4,4); size_t CH=1<<24; uint8_t*buf=malloc(CH);
  fseek(f,lo,SEEK_SET);
  for(long s=lo;s<hi;s+=CH){ size_t r=fread(buf,1,(hi-s<(long)CH)?hi-s:CH,f);
    for(size_t j=0;j<r;j++){ double x=log2(2.0*(s+j)+1)-k; int b=(int)(x*B); if(b>=B)b=B-1; cnt[(size_t)b*4+buf[j]]++; } }
  FILE*o=fopen(argv[3],"wb"); fwrite(cnt,4,(size_t)B*4,o); fclose(o);
}
