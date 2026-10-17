# Mode analysis for generalized maps (3n+d)/2^v: which q dominate, and do decay rates match the same Wald prediction?
import numpy as np
from beta import pred, th
B=2048; LOG=26
def coefs(C,a,qs,w=2):
    c=C[a:a+w].reshape(-1,C.shape[-1]); tot=c.sum(1); N=tot.sum(); pbar=c.sum(0)/N
    x=(np.arange(w*B)+0.5)/B+a; qs=np.asarray(qs,float)
    r=np.exp(-2j*np.pi*np.outer(qs,x))@(c-np.outer(tot,pbar))/N/np.sinc(qs/B)[:,None]
    return r,np.sqrt(pbar*(1-pbar)/N/2),pbar
qs=np.arange(1,1024)
for d in [5,13]:
    C=np.fromfile('gen_d%d.u32'%d,dtype=np.uint32).reshape(LOG,B,10)[:,:,1:].astype(float)
    r2,n2,pb=coefs(C,24,qs); r1,n1,_=coefs(C,16,qs)
    j=int(np.argmax(pb[:8]))   # pick a basin with large share but not ~1
    order=np.argsort(-pb); print("d=%d basin shares (cycle ids 1..8, 9=other) at 2^24-26:"%d,np.round(pb,4))
    for j in order[:3]:
        A=2*np.abs(r2[:,j]); top=np.argsort(-A)[:10]
        print("  basin id %d (share %.3f): top modes at 2^24-26 (noise %.1e):"%(j+1,pb[j],2*n2[j]*1.4),
              ", ".join("%d:%.4f"%(qs[i],A[i]) for i in top))
        print("     amp q=12,41,53,94,106: 2^16-18:",np.round(2*np.abs(r1[[11,40,52,93,105],j]),4)," 2^24-26:",np.round(A[[11,40,52,93,105]],4))
        ok=(np.abs(r2[:,j])>10*n2[j])&(np.abs(r1[:,j])>10*n1[j])
        rm=np.log(np.abs(r1[ok,j])/np.abs(r2[ok,j]))/8; rp=np.array([pred(q)['rate_exact'] for q in qs[ok]])
        if ok.sum()>2: print("     rate test: %d modes, corr %.3f, median|err| %.4f; q=12 meas %.4f pred %.4f"%(ok.sum(),np.corrcoef(rm,rp)[0,1],np.median(abs(rm-rp)),
              np.log(abs(r1[11,j])/abs(r2[11,j]))/8,pred(12)['rate_exact']))
    eps=np.array([q*th-round(q*th) for q in qs])
    A=2*np.abs(r2[:,order[0]])
    print("  basin %d: median amp over q with |eps|<0.01: %.4f ; over q with |eps|>0.05: %.5f (noise %.5f)"%(order[0]+1,np.median(A[abs(eps)<0.01]),np.median(A[abs(eps)>0.05]),2*n2[order[0]]))
