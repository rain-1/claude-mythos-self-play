import json, subprocess
def run(n,seed,mode):
    try: out=subprocess.run(['./find',str(n),str(seed),'1',str(mode)],capture_output=True,text=True,timeout=20).stdout.split()
    except subprocess.TimeoutExpired: return None
    return json.loads(out[0]) if out else None
D={}
for n in (11,12,13,17):
    L=[]
    if n%2 and n%3: L.append([(2*j)%n for j in range(n)])          # linear q(j)=2j
    t=run(n,7,2)
    if t: L.append(t)                                               # toroidal, nonlinear
    for seed in (7,8):
        x=run(n,seed,1)
        if x and x not in L: L.append(x)                            # non-toroidal (uses incremental slack)
    D[str(n)]=L
for n in [1,5]+list(range(7,41)):
    if str(n) in D: continue
    for seed in (3,1,2,4,5):
        x=run(n,seed,0)
        if x: D[str(n)]=[x]; break
json.dump(D,open('squares.json','w'))
print({k:len(v) for k,v in D.items()})
