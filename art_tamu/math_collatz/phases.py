# Phase of modes q=12,53,106 per 2-octave window, for the three basins; compare drift with predicted frequency shift.
import numpy as np
from modes2 import coefs
from beta import pred
for q in [12,53,106]:
    p=pred(q); f=p['fshift_exact']
    print("q=%d: predicted local frequency q%+.5f -> phase drift %+.2f deg/octave"%(q,f,360*f))
    print("  win    amp1    amp5   amp17 | ph1    ph5    ph17 (deg) | ph1 - 360*f*(a+1) | ang(1,5) ang(5,17) ang(17,1)")
    ph0=[]
    for a in range(10,31):
        r,_,_=coefs(a,[q]); c=r[0]
        ph=np.degrees(np.angle(c)); A=2*np.abs(c)
        corr=(ph[0]-360*f*(a+1)+180)%360-180
        d=lambda i,j:(np.degrees(np.angle(c[j]/c[i])))%360
        print("  %2d-%2d %.4f %.4f %.4f | %6.1f %6.1f %6.1f | %6.1f | %5.1f %5.1f %5.1f"%(a,a+2,*A,*ph,corr,d(0,1),d(1,2),d(2,0)))
