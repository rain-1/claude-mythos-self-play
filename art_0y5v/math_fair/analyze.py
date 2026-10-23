import pickle, json, numpy as np, sys
from shapes import all_shapes, Ellipse
import fair
from fair import *
def polish(sh,x):
    y,ok=corrector(sh,x.copy(),it=50); return y
def refine_sym(sh,xa,xb,pair,poly_ds=0.002):
    i,j=pair
    def g(x):
        inv=[invariants(P) for P in Ypolys(sh,x,poly_ds)]; return inv[i]['ev'][1]-inv[j]['ev'][1]+inv[i]['ev'][0]-inv[j]['ev'][0]
    tau=(xb-xa)/np.linalg.norm(xb-xa); ga=g(xa); lo,hi=0.0,1.0; x=xa
    for _ in range(40):
        lam=0.5*(lo+hi); xm=(1-lam)*xa+lam*xb; x,ok=corrector(sh,xm.copy(),tau,xm)
        if np.sign(g(x))==np.sign(ga): lo=lam
        else: hi=lam
    return x
def piece_info(polys):
    pairs,inv=congruent_pairs(polys,1e-5)
    return pairs,[dict(inertia=I['ev'].tolist(),corner_turns_deg=np.degrees(I['corners']).round(6).tolist()) for I in inv]
def sol_record(sh,kind,x,note=''):
    x=np.asarray(x,float)
    if kind=='Y':
        a,P=Ypieces(sh,x); B=sh.pt(np.array(x[2:5])); polys=Ypolys(sh,x,0.01); pc=Ypolys(sh,x,0.002)
        ang=np.degrees(Yangles(sh,x)).tolist()
        rec=dict(type='Y',junction=x[:2].tolist(),endpoints=B.tolist(),boundary_params=x[2:5].tolist(),angles_at_junction_deg=ang)
    else:
        a,P=Cpieces(sh,x); B=sh.pt(np.array(x)); polys=Cpolys(sh,x,0.01); pc=Cpolys(sh,x,0.002)
        rec=dict(type='chords',chords=[B[:2].tolist(),B[2:].tolist()],boundary_params=list(map(float,x)))
    pairs,inf=piece_info(pc)
    rec.update(areas=a.tolist(),perimeters=P.tolist(),residual=float(np.abs(YF(sh,x) if kind=='Y' else CF(sh,x)).max()),
               congruent_pairs=pairs,pairwise_noncongruent=len(pairs)==0,noncongruence_margin=float(noncong_margin(pc)),
               piece_invariants=inf,pieces=[np.round(P_,13).tolist() for P_ in polys],note=note)
    return rec
