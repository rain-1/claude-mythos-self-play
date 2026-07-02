import numpy as np, time
from dbm2 import dbm
t0=time.time()
age,parent,phi,cl=dbm(620, 8500, eta=1.4, seed=11, warm_sweeps=3,
                      full_every=110, Rout_frac=0.995)
r=np.hypot(*np.nonzero(age>=0)-np.array([[620//2],[620//2]]))
print("grow time",time.time()-t0,"size",cl.sum(),"maxr",r.max(),"of",620/2)
np.savez_compressed('dbm_big.npz', age=age, parent=parent, phi=phi.astype(np.float32))
print("saved")
