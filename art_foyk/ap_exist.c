/* First 6-term AP with gap 24 fully inside S (elements allowed between) - the contrast witness. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
static inline int is_bad(uint64_t p){ uint64_t r=p&7; return r==3||r==5; }
int main(){
    uint64_t X=200000000;
    uint8_t* s = malloc(X+1); memset(s,1,X+1); s[0]=0;
    uint32_t sq=(uint32_t)sqrt((double)X)+1;
    uint8_t* isp=malloc(sq+1); memset(isp,1,sq+1); isp[0]=isp[1]=0;
    for(uint32_t i=2;(uint64_t)i*i<=sq;i++) if(isp[i]) for(uint32_t j=i*i;j<=sq;j+=i) isp[j]=0;
    for(uint32_t p=3;p<=sq;p+=2){
        if(!isp[p]||!is_bad(p)) continue;
        for(uint64_t j=p;j<=X;j+=p){ uint64_t n=j; int v=0; do{n/=p;v++;}while(n%p==0); if(v&1) s[j]=0; }
    }
    /* large bad primes: p>sq -> v=1 for multiples p*t, t<=X/p<sq: mark composite-free way:
       for t=1..X/sq, need primes in (sq, X/t]... simpler: for each n, if s[n], strip small primes and check remainder */
    for(uint64_t n=2;n<=X;n++){
        if(!s[n]) continue;
        uint64_t r=n;
        while((r&1)==0) r>>=1;
        for(uint32_t p=3;(uint64_t)p*p<=r;p+=2){ while(r%p==0){ uint64_t q=r/p; if(q%p==0){r=q/p;} else { if(is_bad(p)) s[n]=0; r=q; } if(!s[n])break; } if(!s[n])break; }
        if(s[n] && r>1 && is_bad(r)) s[n]=0;
    }
    fprintf(stderr,"sieve done\n");
    long long count24=0; uint64_t first24=0;
    for(uint64_t n=1;n+120<=X;n++){
        if(s[n]&&s[n+24]&&s[n+48]&&s[n+72]&&s[n+96]&&s[n+120]){
            count24++; if(!first24){ first24=n; }
        }
    }
    printf("6-term g=24 APs in S up to %llu: %lld, first at %llu\n",(unsigned long long)X,count24,(unsigned long long)first24);
    /* also 7,8-term */
    for(int L=7;L<=10;L++){
        uint64_t first=0; long long cnt=0;
        for(uint64_t n=1;n+24*(L-1)<=X;n++){
            int ok=1; for(int i=0;i<L;i++) if(!s[n+24*i]){ok=0;break;}
            if(ok){ cnt++; if(!first) first=n; }
        }
        printf("%d-term g=24 APs: %lld, first at %llu\n",L,cnt,(unsigned long long)first);
    }
    return 0;
}
