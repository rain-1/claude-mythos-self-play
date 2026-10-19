import sys, json, itertools
from cwlib import *
fn=sys.argv[1]; N=int(sys.argv[2])
def orbkey(a,b): return tuple(sorted((a,b,-a-b)))
sols=set()
for line in open(fn):
    x=list(map(int,line.split())); Fv=x[0]; pts=list(zip(x[1::2],x[2::2]))
    for (a,b),(c,d) in itertools.combinations(pts,2):
        if orbkey(a,b)==orbkey(c,d): continue
        if reduce(gcd,(a,b,c,d))!=1: continue
        assert F(a,b)==F(c,d)==Fv
        sols.add(tuple(sorted([(a,b),(c,d)])))
# classes modulo Aut_Q: key = unordered pair of S3-orbit keys (up to global sign)
def clskey(P):
    a,b,c,d=P
    k=tuple(sorted([orbkey(a,b),orbkey(c,d)]))
    k2=tuple(sorted([orbkey(-a,-b),orbkey(-c,-d)]))
    return min(k,k2)
classes={}
for (p,q) in sols:
    P=p+q; classes.setdefault(clskey(P),[]).append(P)
rows=[]
for k,Ps in classes.items():
    Pmin=min(Ps,key=height)
    o=on_cw_orbit(Pmin)
    rows.append((height(Pmin),Pmin,F(Pmin[0],Pmin[1]),len(Ps),o))
rows.sort()
print("N=%d  unordered solution pairs {(a,b),(c,d)} with a<=b,c<=d,F>0: %d ; classes mod Aut_Q: %d"%(N,len(sols),len(rows)))
for h,P,Fv,n,o in rows:
    print(h,P,Fv,'#reps_in_box=%d'%n,'CW-orbit' if o else 'NOT on CW orbit', o if o else '')
with open('solutions.tsv','w') as f:
    f.write("a\tb\tc\td\tF\theight\ton_CW_orbit\n")
    allP=sorted((p+q for p,q in sols), key=lambda P:(height(P),P))
    for P in allP:
        f.write("\t".join(map(str,P))+"\t%d\t%d\t%s\n"%(F(P[0],P[1]),height(P),'yes' if on_cw_orbit(P) else 'no'))
json.dump([list(r[1]) for r in rows][:40],open('small_pairs_classes.json','w'))
json.dump([list(P) for P in allP][:40],open('small_pairs.json','w'))
