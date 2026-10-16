import glob, math
def load(f):
    d={}
    for l in open(f):
        t=l.split()
        if t[0] in('N','succ','prepass'): d[t[0]]=int(t[1])
        elif t[0]=='hist': d['hist']=list(map(int,t[1:]))
    return d
N=S=0; H=[0]*31
for f in sorted(glob.glob('runs/u_*.txt')):
    d=load(f); N+=d['N']; S+=d['succ']; H=[a+b for a,b in zip(H,d['hist'])]
p=S/N; se=math.sqrt(p*(1-p)/N)
print(f"uniform: N={N} succ={S} p={p:.7f} se={se:.2e} 95%CI=[{p-1.96*se:.7f},{p+1.96*se:.7f}]")
print("nvalid among successes (k: fraction):")
for k in range(1,31):
    if H[k]: print(f"  {k:2d}: {H[k]/S:.5f}")
print(f"P(all 30 | >=1) = {H[30]/S:.5f}  (P(all 30) = {H[30]/N:.6f})")
print("mean nvalid | success:", sum(k*H[k] for k in range(31))/S)
e=load('runs/exp.txt'); pe=e['succ']/e['N']; see=math.sqrt(pe*(1-pe)/e['N'])
print(f"exp: N={e['N']} p={pe:.7f} se={see:.2e}  diff from uniform = {(pe-p)/math.hypot(se,see):.2f} sigma")
