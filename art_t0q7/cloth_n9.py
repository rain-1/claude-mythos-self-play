import numpy as np, itertools, json, time
from cloth_lib import area_exact
t0=time.time(); best=(2.0,None); cnt=0
rev9 = 5/9  # (n+1)/2n = 10/18
for pm in itertools.permutations(range(9)):
    a = area_exact(np.array(pm))
    if a < best[0]-1e-12: best=(a,pm)
    cnt+=1
print("n=9 exhaustive:", best[0], best[1], "rev:", rev9, "beats:", best[0]<rev9-1e-9, f"{time.time()-t0:.0f}s")
json.dump({"min":best[0],"argmin":list(best[1])}, open("cloth_n9.json","w"))
