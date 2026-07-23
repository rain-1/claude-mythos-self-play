import numpy as np, time, pickle, os
from dwell_engine import *
P = cities(220, seed=11)
D = np.hypot(*(P[:,None,:]-P[None,:,:]).transpose(2,0,1))
if os.path.exists("dwell_data.pkl"):
    old = pickle.load(open("dwell_data.pkl","rb"))
    tour, L = old['tour'], old['L']
    print("loaded tour", L)
else:
    t0=time.time()
    tour, L = best_tour(D, starts=12, kicks=420)
    print(f"best tour {L:.5f}  ({time.time()-t0:.0f}s)")
t0=time.time()
lb, pi, dwell, last, tog = held_karp(D, iters=8000, UB=L)
print(f"HK bound {lb:.5f}  ({time.time()-t0:.0f}s, edges seen {len(dwell)})  gap {(L-lb)/lb*100:.3f}%")
pickle.dump(dict(P=P, D=D, lb=lb, pi=pi, dwell=dwell, last=last, tog=tog, tour=tour, L=L),
            open("dwell_data.pkl","wb"))
