"""EVERY ROW CANCELS: the twisted Moebius sums A_u(D) = sum_n mu(n) (u/n)_6 over primary n of norm <= D,
drawn as walks in the complex plane for every row u of norm <= U; the untwisted row u = 1 in coral; the rows
u = p^6 (sixth powers, which copy the target row) in honey."""
import numpy as np, sys, pickle, math
from PIL import Image, ImageDraw, ImageFont
from eis import norm, tocx
from caption import caption, CORAL, INK, SOFT, F
S=int(sys.argv[1]); out=sys.argv[2]; U=int(sys.argv[3])
T=pickle.load(open('tables_30000.pkl','rb'))
prim=T['prim']; mu=T['mu']; fac=T['fac']; pidx=T['pidx']; rows=T['rows']; sym=T['sym']; P=T['primes']
Z6=np.exp(2j*np.pi*np.arange(6)/6)
sel=[j for j,(a,b) in enumerate(rows) if norm(a,b)<=U]
nP=len(P); nN=len(prim)
# value matrix V[n, row]
V=np.zeros((nN,len(sel)),np.complex64)
symsel=sym[:,sel]
for i in range(nN):
    if mu[i]==0: continue
    k=np.zeros(len(sel),int); ok=np.ones(len(sel),bool)
    for p,e in fac[i].items():
        s=symsel[pidx[p]]; ok&=(s>=0); k+=np.where(s>=0,s,0)
    V[i]=np.where(ok,Z6[k%6]*mu[i],0)
walks=np.cumsum(V,axis=0)
# sixth-power rows: chi_n(p^6) = 1 if p does not divide n
sixth=[]
for (a,b,N,kind) in P[:7]:
    v=np.array([0 if mu[i]==0 else (0 if (a,b) in fac[i] else mu[i]) for i in range(nN)],np.complex64)
    sixth.append(((a,b,N),np.cumsum(v)))
one=np.cumsum(mu.astype(np.complex64))
rad=np.abs(walks).max(); print('rows',len(sel),'max |walk|',rad,'final |A_u| rms',np.sqrt(np.mean(np.abs(walks[-1])**2)),'|A_1|',abs(one[-1]), 'sqrt(#terms)',math.sqrt((mu!=0).sum()))
SS=2; W=S*SS; H=int(W*1.12); cx,cy=W/2,W*0.5
sc=W*0.44/rad
PAL=np.array([[250,140,160],[255,175,140],[253,214,120],[180,224,140],[130,214,184],[130,196,240],[156,160,240],[196,150,236],[250,140,160]],float)
def wheel(h):
    h=(h%1)*(len(PAL)-1); i=int(h); f=h-i; return tuple(int(v) for v in PAL[i]*(1-f)+PAL[i+1]*f)
img=Image.new('RGB',(W,H),(252,251,249))
lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
lw=max(1,int(W/1800))
order=np.argsort([-norm(*rows[j]) for j in sel])   # big norms first, small rows on top
for jj in order:
    j=sel[jj]; ua,ub=rows[j]; z=tocx(ua,ub); h=(np.angle(z)/(2*np.pi))%1
    col=wheel(h); w=walks[:,jj]
    pts=[(cx+w[i].real*sc,cy-w[i].imag*sc) for i in range(0,len(w),3)]
    d.line(pts,fill=col+(120,),width=lw)
img=Image.alpha_composite(img.convert('RGBA'),lay).convert('RGB'); d=ImageDraw.Draw(img)
# sqrt ring
r0=math.sqrt((mu!=0).sum())*sc
d.ellipse([cx-r0,cy-r0,cx+r0,cy+r0],outline=(150,130,160),width=max(2,int(W/1200)))
# sixth-power rows (honey) and the target row (coral)
HON=(246,196,96)
for (p,wk) in sixth:
    pts=[(cx+wk[i].real*sc,cy-wk[i].imag*sc) for i in range(0,len(wk),2)]
    d.line(pts,fill=HON,width=max(2,int(W/1000)))
pts=[(cx+one[i].real*sc,cy-one[i].imag*sc) for i in range(0,len(one),2)]
d.line(pts,fill=(255,255,255),width=max(4,int(W/450))); d.line(pts,fill=CORAL,width=max(2,int(W/800)))
r=W*0.006; d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=INK)
# endpoints
for jj in range(len(sel)):
    w=walks[-1,jj]; x,y=cx+w.real*sc,cy-w.imag*sc; rr=W*0.003
    d.ellipse([x-rr,y-rr,x+rr,y+rr],fill=wheel((np.angle(tocx(*rows[sel[jj]]))/(2*np.pi))%1))
nterms=int((mu!=0).sum())
caption(img,W/2,W*0.955,'Every Row Cancels',
  f'A_u = Σ μ(n)·(u/n)₆ over the {nterms:,} squarefree primary Eisenstein integers of norm ≤ 30,000, one walk for each of the {len(sel)} rows u with N(u) ≤ {U}',
  f'hue = direction of u  ·  coral: the untwisted row u = 1, the target  ·  honey: the rows u = p⁶, which copy the target except at multiples of p  ·  ring: √{nterms:,} = {math.sqrt(nterms):.0f}',
  W*0.036,align='center',line3=f'openai/math family 003 claims square-root cancellation on average over the rows; measured here: root-mean-square |A_u| = {np.sqrt(np.mean(np.abs(walks[-1])**2)):.1f} against √terms = {math.sqrt(nterms):.1f}')
img.resize((S,int(H/SS)),Image.LANCZOS).save(out)
