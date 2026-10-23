# condense partitions_raw.json -> partitions.json (and add the certified disc data)
import json, numpy as np, mpmath as mp
R=json.load(open('partitions_raw.json'))
def thin(P,maxpts=160):
    P=np.array(P)
    if len(P)<=maxpts: return P.tolist()
    # keep corners (large turning) + uniform subsample
    e1=P-np.roll(P,1,0); e2=np.roll(P,-1,0)-P
    turn=np.abs(np.arctan2(e1[:,0]*e2[:,1]-e1[:,1]*e2[:,0],(e1*e2).sum(1)))
    keep=set(np.where(turn>0.02)[0])|set(np.linspace(0,len(P)-1,maxpts).astype(int))
    return P[sorted(keep)].tolist()
def slim(s):
    s=dict(s); s['pieces']=[thin(P) for P in s['pieces']]; return s
out={'_README':'See RESULTS.md. Coordinates: every shape scaled to area pi. Y solutions: junction, endpoints (boundary points), angles at junction; '
     'pieces = closed polygons (boundary arcs sampled, first point not repeated). congruent_pairs = index pairs of pieces judged congruent '
     '(invariants: inertia eigenvalues, max centroid distance, corner turning angles, tol 1e-5). Y_families = traced 1-parameter solution curves '
     '(junction_path = junction along the curve; solutions = representative points incl. max non-congruence margin and congruent-pair points).'}
for nm,d in R.items():
    d=dict(d)
    fams=[]
    for f in d['Y_families']:
        f=dict(f); sols=f['solutions']
        main=[s for s in sols if not s['note'].startswith('congruent-pair')]
        cp=[s for s in sols if s['note'].startswith('congruent-pair')]
        allcong=len(cp)>40
        f['all_points_have_congruent_pair']=bool(allcong or (main and all(s['noncongruence_margin']<1e-6 for s in main)))
        f['solutions']=[slim(s) for s in main[:5]+cp[:6]]
        jp=np.array(f['junction_path']); f['junction_path']=jp[::max(1,len(jp)//300)].round(8).tolist()
        fams.append(f)
    d['Y_families']=fams
    d['chord_solutions']=[slim(s) for s in d['chord_solutions']]
    if 'best_noncongruent_Y' in d: d['best_noncongruent_Y']=slim(d['best_noncongruent_Y'])
    out[nm]=d
# certified disc solutions (unit disc scaled to area pi = unit disc)
mp.mp.dps=40
r,t=mp.findroot(lambda r,t:[t-r*mp.sin(t)-2*mp.pi/3, mp.sqrt(1+r*r-2*r*mp.cos(t))-(1-r+3*r*mp.sin(t))],(mp.mpf('0.60826'),mp.mpf('2.47195')))
def disc_pieces(p,ts):
    res=[]
    for i in range(3):
        a=ts[i]; b=ts[(i+1)%3]+(2*np.pi if i==2 else 0)
        th=np.linspace(a,b,max(3,int((b-a)/0.01)))
        res.append([list(p)]+np.stack([np.cos(th),np.sin(th)],1).tolist())
    return res
tt=[0.0,float(t),2*np.pi-float(t)]
out['disc']['certified_Y_solutions']=[
  dict(name='120-degree (centre)',junction=[0,0],endpoint_angles=[0,2*np.pi/3,4*np.pi/3],arcs=[2*np.pi/3]*3,perimeter=2+2*np.pi/3,
       congruent_pairs=[[0,1],[0,2],[1,2]],pieces=disc_pieces((0,0),[0,2*np.pi/3,4*np.pi/3])),
  dict(name='mirror-symmetric',r=mp.nstr(r,35),t1=mp.nstr(t,35),junction=[mp.nstr(r,20),'0'],endpoint_angles=['0',mp.nstr(t,20),mp.nstr(2*mp.pi-t,20)],
       arcs=[mp.nstr(t,20),mp.nstr(2*mp.pi-2*t,20),mp.nstr(t,20)],perimeter=mp.nstr(t+1-r+mp.sqrt(1+r*r-2*r*mp.cos(t)),25),
       angles_at_junction_deg=[mp.nstr(mp.degrees(mp.atan2(mp.sin(t),mp.cos(t)-r)),20)]*2+[mp.nstr(360-2*mp.degrees(mp.atan2(mp.sin(t),mp.cos(t)-r)),20)],
       congruent_pairs=[[0,2]],pieces=disc_pieces((float(r),0.0),tt))]
json.dump(out,open('partitions.json','w'))
import os; print(os.path.getsize('partitions.json')/1e6,'MB')
