/* MC predictive test k=15 m=3: inner chamber t=4 deficit. Sample uniform (sigma,tau), tally selected types. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static uint64_t rs = 88172645463325252ULL;
static inline uint64_t rnd(){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
int main(int argc,char**argv){
    int k=15,m=3,N=2*k-m; long long T=atoll(argv[1]);
    int S2s=k-m; /* S2 = k-m..N-1 */
    long long c999=0,c1098=0,c1089=0,c111=0,single=0,tot=0;
    int perm1[64],perm2[64],sig[64],tau[64],pi[64],seen[64],cc[64];
    for(long long it=0;it<T;it++){
        /* random cycle on S1=0..k-1: random perm of 1..k-1 after 0 */
        for(int i=0;i<k;i++) perm1[i]=i;
        for(int i=k-1;i>1;i--){ int j=1+rnd()%i; int t=perm1[i];perm1[i]=perm1[j];perm1[j]=t; }
        for(int i=0;i<N;i++) sig[i]=i;
        for(int i=0;i<k;i++) sig[perm1[i]]=perm1[(i+1)%k];
        for(int i=0;i<k;i++) perm2[i]=S2s+i;
        for(int i=k-1;i>1;i--){ int j=1+rnd()%i; int t=perm2[i];perm2[i]=perm2[j];perm2[j]=t; }
        for(int i=0;i<N;i++) tau[i]=i;
        for(int i=0;i<k;i++) tau[perm2[i]]=perm2[(i+1)%k];
        for(int i=0;i<N;i++) pi[i]=sig[tau[i]];
        memset(seen,0,sizeof(int)*N);
        int nc=0;
        for(int s=0;s<N;s++) if(!seen[s]){ int l=0,j=s; while(!seen[j]){seen[j]=1;j=pi[j];l++;} cc[nc++]=l; }
        tot++;
        if(nc==1){ single++; continue; }
        /* sort desc small */
        for(int i=1;i<nc;i++){int v=cc[i],j=i-1;while(j>=0&&cc[j]<v){cc[j+1]=cc[j];j--;}cc[j+1]=v;}
        if(nc==3){
            if(cc[0]==9&&cc[1]==9&&cc[2]==9) c999++;
            else if(cc[0]==10&&cc[1]==9&&cc[2]==8) c1098++;
            else if(cc[0]==10&&cc[1]==10&&cc[2]==7) c1089++;
            else if(cc[0]==11&&cc[1]==11&&cc[2]==5) c111++;
        }
    }
    printf("samples %lld\nsingle %lld  (pred 0.5) obs %.6f\n",tot,single,(double)single/tot);
    /* predictions: q = 2*perms*(bc - t(t+1))/((14*13)^2), denominators 33124 */
    printf("(9,9,9):   obs %.6e  pred(t=4,defic20) %.6e  alt(defic12) %.6e\n",(double)c999/tot, 2.0*1*(81-20)/33124.0, 2.0*1*(81-12)/33124.0);
    printf("(10,9,8):  obs %.6e  pred(t=3,defic12) %.6e  alt(defic20) %.6e\n",(double)c1098/tot, 2.0*6*(72-12)/33124.0, 2.0*6*(72-20)/33124.0);
    printf("(10,10,7): obs %.6e  pred(t=3,defic12) %.6e\n",(double)c1089/tot, 2.0*3*(70-12)/33124.0);
    printf("(11,11,5): obs %.6e  pred(t=2,defic6)  %.6e\n",(double)c111/tot, 2.0*3*(55-6)/33124.0);
    return 0;
}
