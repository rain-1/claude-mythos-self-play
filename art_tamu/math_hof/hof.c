#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
// usage: hof K  -> compute to N=2^K
int main(int argc,char**argv){
  int K=atoi(argv[1]); int64_t N=1LL<<K;
  int32_t *c=malloc((N+1)*4), *d=malloc((N+1)*4);
  c[1]=c[2]=1; d[1]=d[2]=1;
  for(int64_t n=3;n<=N;n++){ c[n]=c[c[n-1]]+c[n-c[n-1]]; d[n]=n-d[d[n-1]]-d[n-d[n-1]]; }
  // checks
  int64_t viol=0;
  FILE*fe=fopen("equality_2e20.txt","w");
  FILE*fo=fopen("octave_stats.txt","w");
  fprintf(fo,"# k  min_slack(2*s)  argmin_n  n_eq  max2A  max2|B|  minB2  maxB2  count_B>0 count_B<0 count_B=0  maxDeltaStar minDeltaStar\n");
  // profiles: k=10..20, 1024 bins each, 4 arrays (doubles of 2A,2B)
  FILE*fp=fopen("profiles.bin","wb");
  for(int k=0;k<K;k++){
    int64_t lo=1LL<<k, hi=lo<<1; if(hi>N) hi=N+1;
    int64_t mins=INT64_MAX, arg=-1, neq=0, mA=INT64_MIN,mB=0,minB=INT64_MAX,maxB=INT64_MIN,pos=0,neg=0,zer=0; int maxd=-99,mind=99;
    int32_t pmaxA[1024],pminA[1024],pmaxB[1024],pminB[1024];
    for(int i=0;i<1024;i++){pmaxA[i]=pmaxB[i]=INT32_MIN;pminA[i]=pminB[i]=INT32_MAX;}
    for(int64_t n=lo;n<hi;n++){
      int64_t A2=2LL*c[n]-n, B2=2LL*d[n]-n, aB=B2<0?-B2:B2;
      int64_t s=A2-aB;
      if(s<0) viol++;
      if(s<mins){mins=s;arg=n;}
      if(s==0){neq++; if(n<=(1<<20)) fprintf(fe,"%lld %lld %lld\n",(long long)n,(long long)A2,(long long)B2);}
      if(A2>mA)mA=A2; if(aB>mB)mB=aB; if(B2<minB)minB=B2; if(B2>maxB)maxB=B2;
      if(B2>0)pos++; else if(B2<0)neg++; else zer++;
      if(n>1){int dd=d[n]-d[n-1]; if(dd>maxd)maxd=dd; if(dd<mind)mind=dd;}
      if(k>=10&&k<=20&&k<K){ int b=(int)(((n-lo)*1024)>>k); int a=(int)A2, bb=(int)B2;
        if(a>pmaxA[b])pmaxA[b]=a; if(a<pminA[b])pminA[b]=a; if(bb>pmaxB[b])pmaxB[b]=bb; if(bb<pminB[b])pminB[b]=bb; }
    }
    fprintf(fo,"%d %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %d %d\n",k,(long long)mins,(long long)arg,(long long)neq,(long long)mA,(long long)mB,(long long)minB,(long long)maxB,(long long)pos,(long long)neg,(long long)zer,maxd,mind);
    fflush(fo);
    if(k>=10&&k<=20){fwrite(pmaxA,4,1024,fp);fwrite(pminA,4,1024,fp);fwrite(pmaxB,4,1024,fp);fwrite(pminB,4,1024,fp);}
  }
  // n=N itself
  {int64_t n=N; int64_t A2=2LL*c[n]-n,B2=2LL*d[n]-n; fprintf(fo,"# n=N: 2A=%lld 2B=%lld\n",(long long)A2,(long long)B2);}
  fprintf(fo,"# violations: %lld\n",(long long)viol);
  fclose(fo);fclose(fe);fclose(fp);
  FILE*fs=fopen("small.bin","wb"); fwrite(c,4,(1<<16)+1,fs); fwrite(d,4,(1<<16)+1,fs); fclose(fs);
  if(argc>2){FILE*fb=fopen(argv[2],"wb"); int64_t M=atoll(argv[3]); fwrite(c,4,M+1,fb); fwrite(d,4,M+1,fb); fclose(fb);}
  return 0;
}
