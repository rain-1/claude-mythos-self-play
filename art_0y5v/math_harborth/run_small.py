import sys, json, time, math
sys.path.insert(0,'.')
import graphs
from common import faces_from_drawing
from gsearch import run
name=sys.argv[1]; order=json.loads(sys.argv[2]); ks=json.loads(sys.argv[3]); L=int(sys.argv[4])
n,edges,ref=getattr(graphs,name)()
faces=faces_from_drawing(ref,edges)
allres={}
for k in ks:
    t=time.time()
    tot,res=run(n,edges,faces,order,k,L,L)
    print(name,'k',k,'L',L,'sols',tot,round(time.time()-t,1),flush=True)
    for mx in sorted(res): allres[f"{k}:{mx}"]=(k,mx,math.degrees(res[mx][0]),res[mx][1])
    best=-1
    for mx in sorted(res):
        a=math.degrees(res[mx][0])
        if a>best+0.01: best=a; print('   max',mx,'ang',round(a,2),res[mx][1])
json.dump(allres,open(f'small_{name}_L{L}.json','w'))
