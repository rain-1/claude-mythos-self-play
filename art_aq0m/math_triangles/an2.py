import json
from fractions import Fraction as F
from math import comb
D={int(n):{int(x):c for x,c in v.items()} for n,v in json.load(open('dist.json')).items()}
for n in range(3,26):
    d=D[n]; M=max(d)
    miss=[x for x in range(M+1) if x not in d]
    print(n,"max",M,"(n^3-n)/24" if M*24==n**3-n else "(n^3-4n)/24" if M*24==n**3-4*n else "?", "cnt",d[M],
          "#support",len(d),"missing top:",[M-x for x in miss if x>M-40][::-1][:15], "small support:",sorted(d)[:8])
# cumulants vs limit T (sech(sqrt(2 l))): k1=1,k2=2/3,k3=16/15, k4=272/105
n=60; d=D[n]; T=2**(n-1)
ys={ (F(n**3,24)-x)*8/F(n*n):c for x,c in d.items()}
m=[sum(F(c)*y**k for y,c in ys.items())/T for k in range(5)]
k2=m[2]-m[1]**2; k3=m[3]-3*m[2]*m[1]+2*m[1]**3
print("n=60 scaled mean,var,k3:",float(m[1]),float(k2),float(k3), " limit 1, .6667, 1.0667")
