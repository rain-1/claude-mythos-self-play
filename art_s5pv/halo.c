// halo.c — Monte Carlo ice-crystal halo simulator (hexagonal prisms, Fresnel, dispersion).
// Output: XYZ radiance maps in (1) a stereographic camera and (2) an equirectangular sky.
// usage: halo out_prefix nrays sun_el_deg pop_spec cam_az cam_el cam_W cam_H cam_scale eq_W seed
//   pop_spec: comma list "type:weight:ratio:tilt" type R=random P=plate C=column(horizontal) Y=parry ; ratio = c/a half-height over radius
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <omp.h>
typedef struct{double x,y,z;}V;
static inline V v(double x,double y,double z){V r={x,y,z};return r;}
static inline V add(V a,V b){return v(a.x+b.x,a.y+b.y,a.z+b.z);}
static inline V sub(V a,V b){return v(a.x-b.x,a.y-b.y,a.z-b.z);}
static inline V mul(V a,double s){return v(a.x*s,a.y*s,a.z*s);}
static inline double dot(V a,V b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static inline V cross(V a,V b){return v(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);}
static inline V nrm(V a){return mul(a,1.0/sqrt(dot(a,a)));}
typedef struct{uint64_t s;}RNG;
static inline uint64_t nx(RNG*r){uint64_t z=(r->s+=0x9e3779b97f4a7c15ULL);z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31);}
static inline double U(RNG*r){return (nx(r)>>11)*(1.0/9007199254740992.0);}
static inline double G(RNG*r){double u=U(r)+1e-300,w=U(r);return sqrt(-2*log(u))*cos(2*M_PI*w);}
// CIE 1931 multi-lobe fit (Wyman, Sloan, Shirley 2013)
static double g1(double x,double m,double s1,double s2){double t=(x-m)/(x<m?s1:s2);return exp(-0.5*t*t);}
static void cmf(double l,double*X,double*Y,double*Z){
 *X=1.056*g1(l,599.8,37.9,31.0)+0.362*g1(l,442.0,16.0,26.7)-0.065*g1(l,501.1,20.4,26.2);
 *Y=0.821*g1(l,568.8,46.9,40.5)+0.286*g1(l,530.9,16.3,31.1);
 *Z=1.217*g1(l,437.0,11.8,36.0)+0.681*g1(l,459.0,26.0,13.8);}
static inline double nice(double l){return 1.3008+2969.0/(l*l);}
typedef struct{char t;double w,ratio,tilt;}Pop;
static Pop pops[8];static int npop;static double wsum;
// random rotation matrix columns (crystal->world)
static void rot_random(RNG*r,V*a,V*b,V*c){ // uniform quaternion
 double u1=U(r),u2=U(r),u3=U(r);double q0=sqrt(1-u1)*sin(2*M_PI*u2),q1=sqrt(1-u1)*cos(2*M_PI*u2),q2=sqrt(u1)*sin(2*M_PI*u3),q3=sqrt(u1)*cos(2*M_PI*u3);
 *a=v(1-2*(q2*q2+q3*q3),2*(q1*q2+q0*q3),2*(q1*q3-q0*q2));
 *b=v(2*(q1*q2-q0*q3),1-2*(q1*q1+q3*q3),2*(q2*q3+q0*q1));
 *c=v(2*(q1*q3+q0*q2),2*(q2*q3-q0*q1),1-2*(q1*q1+q2*q2));}
static V tiltv(RNG*r,V axis,double sig){ // small gaussian tilt of a unit vector
 V t1=nrm(cross(axis,fabs(axis.z)<0.9?v(0,0,1):v(1,0,0)));V t2=cross(axis,t1);
 double a=G(r)*sig,b=G(r)*sig;return nrm(add(axis,add(mul(t1,a),mul(t2,b))));}
