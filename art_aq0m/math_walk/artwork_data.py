import os; os.environ["OMP_NUM_THREADS"]="1"
import json, numpy as np
from walk import W_bessel, W_angles, all_W
a=[1.0,0.85,0.7,0.55,0.4]
Wb=all_W(a,lambda b,o: W_bessel(b,o,T=8000.0)); Wa=all_W(a,lambda b,o: W_angles(b,o,N=3000))
for k in range(5): print(k,a[k],"%.8f %.8f %.1e"%(Wb[k],Wa[k],Wb[k]-Wa[k]))
print("sums",sum(Wb),sum(Wa))
json.dump({"amplitudes":a,"event":"E_k = {|S - a_k U_k| < a_k}, S = sum a_j U_j, U_j iid uniform on unit circle",
 "P_E_k":[round(x,6) for x in Wb],"P_E_k_angle_quadrature":[round(x,6) for x in Wa],"sum":sum(Wb)},open("artwork_data.json","w"),indent=1)
