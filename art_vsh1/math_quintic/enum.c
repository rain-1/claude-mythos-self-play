// Enumerate collisions of F(a,b)=ab(a+b)(a^2+ab+b^2) over -N<=a<=b<=N, F>0.
// Multi-pass hash partition on low 64 bits of F; full 128-bit F stored.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef unsigned __int128 u128; typedef __int128 i128;
typedef struct { uint64_t lo, hi; int32_t a, b; } __attribute__((packed)) E;
static int cmp(const void*x,const void*y){const E*p=x,*q=y;
 if(p->hi!=q->hi) return p->hi<q->hi?-1:1; if(p->lo!=q->lo) return p->lo<q->lo?-1:1; return 0;}
int main(int argc,char**argv){
 long N=atol(argv[1]); int LP=atoi(argv[2]); long P=1L<<LP; FILE*out=fopen(argv[3],"w");
 const uint64_t C=0x9E3779B97F4A7C15ULL;
 long cap=(long)((double)(N+1)*(N+1)*1.2/P)+1000000; E*buf=malloc(cap*sizeof(E));
 long ngroups=0;
 for(long k=0;k<P;k++){
  long n=0;
  for(long a=-N;a<=N;a++){ for(long b=a;b<=N;b++){
    long s=a+b; if(a==0||b==0||s==0) continue;
    // sign of F = sign(a*b*s)
    int neg=((a<0)^(b<0)^(s<0)); if(neg) continue;
    uint64_t ua=a,ub=b,us=s; uint64_t lo=ua*ub*us*(ua*ua+ua*ub+ub*ub);
    if(((lo*C)>>(64-LP))!=(uint64_t)k) continue;
    i128 F=(i128)a*b; F*=s; F*=(i128)(a*a+a*b+b*b);
    if(n>=cap){fprintf(stderr,"cap\n");exit(1);}
    buf[n].lo=(uint64_t)F; buf[n].hi=(uint64_t)((u128)F>>64); buf[n].a=a; buf[n].b=b; n++;
  }}
  qsort(buf,n,sizeof(E),cmp);
  for(long i=0;i<n;){ long j=i+1; while(j<n&&buf[j].lo==buf[i].lo&&buf[j].hi==buf[i].hi) j++;
    int nontriv=0; if(j-i>1){ long x0=buf[i].a,y0=buf[i].b,z0=-x0-y0; long mx0=x0>y0?x0:y0; mx0=mx0>z0?mx0:z0; long mn0=x0<y0?x0:y0; mn0=mn0<z0?mn0:z0;
      for(long m=i+1;m<j;m++){ long x=buf[m].a,y=buf[m].b,z=-x-y; long mx=x>y?x:y; mx=mx>z?mx:z; long mn=x<y?x:y; mn=mn<z?mn:z; if(mx!=mx0||mn!=mn0) nontriv=1;}}
    if(nontriv){ ngroups++; u128 F=((u128)buf[i].hi<<64)|buf[i].lo;
      // print F as decimal
      char s[64]; int L=0; u128 t=F; do{s[L++]='0'+(int)(t%10); t/=10;}while(t); 
      for(int q=L-1;q>=0;q--) fputc(s[q],out);
      for(long m=i;m<j;m++) fprintf(out," %d %d",buf[m].a,buf[m].b); fputc('\n',out);}
    i=j;}
  fflush(out); fprintf(stderr,"pass %ld n=%ld groups=%ld\n",k,n,ngroups);
 }
 fclose(out); return 0;}