static void orient(RNG*r,Pop*p,V*ex,V*ey,V*ez){
 double sig=p->tilt*M_PI/180;
 if(p->t=='R'){rot_random(r,ex,ey,ez);return;}
 if(p->t=='P'){V c=tiltv(r,v(0,0,1),sig);V t=nrm(cross(c,v(1,0,0)));V s=cross(c,t);double ph=2*M_PI*U(r);
   *ez=c;*ex=add(mul(t,cos(ph)),mul(s,sin(ph)));*ey=cross(*ez,*ex);return;}
 if(p->t=='C'||p->t=='Y'){double az=2*M_PI*U(r);V c=tiltv(r,v(cos(az),sin(az),0),sig);
   V up=v(0,0,1);V t=nrm(sub(up,mul(c,dot(up,c))));V s=cross(c,t);double ph;
   if(p->t=='C')ph=2*M_PI*U(r); else ph=G(r)*sig + (M_PI/2); // Parry: a side-face normal (ex) horizontal => face normal at 90 deg from up
   *ez=c;*ex=add(mul(t,cos(ph)),mul(s,sin(ph)));*ey=cross(*ez,*ex);return;}
}
// fresnel unpolarised
static double fres(double ci,double n1,double n2,double*ct){double s=n1/n2;double st2=s*s*(1-ci*ci);if(st2>=1){*ct=0;return 1;}
 double c2=sqrt(1-st2);*ct=c2;double rs=(n1*ci-n2*c2)/(n1*ci+n2*c2),rp=(n2*ci-n1*c2)/(n2*ci+n1*c2);return 0.5*(rs*rs+rp*rp);}
