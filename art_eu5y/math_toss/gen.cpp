// gen n : enumerate all (w, T, U): stair w with n corners whose corner set is a direct sum T (+) U,
// with corner 1 in U, T and U both asymmetric (not centrally symmetric), U not an initial segment,
// and (-T)(+)U again a stair w'.  Prints "w w'" per line.  A corner is (index i = x+y, x).
#include <bits/stdc++.h>
using namespace std;
int n,a,b; int X[128]; int need[128]; int Ti[128],Tx[128],nT,Ui[128],Ux[128],nU; long long leaves=0,outp=0;
bool sym(int*I,int*Xs,int k){ int im=I[k-1],xm=Xs[k-1]; // elements sorted by index
  for(int p=0;p<k;p++){int q=k-1-p; if(I[p]+I[q]!=im||Xs[p]+Xs[q]!=xm)return false;} return true;}
void leaf(){
  leaves++;
  // flip T: points (iu - it, xu - xt), translate by (iT_max, xT_max)
  static int Y[128]; for(int k=0;k<n;k++)Y[k]=-1;
  int im=Ti[nT-1],xm=Tx[nT-1];
  for(int p=0;p<nT;p++)for(int q=0;q<nU;q++){int i=Ui[q]-Ti[p]+im,x=Ux[q]-Tx[p]+xm; if(i<0||i>=n||Y[i]!=-1)return; Y[i]=x;}
  if(Y[0]!=0)return; for(int k=1;k<n;k++){int d=Y[k]-Y[k-1]; if(d!=0&&d!=1)return;}
  bool same=true; for(int k=0;k<n;k++) if(Y[k]!=X[k]){same=false;break;} if(same)return;
  char w[128],v[128]; for(int k=1;k<n;k++){w[k-1]=(X[k]==X[k-1])?'1':'0'; v[k-1]=(Y[k]==Y[k-1])?'1':'0';} w[n-1]=v[n-1]=0;
  printf("%s %s\n",w,v); outp++;
}
void rec(int i){
  if(i==n){ if(nT==a&&nU==b) leaf(); return; }
  if(need[i]>=0){ int x=need[i]; if(x!=X[i-1]&&x!=X[i-1]+1)return; X[i]=x; rec(i+1); return; }
  for(int dx=0;dx<2;dx++){ int x=X[i-1]+dx; X[i]=x;
    for(int role=0;role<2;role++){
      if(i==1&&role==0)continue;                 // corner 1 belongs to U
      int *AI=role?Ui:Ti,*AX=role?Ux:Tx,&nA=role?nU:nT; int *BI=role?Ti:Ui,*BX=role?Tx:Ux; int nB=role?nT:nU; int capA=role?b:a;
      if(nA>=capA)continue;
      if(role==0&&nT==1&&nU==b)continue;         // U is an initial segment: ordinary product
      // sums with the other set (element 0 of B is the origin -> the corner itself)
      int touched[128],nt=0; bool ok=true;
      for(int q=1;q<nB&&ok;q++){int k=i+BI[q],xx=x+BX[q]; if(k>=n||need[k]>=0){ok=false;break;} need[k]=xx; touched[nt++]=k;}
      if(ok){ // monotone consistency of all future needs
        int pi=i,px=x; for(int k=i+1;k<n&&ok;k++) if(need[k]>=0){ if(need[k]<px||need[k]>px+(k-pi))ok=false; pi=k;px=need[k]; }
      }
      if(ok){ AI[nA]=i;AX[nA]=x;nA++;
        bool go=true;
        if(nA==capA && sym(AI,AX,nA)) go=false;  // a symmetric factor flips to the reversal
        if(go) rec(i+1);
        nA--; }
      for(int t=0;t<nt;t++)need[touched[t]]=-1;
    }
  }
}
int main(int argc,char**argv){ n=atoi(argv[1]);
  for(a=3;a<=n/3;a++) if(n%a==0){ b=n/a; for(int k=0;k<128;k++)need[k]=-1; X[0]=0; Ti[0]=0;Tx[0]=0;nT=1;Ui[0]=0;Ux[0]=0;nU=1; long long l0=leaves,o0=outp; rec(1);
    fprintf(stderr,"|T|=%d |U|=%d: %lld decompositions, %lld flips to a different stair\n",a,b,leaves-l0,outp-o0); }
}
