import numpy as np, pickle, time, sys
from shapes import all_shapes
from fair import *
def covered(sh,x,curves,tol):
    E=[embed(sh,y) for y in relabels(sh,x)]
    for C in curves:
        EC=C['emb']
        for e in E:
            if np.min(np.linalg.norm(EC-e,axis=1))<tol: return True
    return False
def run(sh,nseed=150,h=0.02,seed=0):
    import fair
    fair.KINKS=(sh.offs[:-1],sh.S) if hasattr(sh,'offs') else None
    rng=np.random.default_rng(seed); poly=sh.sample(0,sh.S,0.005)
    t0=time.time(); S=seeds(sh,nseed,rng,poly)
    curves=[]
    for x in S:
        if covered(sh,x,curves,3*h): continue
        x,_=corrector(sh,x)
        xs,cl,why=trace(sh,x,h=h,maxsteps=2500)
        if not cl:  # trace the other direction too
            xs2,cl2,why2=trace(sh,x,h=-h,maxsteps=2500)
            xs=np.vstack([xs2[::-1],xs[1:]]); why=why+'/'+why2
        emb=np.array([embed(sh,y) for y in xs])
        ins=np.array([inside(sh,y[:2],poly) for y in xs]); cv=np.array([Yangles(sh,y).max()<=np.pi+1e-12 for y in xs])
        marg=np.array([noncong_margin(Ypolys(sh,y,0.01)) for y in xs])
        curves.append(dict(xs=xs,emb=emb,closed=cl,why=why,inside=ins,convex=cv,margin=marg))
        print('  %s curve %d: %d pts closed=%s (%s) inside %.2f convex&inside %.2f max margin %.4f  [%.0fs]'%(
            sh.name,len(curves),len(xs),cl,why,ins.mean(),(ins&cv).mean(),marg[ins&cv].max() if (ins&cv).any() else -1,time.time()-t0),flush=True)
    ch=chord_solutions(sh,300,rng)
    print('  %s: %d seeds, %d Y-curves, %d chord-pair solutions [%.0fs]'%(sh.name,len(S),len(curves),len(ch),time.time()-t0),flush=True)
    return dict(name=sh.name,curves=curves,chords=ch,nseeds=len(S))
if __name__=="__main__":
    names=sys.argv[1:]
    out={}
    for sh in all_shapes():
        if names and sh.name not in names: continue
        out[sh.name]=run(sh)
        pickle.dump(out,open('raw_%s.pkl'%('_'.join(names) if names else 'all'),'wb'))
