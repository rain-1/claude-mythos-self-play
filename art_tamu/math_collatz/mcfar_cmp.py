# Compare Monte-Carlo coefficients at 2^40, 2^50, 2^60 with extrapolation from the exact data at 2^30 (complex: amplitude AND phase).
import numpy as np
from beta import beta, th
D=np.loadtxt('mcfar.txt')
B=65536; c=np.fromfile('oct30_65536.u32',dtype=np.uint32).reshape(B,4)[:,1:].astype(float)
g=c/c.sum(1)[:,None]; x=30+(np.arange(B)+0.5)/B
print("| q | basin | a | MC 2|c| | pred 2|c| | MC phase | pred phase |")
print("|---|---|---|---|---|---|---|")
for q in [12,53,106]:
    e=q*th-round(q*th); b=beta(e)
    c30=((g-g.mean(0))*np.exp(-2j*np.pi*q*x)[:,None]).mean(0)   # uniform-in-x weight, like the MC
    for a in [30,40,50,60]:
        row=D[(D[:,0]==a)&(D[:,1]==q)][0]; mc=row[2::2]+1j*row[3::2]
        pr=c30*np.exp(-b*(a-30))
        for j,name in enumerate(['1','5','17']):
            print("| %d | %s | 2^%d | %.4f | %.4f | %6.1f | %6.1f |"%(q,name,a,2*abs(mc[j]),2*abs(pr[j]),np.degrees(np.angle(mc[j])),np.degrees(np.angle(pr[j]))))
print("MC noise: std of 2|c| ~ %.4f"%(2*np.sqrt(0.22/2/4e6)))
