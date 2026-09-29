// bee_tree.c — the whole prefix tree of bee numbers up to K bits.
// Writes tree_K.bin: for depth j=1..K, 2^(j-1) bytes: 0 = not a bee number,
// else 1+heading (heading 0..5 = direction 30+60h degrees... see below),
// plus for each depth the byte 'died here' mark (value 7) for first-death nodes.
// Bit convention (MO 515588): after the leading 1, bit 1 = turn LEFT, 0 = turn RIGHT.
#include <stdio.h>
#include <stdlib.h>
#define L 128
static unsigned char vis[2*L][2*L];
static unsigned char *lev[40],*ang[40],*dst[40];
#include <math.h>
static double HX[6],HY[6];
static int K;
static void nb(int x,int y,int i,int *nx,int *ny){
  int even=((x+y)&1)==0;
  if(even){ if(i==0){*nx=x+1;*ny=y;} else if(i==1){*nx=x;*ny=y+1;} else {*nx=x-1;*ny=y;} }
  else    { if(i==0){*nx=x-1;*ny=y;} else if(i==1){*nx=x;*ny=y-1;} else {*nx=x+1;*ny=y;} }
}
// heading of step from (x,y) using neighbour index i: angle in degrees/60 - 0.5 -> 0..5
// even: E=-30(h=5), N=90(h=1), W=210(h=3); odd: W=150(h=2), S=270(h=4), E=30(h=0)
static int head(int x,int y,int i){ int even=((x+y)&1)==0;
  if(even) return i==0?5:(i==1?1:3); else return i==0?2:(i==1?4:0); }
static int idx_of(int x,int y,int px,int py){ for(int i=0;i<3;i++){int a,b;nb(x,y,i,&a,&b); if(a==px&&b==py) return i;} return -1; }
static void dfs(int x,int y,int px,int py,int depth,long long n,int h,double rx,double ry){
  long long q=n-(1LL<<(depth-1)); lev[depth][q]=1+h;
  double a=atan2(ry,rx)/(2*M_PI); if(a<0)a+=1; ang[depth][q]=(unsigned char)(a*255.999);
  double d=sqrt(rx*rx+ry*ry)/pow(depth,0.75)/2.5; if(d>1)d=1; dst[depth][q]=(unsigned char)(d*255.999);
  if(depth==K) return;
  int j=idx_of(x,y,px,py);
  for(int t=1;t<=2;t++){ // t=1 -> right turn (bit 0), t=2 -> left turn (bit 1)
    int a,b; nb(x,y,(j+t)%3,&a,&b);
    long long m=2*n+(t==2);
    if(vis[a+L][b+L]){ lev[depth+1][m-(1LL<<depth)]=7; continue; }
    int hh=head(x,y,(j+t)%3); vis[a+L][b+L]=1; dfs(a,b,x,y,depth+1,m,hh,rx+HX[hh],ry+HY[hh]); vis[a+L][b+L]=0;
  }
}
int main(int argc,char**argv){
  K=atoi(argv[1]);
  for(int h=0;h<6;h++){HX[h]=cos((30+60*h)*M_PI/180);HY[h]=sin((30+60*h)*M_PI/180);}
  for(int j=1;j<=K;j++){lev[j]=calloc(1LL<<(j-1),1);ang[j]=calloc(1LL<<(j-1),1);dst[j]=calloc(1LL<<(j-1),1);}
  vis[L][L]=1; vis[L+1][L]=1;
  dfs(1,0,0,0,1,1,head(0,0,0),HX[head(0,0,0)],HY[head(0,0,0)]);
  char fn[64]; sprintf(fn,"tree_%d.bin",K); FILE*f=fopen(fn,"wb");
  for(int j=1;j<=K;j++) fwrite(lev[j],1,1LL<<(j-1),f);
  fclose(f);
  sprintf(fn,"ang_%d.bin",K); f=fopen(fn,"wb"); for(int j=1;j<=K;j++) fwrite(ang[j],1,1LL<<(j-1),f); fclose(f);
  sprintf(fn,"dst_%d.bin",K); f=fopen(fn,"wb"); for(int j=1;j<=K;j++) fwrite(dst[j],1,1LL<<(j-1),f); fclose(f);
  for(int j=1;j<=K;j++){ long long c=0,d=0; for(long long i=0;i<(1LL<<(j-1));i++){c+=(lev[j][i]>0&&lev[j][i]<7); d+=lev[j][i]==7;} printf("%d %lld dead_here=%lld\n",j,c,d);}
}