int main(int argc,char**argv){
 if(argc<12){fprintf(stderr,"args\n");return 1;}
 char*pre=argv[1];long nr=atol(argv[2]);double sel=atof(argv[3])*M_PI/180;
 char spec[512];strcpy(spec,argv[4]);
 double caz=atof(argv[5])*M_PI/180,cel=atof(argv[6])*M_PI/180;int W=atoi(argv[7]),H=atoi(argv[8]);double sc=atof(argv[9]);int EW=atoi(argv[10]);int EH=EW/2;uint64_t seed=atoll(argv[11]);
 for(char*tok=strtok(spec,",");tok;tok=strtok(NULL,",")){Pop p;sscanf(tok,"%c:%lf:%lf:%lf",&p.t,&p.w,&p.ratio,&p.tilt);pops[npop++]=p;wsum+=p.w;}
 V sun=v(cos(sel),0,sin(sel)); // sun at azimuth 0 (x axis); z up
 // camera basis: forward f at (caz,cel)
 V f=v(cos(cel)*cos(caz),cos(cel)*sin(caz),sin(cel));V rt=nrm(cross(f,v(0,0,1)));V up=cross(rt,f);
 float*cam=calloc((size_t)W*H*3,4);float*eq=calloc((size_t)EW*EH*3,4);
 FILE*spk=0;char fn[512];sprintf(fn,"%s_sparks.bin",pre);spk=fopen(fn,"wb");long nsp=0;
 long hits=0;
 #pragma omp parallel reduction(+:hits)
 {int tid=omp_get_thread_num();RNG r={seed*1000003ULL+tid*7919ULL+1};
  float*lc=calloc((size_t)W*H*3,4);float*le=calloc((size_t)EW*EH*3,4);
  #pragma omp for schedule(static)
  for(long i=0;i<nr;i++){
   // population
   double pw=U(&r)*wsum;int pi=0;while(pi<npop-1&&pw>pops[pi].w){pw-=pops[pi].w;pi++;}Pop*p=&pops[pi];
   V ex,ey,ez;orient(&r,p,&ex,&ey,&ez);
   // incoming direction: from a point on the sun disk (0.266 deg radius)
   V s=sun;{V t1=nrm(cross(s,v(0,0,1)));V t2=cross(t1,s);double rr=sqrt(U(&r))*0.00465,th=2*M_PI*U(&r);s=nrm(add(s,add(mul(t1,rr*cos(th)),mul(t2,rr*sin(th)))));}
   V d=mul(s,-1);
   // planes in world: normals and offsets, crystal radius 1 (apothem 1), half-height = ratio
   V nn[8];double dd[8];
   for(int k=0;k<6;k++){double a=k*M_PI/3;nn[k]=add(mul(ex,cos(a)),mul(ey,sin(a)));dd[k]=1;}
   nn[6]=ez;dd[6]=p->ratio;nn[7]=mul(ez,-1);dd[7]=p->ratio;
   // origin: random point on disk perpendicular to d, radius R covering crystal
   double R=sqrt(4.0/3+p->ratio*p->ratio)+1e-3;V t1=nrm(cross(d,fabs(d.z)<0.9?v(0,0,1):v(1,0,0)));V t2=cross(d,t1);
   double rr=R*sqrt(U(&r)),th=2*M_PI*U(&r);V o=add(mul(d,-10),add(mul(t1,rr*cos(th)),mul(t2,rr*sin(th))));
   double te=-1e30,tx=1e30;int fe=-1;
   for(int k=0;k<8;k++){double dn=dot(nn[k],d),num=dd[k]-dot(nn[k],o);if(dn<0){double t=num/dn;if(t>te){te=t;fe=k;}}else if(dn>0){double t=num/dn;if(t<tx)tx=t;}else if(num<0){te=1e30;}}
   if(!(te<tx))continue;
   hits++;
   double lam=400+300*U(&r);double n=nice(lam);
   V pnt=add(o,mul(d,te));V N=nn[fe];double ci=-dot(d,N),ct;double Rf=fres(ci,1,n,&ct);V out;int ok=0;
   if(U(&r)<Rf){out=add(d,mul(N,2*ci));ok=1;}
   else{ d=nrm(add(mul(d,1/n),mul(N,ci/n-ct)));
     for(int b=0;b<10;b++){ double tb=1e30;int fb=-1;
       for(int k=0;k<8;k++){double dn=dot(nn[k],d);if(dn>1e-12){double t=(dd[k]-dot(nn[k],pnt))/dn;if(t<tb){tb=t;fb=k;}}}
       if(fb<0)break;pnt=add(pnt,mul(d,tb));V M=nn[fb];double c1=dot(d,M);double c2;double R2=fres(c1,n,1,&c2);
       if(U(&r)<R2){d=sub(d,mul(M,2*c1));}
       else{out=nrm(add(mul(d,n),mul(M,c2-n*c1)));ok=1;break;}
     }}
   if(!ok)continue;
   V sky=mul(out,-1); // where the observer sees it
   double X,Y,Z;cmf(lam,&X,&Y,&Z);
   // equirect
   {double az=atan2(sky.y,sky.x),el=asin(fmax(-1,fmin(1,sky.z)));int ix=(int)((az/(2*M_PI)+0.5)*EW),iy=(int)((0.5-el/M_PI)*EH);if(ix>=EW)ix=EW-1;if(iy>=EH)iy=EH-1;if(ix<0)ix=0;if(iy<0)iy=0;
    float*q=le+((size_t)iy*EW+ix)*3;q[0]+=X;q[1]+=Y;q[2]+=Z;}
   // stereographic camera
   {double cz=dot(sky,f);if(cz>-0.95){double k=sc*2/(1+cz);double px=W*0.5+k*dot(sky,rt)*W*0.5,py=H*0.5-k*dot(sky,up)*W*0.5;
     if(px>=0&&px<W&&py>=0&&py<H){int ix=(int)px,iy=(int)py;float*q=lc+((size_t)iy*W+ix)*3;q[0]+=X;q[1]+=Y;q[2]+=Z;
       if((nx(&r)&0xfffff)<4){
       #pragma omp critical
       {float rec[4]={(float)px,(float)py,(float)lam,(float)pi};fwrite(rec,4,4,spk);nsp++;}}}}}
  }
  #pragma omp critical
  {for(size_t j=0;j<(size_t)W*H*3;j++)cam[j]+=lc[j];for(size_t j=0;j<(size_t)EW*EH*3;j++)eq[j]+=le[j];}
  free(lc);free(le);}
 fclose(spk);
 sprintf(fn,"%s_cam.f32",pre);FILE*o=fopen(fn,"wb");fwrite(cam,4,(size_t)W*H*3,o);fclose(o);
 sprintf(fn,"%s_eq.f32",pre);o=fopen(fn,"wb");fwrite(eq,4,(size_t)EW*EH*3,o);fclose(o);
 fprintf(stderr,"rays %ld hits %ld sparks %ld\n",nr,hits,nsp);
 return 0;}
