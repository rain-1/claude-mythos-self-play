import json, math, sys
sys.path.insert(0,'.')
from graphs import icosahedron
from common import *
n,E,ref=icosahedron()
sols=json.load(open(sys.argv[1]))
out={}
for s in sols:
    X=s[0::2]; Y=s[1::2]
    P=[(x,y) for x,y in zip(X,Y)]
    lens=[math.isqrt((X[a]-X[b])**2+3*(Y[a]-Y[b])**2) for a,b in E]
    g=0
    for l in lens: g=math.gcd(g,l)
    Pf=[(x,y*math.sqrt(3)) for x,y in P]
    fs=faces_from_drawing(Pf,E)
    key=(max(lens)//g, round(min_angle_deg(Pf,fs),2))
    out[key]=(g,P)
for k in sorted(out): print(k, out[k])
