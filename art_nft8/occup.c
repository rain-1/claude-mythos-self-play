#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
static inline int digitsum(uint64_t n){ int s=0; while(n){s+=n%10;n/=10;} return s; }
int main(void){
    uint64_t a=1, X=100000000000ULL;
    static uint64_t occ[12][9], cop[12][9];
    while (a < X){
        int d=0; uint64_t t=a; while(t>=10){t/=10;d++;}
        int m=(int)(a%9);
        occ[d][m]++;
        if ((a&1) && a%5) cop[d][m]++;
        a += digitsum(a);
    }
    printf("decade coprime10-share lanes 1,2,4,8,7,5\n");
    int L[6]={1,2,4,8,7,5};
    for (int d=4; d<11; d++){
        uint64_t tot=0; for(int i=0;i<6;i++) tot+=cop[d][L[i]];
        if (!tot) continue;
        printf("10^%d:", d);
        for (int i=0;i<6;i++) printf(" %.4f", (double)cop[d][L[i]]/tot);
        printf("\n");
    }
    return 0;
}
