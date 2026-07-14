"""Steffen flex + Bellows verification (uses self-contained topology)."""
import numpy as np
from art_50e7.steffen_flex import config, EDGES, FACES, volume, elens

if __name__=='__main__':
    ts=np.linspace(-0.30,0.30,201); prevV=None; Vols=[]; Ls=[]; travel=[]
    L0=elens(config(0.0)); base=config(0.0)
    for t in ts:
        V=config(t, prev={k+1:prevV[k] for k in range(9)} if prevV is not None else None)
        prevV=V; Vols.append(abs(volume(V))); Ls.append(elens(V)); travel.append(np.linalg.norm(V-base))
    Vols=np.array(Vols); Ls=np.array(Ls)
    print("edges %d faces %d  Euler V-E+F=%d"%(len(EDGES),len(FACES),9-len(EDGES)+len(FACES)))
    print("edge-length max drift: %.2e"%np.abs(Ls-L0).max())
    print("volume: min %.5f max %.5f spread %.2e"%(Vols.min(),Vols.max(),Vols.max()-Vols.min()))
    print("config travel: max %.4f"%max(travel))
    dmin=min(np.linalg.norm(config(t)[a]-config(t)[b]) for t in ts for a in range(9) for b in range(a+1,9))
    print("min vertex separation: %.4f"%dmin)
