from flower import *
import time
t=time.time()
render(1024,1024,'../proto/f2.png',legs=((6,1),(10,3)),hyp=(5,2),scale=0.15,center=(0.5,0.5))
render(1024,1024,'../proto/f3.png',scale=0.17,center=(0.5,0.5))
print(time.time()-t)