def analyze(sh,d):
    fair.KINKS=(sh.offs[:-1],sh.S) if hasattr(sh,'offs') else None
    poly=sh.sample(0,sh.S,0.005)
    out=dict(name=sh.name,area=sh.A,perimeter=sh.Ltot,boundary=sh.pt(np.linspace(0,sh.S,401)[:-1]).round(13).tolist(),
             Y_families=[],chord_solutions=[],n_unphysical_Y_curves=0)
    summ=[]
    for ci,C in enumerate(d['curves']):
        ok=C['inside']&C['convex']; xs=C['xs']
        if not C['inside'].any(): out['n_unphysical_Y_curves']+=1; continue
        fam=dict(closed=bool(C['closed']),n_points=len(xs),curve_length_5d=float(np.sum(np.linalg.norm(np.diff(xs,axis=0),axis=1))),
                 frac_inside=float(C['inside'].mean()),frac_convex_and_inside=float(ok.mean()),
                 junction_path=xs[:,:2].round(10).tolist(),solutions=[])
        m=np.where(ok,C['margin'],-1)
        if ok.any():
            ib=int(np.argmax(m)); fam['solutions'].append(sol_record(sh,'Y',polish(sh,xs[ib]),'max non-congruence margin on this family'))
            for k in np.linspace(0,len(xs)-1,9)[:-1].astype(int):
                if ok[k] and k!=ib: fam['solutions'].append(sol_record(sh,'Y',polish(sh,xs[k]),'sample along family'))
        # congruent-pair points: sign changes of pairwise inertia differences
        syms=[]
        invs=[[invariants(P) for P in Ypolys(sh,y,0.01)] for y in xs]
        for (i,j) in [(0,1),(1,2),(0,2)]:
            g=np.array([I[i]['ev'].sum()-I[j]['ev'].sum() for I in invs])
            for k in np.where(np.sign(g[:-1])!=np.sign(g[1:]))[0]:
                x=refine_sym(sh,xs[k],xs[k+1],(i,j))
                rec=sol_record(sh,'Y',x,'pair (%d,%d) inertia-trace equal'%(i,j))
                if rec['congruent_pairs']: syms.append(rec)
        # dedupe syms (mod relabel)
        U=[]
        for r_ in syms:
            if not any(np.allclose(np.sort(np.array(r_['endpoints']),0),np.sort(np.array(u['endpoints']),0),atol=1e-6) and np.allclose(r_['junction'],u['junction'],atol=1e-6) for u in U): U.append(r_)
        for r_ in U:
            r_['note']='congruent-pair point: '+r_['note']; fam['solutions'].append(r_)
        fam['n_congruent_pair_points']=len(U)
        fam['n_congruent_pair_points_convex']=sum(1 for r_ in U if max(r_['angles_at_junction_deg'])<=180+1e-9)
        out['Y_families'].append(fam)
        summ.append('Yfam closed=%s len=%.2f convex%%=%.0f maxmargin=%.4f congruent-pair pts=%d'%(fam['closed'],fam['curve_length_5d'],100*ok.mean(),m.max(),len(U)))
    for x in d['chords']:
        x=np.asarray(x); 
        y=x.copy()
        for _ in range(30):
            f=CF(sh,y)
            if np.abs(f).max()<1e-14: break
            y=y-np.linalg.solve(jac(lambda z:CF(sh,z),y,sidx=(0,1,2,3)),f)
        r_=sol_record(sh,'chords',y); out['chord_solutions'].append(r_)
        summ.append('chords: congruent pairs %s margin %.4f'%(r_['congruent_pairs'],r_['noncongruence_margin']))
    # targeted search: convex multistart seeds + short local traces, keep max non-congruence margin
    rng=np.random.default_rng(5); S=seeds(sh,300,rng,poly); best=None
    for x in [x for x in S if Yangles(sh,x).max()<=np.pi][:25]:
        for hs in (0.005,-0.005):
            xs,_,_=trace(sh,x,h=hs,maxsteps=120)
            for y in xs:
                if Yangles(sh,y).max()<=np.pi and inside(sh,y[:2],poly):
                    m=noncong_margin(Ypolys(sh,y,0.01))
                    if best is None or m>best[0]: best=(m,y)
    if best is not None:
        out['best_noncongruent_Y']=sol_record(sh,'Y',polish(sh,best[1]),'targeted search: convex Y maximising non-congruence margin')
        summ.append('targeted best convex Y: margin %.4f angles %s pairs %s'%(out['best_noncongruent_Y']['noncongruence_margin'],np.round(out['best_noncongruent_Y']['angles_at_junction_deg'],3),out['best_noncongruent_Y']['congruent_pairs']))
    out['admits_noncongruent']=any(s['pairwise_noncongruent'] and (s['type']=='chords' or max(s['angles_at_junction_deg'])<=180+1e-9)
                                   and s['noncongruence_margin']>1e-3 for f in out['Y_families'] for s in f['solutions']) or \
                               any(s['pairwise_noncongruent'] and s['noncongruence_margin']>1e-3 for s in out['chord_solutions']) or \
                               ('best_noncongruent_Y' in out and out['best_noncongruent_Y']['pairwise_noncongruent'] and max(out['best_noncongruent_Y']['angles_at_junction_deg'])<=180+1e-9 and out['best_noncongruent_Y']['noncongruence_margin']>1e-3)
    return out,summ
if __name__=="__main__":
    raw=pickle.load(open(sys.argv[1],'rb')); res={}
    for sh in all_shapes():
        if sh.name not in raw: continue
        o,s=analyze(sh,raw[sh.name]); res[sh.name]=o
        print(sh.name,'admits non-congruent:',o['admits_noncongruent'],'| unphysical Y curves',o['n_unphysical_Y_curves']); [print('   ',t) for t in s]
    json.dump(res,open(sys.argv[2],'w'))
