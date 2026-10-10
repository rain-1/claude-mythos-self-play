# upper bound: any partition into N zero-sum parts has  N <= 629/8 + W/8,
# W = max over disjoint families of parts of size <=7 of  sum (8-|S|)   (parts of size >=8 cost >= 8 each)
import numpy as np,sys
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
sets=[tuple(map(int,l.split()[1:])) for l in open('sets.txt')]
w=np.array([8-len(s) for s in sets],float)
A=lil_matrix((629,len(sets)))
for j,s in enumerate(sets):
    for e in s:A[e,j]=1
r=linprog(-w,A_ub=A.tocsr(),b_ub=np.ones(629),bounds=(0,1),method='highs')
W=-r.fun;print('LP  W <=',W,' => N <=',(629+W)/8)
from ortools.sat.python import cp_model
m=cp_model.CpModel();x=[m.NewBoolVar('') for _ in sets]
inc=[[] for _ in range(629)]
for j,s in enumerate(sets):
    for e in s:inc[e].append(x[j])
for l in inc:
    if l:m.AddAtMostOne(l)
m.Maximize(sum(int(w[j])*x[j] for j in range(len(sets))))
so=cp_model.CpSolver();so.parameters.max_time_in_seconds=float(sys.argv[1]);so.parameters.num_workers=4
st=so.Solve(m);print(so.StatusName(st),'W found',so.ObjectiveValue(),'W bound',so.BestObjectiveBound(),' => N <=',int((629+so.BestObjectiveBound())//8))
