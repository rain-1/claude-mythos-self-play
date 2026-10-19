import numpy as np, pickle
info=pickle.load(open('planes.pkl','rb'))
for nv,inside in info:
  if len(inside)==3:
    k=np.argmax(abs(nv)); v=nv/nv[k]
    rat=np.allclose(v.imag,0,atol=1e-9)
    print(inside, 'REAL-plane' if rat else '', np.round(v,3) if rat else '')
