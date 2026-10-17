# Test: measured decay rate of every mode q=1..1023 vs random-walk (Wald) prediction, no free parameters.
import numpy as np
from modes2 import coefs
from beta import pred
qs=np.arange(1,1024)
r1,n1,_=coefs(21,qs); r2,n2,_=coefs(29,qs)
P=[pred(q) for q in qs]
rate_p=np.array([p['rate_exact'] for p in P]); eps=np.array([p['eps'] for p in P])
for j,name in enumerate(['basin1','basin5','basin17']):
    A1=np.abs(r1[:,j]); A2=np.abs(r2[:,j])
    ok=(A2>30*n2[j])&(A1>30*n1[j])           # both well above noise
    rate_m=np.log(A1/A2)/8
    d=rate_m[ok]-rate_p[ok]
    print("%s: %d modes with amp>30 sigma in both windows; corr(meas,pred)=%.4f; median|err|=%.4f /octave; max|err|=%.4f"%(
        name,ok.sum(),np.corrcoef(rate_m[ok],rate_p[ok])[0,1],np.median(abs(d)),abs(d).max()))
    if j==0:
        o=np.where(ok)[0]; o=o[np.argsort(-A2[o])][:30]
        print("  q     eps       amp(2^21-23) amp(2^29-31)  rate_meas rate_pred")
        for i in sorted(o,key=lambda i:qs[i]):
            print("  %4d %+.5f  %9.5f  %9.5f   %.5f   %.5f"%(qs[i],eps[i],2*A1[i],2*A2[i],rate_m[i],rate_p[i]))
