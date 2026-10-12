// doors.c — evaluate a Riemann map from boundary data (barycentric Cauchy, close-evaluation safe)
// and reduce disk points into the ideal triangle (1, w, w^2) by reflections.
// mode "map":  doors map bnd.bin pts.bin out.bin   (bnd: N, t[N] complex, wt[N] complex, F[N] complex ; pts: M complex)
//              out: M complex values of F(z)
// mode "tile": doors tile in.bin out.bin  (in: M complex w in unit disk) out: per point 4 floats: centre re, im, depth, |dT^-1/dw at 0|... 
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <complex.h>
#include <math.h>
typedef double complex cd;
static cd *T,*W,*F; static long N;
static cd evalF(cd z){
  cd num=0,den=0;
  for(long j=0;j<N;j++){ cd d=T[j]-z; if(cabs(d)<1e-14) return F[j]; cd q=W[j]/d; num+=F[j]*q; den+=q; }
  return num/den;
}
int main(int argc,char**argv){
  if(!strcmp(argv[1],"map")){
    FILE*f=fopen(argv[2],"rb"); fread(&N,8,1,f);
    T=malloc(N*sizeof(cd));W=malloc(N*sizeof(cd));F=malloc(N*sizeof(cd));
    fread(T,sizeof(cd),N,f);fread(W,sizeof(cd),N,f);fread(F,sizeof(cd),N,f);fclose(f);
    f=fopen(argv[3],"rb"); fseek(f,0,SEEK_END); long M=ftell(f)/sizeof(cd); rewind(f);
    cd*P=malloc(M*sizeof(cd)); fread(P,sizeof(cd),M,f); fclose(f);
    cd*O=malloc(M*sizeof(cd));
    #pragma omp parallel for schedule(dynamic,4096)
    for(long i=0;i<M;i++) O[i]=evalF(P[i]);
    f=fopen(argv[4],"wb"); fwrite(O,sizeof(cd),M,f); fclose(f);
  } else {
    FILE*f=fopen(argv[2],"rb"); fseek(f,0,SEEK_END); long M=ftell(f)/sizeof(cd); rewind(f);
    cd*P=malloc(M*sizeof(cd)); fread(P,sizeof(cd),M,f); fclose(f);
    double*O=malloc(M*8*sizeof(double));
    int maxit=argc>4?atoi(argv[4]):400;
    cd C[3]; double R2=3.0; for(int k=0;k<3;k++) C[k]=-2.0*cexp(I*2*M_PI*k/3.0); // circle through w^{k+1}, w^{k+2}: centre opposite vertex k
    #pragma omp parallel for schedule(dynamic,4096)
    for(long i=0;i<M;i++){
      cd w=P[i]; cd a=1,b=0,c=0,d=1; int p=0; int depth=0; int last=-1;
      for(int it=0;it<maxit;it++){
        int hit=-1; for(int k=0;k<3;k++){ if(k==last) continue; if(cabs(w-C[k])<sqrt(R2)) {hit=k;break;} }
        if(hit<0) break;
        cd cc=C[hit]; // inversion: w' = (cc*conj(w) + R2-|cc|^2)/(conj(w)-conj(cc))
        cd n11=cc, n12=R2-creal(cc*conj(cc)), n21=1, n22=-conj(cc);
        cd wb=conj(w); w=(n11*wb+n12)/(n21*wb+n22);
        // new M = N * conj(M)
        cd a2=n11*conj(a)+n12*conj(c), b2=n11*conj(b)+n12*conj(d), c2=n21*conj(a)+n22*conj(c), d2=n21*conj(b)+n22*conj(d);
        double s=cabs(a2)+cabs(b2)+cabs(c2)+cabs(d2); a=a2/s;b=b2/s;c=c2/s;d=d2/s; p^=1; depth++; last=hit;
      }
      // sub-tile k of the (2,3,inf) subdivision from the reduced point; its centre mapped back by T^{-1}
      double ang=carg(w); if(ang<0) ang+=2*M_PI; int k=(int)floor(ang/(M_PI/3)); if(k>5)k=5;
      cd y=0.30*cexp(I*(M_PI/6+k*M_PI/3));
      cd u=(d*y-b)/(-c*y+a); if(p) u=conj(u);
      cd u0=-b/a; if(p) u0=conj(u0);
      double det=cabs(a*d-b*c); double sc=det/(cabs(a)*cabs(a));
      double*o=O+8*i; o[0]=creal(u);o[1]=cimag(u);o[2]=creal(w);o[3]=cimag(w);o[4]=depth;o[5]=sc;o[6]=p;o[7]=k;
      (void)u0;
    }
    f=fopen(argv[3],"wb"); fwrite(O,sizeof(double),8*M,f); fclose(f);
  }
  return 0;
}
