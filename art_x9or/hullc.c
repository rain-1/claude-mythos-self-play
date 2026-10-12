// hullc: R^{1/3} E_t[P(RK)-P(conv(RK ∩ (Z^2+t)))] for an ellipse K(a,b,theta), stratified t grid m x m.
// usage: hullc a b theta R m seed  -> prints mean, stderr of the normalised deficit (without the kappa factor), and mean vertex count
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
typedef struct {double x,y;} P2;
static int cmp(const void*a,const void*b){const P2*p=a,*q=b; if(p->x!=q->x) return p->x<q->x?-1:1; return p->y<q->y?-1:(p->y>q->y);}
static double cross(P2 o,P2 a,P2 b){return (a.x-o.x)*(b.y-o.y)-(a.y-o.y)*(b.x-o.x);}
int main(int argc,char**argv){
  double a=atof(argv[1]),b=atof(argv[2]),th=atof(argv[3]),R=atof(argv[4]); int m=atoi(argv[5]); unsigned seed=atoi(argv[6]);
  double Pexact=atof(argv[7]);
  double c=cos(th),s=sin(th);
  double A11=c*c/(a*a)+s*s/(b*b), A12=c*s*(1/(a*a)-1/(b*b)), A22=s*s/(a*a)+c*c/(b*b);
  long cap=(long)(8*R*(a>b?a:b))+64; P2*pts=malloc(cap*sizeof(P2)); P2*H=malloc(cap*sizeof(P2));
  srand(seed); double ox=rand()/(double)RAND_MAX/m, oy=rand()/(double)RAND_MAX/m;
  double sum=0,sum2=0,vsum=0; int n=0;
  for(int i=0;i<m;i++) for(int j=0;j<m;j++){
    double tx=fmod((i+0.5)/m+ox,1.0), ty=fmod((j+0.5)/m+oy,1.0);
    long np=0;
    for(int ax=0;ax<2;ax++){
      double B11=ax?A22:A11, B22=ax?A11:A22, ux=ax?ty:tx, uy=ax?tx:ty;
      double xm=R/sqrt(B11-A12*A12/B22);
      for(double x=ceil(-xm-ux)+ux; x<=xm; x+=1.0){
        double disc=A12*A12*x*x-B22*(B11*x*x-R*R); if(disc<0) continue; disc=sqrt(disc);
        double y1=(-A12*x-disc)/B22, y2=(-A12*x+disc)/B22;
        double lo=ceil(y1-uy)+uy, hi=floor(y2-uy)+uy; if(lo>hi) continue;
        if(ax){pts[np++]=(P2){lo,x}; pts[np++]=(P2){hi,x};} else {pts[np++]=(P2){x,lo}; pts[np++]=(P2){x,hi};}
      }
    }
    qsort(pts,np,sizeof(P2),cmp);
    long k=0;
    for(long q=0;q<np;q++){ while(k>=2&&cross(H[k-2],H[k-1],pts[q])<=1e-9) k--; H[k++]=pts[q]; }
    for(long q=np-2,t=k+1;q>=0;q--){ while(k>=t&&cross(H[k-2],H[k-1],pts[q])<=1e-9) k--; H[k++]=pts[q]; }
    k--; double per=0; for(long q=0;q<k;q++){ double dx=H[q+1].x-H[q].x, dy=H[q+1].y-H[q].y; per+=sqrt(dx*dx+dy*dy); }
    double D=(R*Pexact-per)*cbrt(R); sum+=D; sum2+=D*D; vsum+=k; n++;
  }
  double mu=sum/n, sd=sqrt((sum2/n-mu*mu)/n);
  printf("%.6f %.6f %.1f\n",mu,sd,vsum/n); if(getenv("DBG")){for(long q=0;q<12;q++) fprintf(stderr,"%g %g\n",H[q].x,H[q].y);}
  return 0;
}
