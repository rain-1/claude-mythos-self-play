# Table for THEORY.md: measured amplitude 2|c_q| of basin-1 density per 2-octave window vs. zero-parameter prediction
# A_pred(a) = A_meas(29) * exp(r_q (29-a)),  r_q = Wald rate (anchored at the top window only).
import numpy as np
from modes2 import coefs
from beta import pred
qs=[5,12,17,41,53,65,94,106,306,359,665,971]
R={a:coefs(a,qs)[0][:,0] for a in range(10,30)}
rp=[pred(q)['rate_exact'] for q in qs]
print("| window | "+" | ".join("q=%d"%q for q in qs)+" |"); print("|"+"---|"*(len(qs)+1))
print("| r_q pred | "+" | ".join("%.4f"%r for r in rp)+" |")
for a in range(10,30,2):
    A=2*np.abs(R[a]); P=2*np.abs(R[29])*np.exp(np.array(rp)*(29-a))
    print("| 2^%d-2^%d | "%(a,a+2)+" | ".join("%.4f (%.4f)"%(x,y) for x,y in zip(A,P))+" |")
A=2*np.abs(R[29]); print("| 2^29-2^31 | "+" | ".join("%.4f"%x for x in A)+" |")
