/* Spiral-greedy fill of Z^2: each cell (in spiral order) gets the integer of
   smallest |v| (ties: v>=0 first, i.e. 0,1,-1,2,-2,...) not already used on
   its row, its column, and (mode>=1) its diagonal x-y=k, (mode>=2) its
   anti-diagonal x+y=k.  Usage: greedy R mode out.bin
   Writes (2R+1)^2 int64 values, row-major with index [y+R][x+R]. Also prints
   max|f| per ring to stdout. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int VOFF;
#define VSZ (2*VOFF+1)
static unsigned char *used; /* lines x values */
static int nlines;
static inline unsigned char *U(int line){ return used + (size_t)line*VSZ; }
int main(int argc,char**argv){
  int R=atoi(argv[1]), mode=atoi(argv[2]); const char*out=argv[3];
  VOFF=2*R+200; int W=2*R+1; int rows0=0, cols0=W, diag0=2*W, anti0=2*W+2*W; /* diag idx x-y+2R, anti x+y+2R */
  nlines=2*W+(mode>=1?2*W:0)+(mode>=2?2*W:0);
  used=calloc((size_t)nlines*VSZ,1);
  long long *f=malloc(sizeof(long long)*W*W);
  for(int r=0;r<=R;r++){
    int n= r==0?1:8*r; int maxabs=0;
    for(int i=0;i<n;i++){
      int x,y;
      if(r==0){x=0;y=0;}
      else{ int s=i/(2*r), t=i%(2*r);
        if(s==0){x=r;y=-r+1+t;} else if(s==1){x=r-1-t;y=r;}
        else if(s==2){x=-r;y=r-1-t;} else {x=-r+1+t;y=-r;} }
      unsigned char *L[4]; int nl=0;
      L[nl++]=U(rows0+y+R); L[nl++]=U(cols0+x+R);
      if(mode>=1) L[nl++]=U(diag0+x-y+2*R);
      if(mode>=2) L[nl++]=U(anti0+x+y+2*R);
      int v=0;
      for(int a=0;;a++){
        int cand[2]={a,-a}; int found=0;
        for(int c=0;c<(a?2:1);c++){ int ok=1; int id=cand[c]+VOFF;
          for(int j=0;j<nl;j++) if(L[j][id]){ok=0;break;}
          if(ok){v=cand[c];found=1;break;} }
        if(found)break;
        if(a>=VOFF-1){fprintf(stderr,"overflow\n");return 1;}
      }
      for(int j=0;j<nl;j++) L[j][v+VOFF]=1;
      f[(size_t)(y+R)*W+(x+R)]=v; if(abs(v)>maxabs)maxabs=abs(v);
    }
    printf("%d %d\n",r,maxabs);
  }
  FILE*fp=fopen(out,"wb"); fwrite(f,sizeof(long long),(size_t)W*W,fp); fclose(fp);
  return 0;
}
