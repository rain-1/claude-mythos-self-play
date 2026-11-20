// dig.cpp — "Digits on a chessboard" (MO 516966) generalised.
// Board = set of cells of an R x C grid (optionally a torus); base b; every ordered pair of
// digits must appear exactly once on the edges (read left->right and top->down).
// usage: dig R C b mode seed maxiter   mode: rect | holed (centre 2x2 removed) | torus
//        add 'm' suffix (rectm / holedm / torusm) to force a left-right mirror symmetry with
//        digit involution sigma(d) = d + b/2 mod b.
// Simulated annealing on cost = #pairs missing. Prints the grid when cost = 0.
#include <bits/stdc++.h>
using namespace std;
int R,C,b; bool torus=false,mirror=false; vector<int> alive;
int main(int argc,char**argv){
  if(argc<7){fprintf(stderr,"usage\n");return 1;}
  R=atoi(argv[1]);C=atoi(argv[2]);b=atoi(argv[3]);string mode=argv[4];
  unsigned long long seed=atoll(argv[5]);long long maxit=atoll(argv[6]);
  if(mode.back()=='m'){mirror=true;mode.pop_back();}
  torus=(mode=="torus");
  alive.assign(R*C,1);
  if(mode.substr(0,4)=="hole"){int h= mode=="holed"?2:atoi(mode.c_str()+4); for(int i=(R-h)/2;i<(R-h)/2+h;i++)for(int j=(C-h)/2;j<(C-h)/2+h;j++)alive[i*C+j]=0;}
  vector<array<int,2>> E; // directed edges (first,second)
  for(int i=0;i<R;i++)for(int j=0;j<C;j++){ if(!alive[i*C+j])continue;
    if(j+1<C||(torus&&C>1)){int k=i*C+(j+1)%C; if(alive[k])E.push_back({i*C+j,k});}
    if(i+1<R||(torus&&R>1)){int k=((i+1)%R)*C+j; if(alive[k])E.push_back({i*C+j,k});}}
  int ne=E.size(); if(ne!=b*b){fprintf(stderr,"edges %d != b^2 %d\n",ne,b*b);return 2;}
  vector<vector<int>> inc(R*C); for(int e=0;e<ne;e++){inc[E[e][0]].push_back(e);inc[E[e][1]].push_back(e);}
  // variables
  vector<vector<int>> var; vector<int> sg(R*C,0); // sg: 0 identity, 1 sigma
  for(int i=0;i<R;i++)for(int j=0;j<C;j++){ if(!alive[i*C+j])continue;
    if(mirror){ if(j<C-1-j){var.push_back({i*C+j,i*C+C-1-j}); sg[i*C+C-1-j]=1;} else if(j==C-1-j){fprintf(stderr,"odd width\n");return 3;} }
    else var.push_back({i*C+j}); }
  mt19937_64 rng(seed); int nv=var.size(); int h=b/2;
  vector<int> g(R*C,0), cnt(b*b,0);
  auto setv=[&](int v,int d){ for(int c:var[v]) g[c]= sg[c]? (d+h)%b : d; };
  for(int v=0;v<nv;v++)setv(v,rng()%b);
  for(auto&e:E)cnt[g[e[0]]*b+g[e[1]]]++;
  int cost=0; for(int p=0;p<b*b;p++) if(!cnt[p])cost++;
  double T0=argc>7?atof(argv[7]):0.6,T1=argc>8?atof(argv[8]):0.12; long long CYC=argc>9?atoll(argv[9]):20000000; int best=cost; vector<int> bg=g; vector<int> es; vector<char> mark(ne,0);
  for(long long it=0;it<maxit&&cost>0;it++){
    double T=T0*pow(T1/T0,(double)(it%CYC)/(double)CYC);
    int v=rng()%nv; int c0=var[v][0]; int old= g[c0]; int nd=rng()%(b-1); if(nd>=old)nd++;
    es.clear(); for(int c:var[v])for(int e:inc[c]) if(!mark[e]){mark[e]=1;es.push_back(e);}
    for(int e:es)mark[e]=0;
    int d=0;
    for(int e:es){int p=g[E[e][0]]*b+g[E[e][1]]; if(--cnt[p]==0)d++;}
    setv(v,nd);
    for(int e:es){int p=g[E[e][0]]*b+g[E[e][1]]; if(cnt[p]++==0)d--;}
    if(d<=0 || (rng()>>11)*(1.0/9007199254740992.0) < exp(-d/T)){cost+=d; if(cost<best){best=cost;bg=g;}}
    else{ for(int e:es){int p=g[E[e][0]]*b+g[E[e][1]];--cnt[p];} setv(v,old); for(int e:es){int p=g[E[e][0]]*b+g[E[e][1]];cnt[p]++;} }
    if(it%50000000==0&&it)fprintf(stderr,"it %lld cost %d best %d\n",it,cost,best);
  }
  if(cost){printf("FAIL best %d\n",best);for(int i=0;i<R;i++){for(int j=0;j<C;j++){ if(alive[i*C+j])printf("%d ",bg[i*C+j]); else printf(". ");}printf("\n");}return 4;}
  // verify from scratch
  set<int> S; for(auto&e:E)S.insert(g[e[0]]*b+g[e[1]]); if((int)S.size()!=b*b){printf("VERIFY FAIL\n");return 5;}
  printf("SOLVED %d %d %d %s%s\n",R,C,b,mode.c_str(),mirror?"m":"");
  for(int i=0;i<R;i++){for(int j=0;j<C;j++){ if(alive[i*C+j])printf("%d ",g[i*C+j]); else printf(". ");}printf("\n");}
  return 0;
}
