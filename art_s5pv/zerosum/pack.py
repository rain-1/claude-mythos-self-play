# max packing of disjoint zero-sum subsets (sizes 5,6,7) of U; N = packed + 1 (leftover is zero-sum automatically)
import sys
from ortools.sat.python import cp_model
sets=[tuple(map(int,l.split()[1:])) for l in open(sys.argv[3] if len(sys.argv)>3 else 'sets.txt')]
only=int(sys.argv[1]) if len(sys.argv)>1 else 0   # 0: all sizes; 6: only sizes<=6 (for the upper bound)
if only: sets=[s for s in sets if len(s)<=only]
m=cp_model.CpModel();x=[m.NewBoolVar(f"x{i}") for i in range(len(sets))]
inc=[[] for _ in range(629)]
for i,s in enumerate(sets):
    for e in s: inc[e].append(x[i])
for e in range(629):
    if inc[e]: m.AddAtMostOne(inc[e])
if only:
    m.Maximize(sum(x[i]*(1 if len(s)==6 else 2) for i,s in enumerate(sets)))   # 2a+b
else:
    m.Maximize(sum(x))
sol=cp_model.CpSolver();sol.parameters.max_time_in_seconds=float(sys.argv[2]) if len(sys.argv)>2 else 900;sol.parameters.num_workers=4
st=sol.Solve(m);print(sol.StatusName(st),'obj',sol.ObjectiveValue(),'bound',sol.BestObjectiveBound())
ch=[sets[i] for i in range(len(sets)) if sol.Value(x[i])]
cov=sum(len(s) for s in ch);print('chosen',len(ch),'covered',cov,'leftover',629-cov,'sizes',{k:sum(len(s)==k for s in ch) for k in (5,6,7)})
open(f'packing_{only}.txt','w').write('\n'.join(' '.join(map(str,s)) for s in ch))
