import numpy as np, time
from bigcount import connected_count, planar_connected_count, burnside
from platonic import rot_group_from_verts

phi = (1+np.sqrt(5))/2
# icosahedron: cyclic perms of (0, ±1, ±phi)
ICO_V = []
for s1 in (1,-1):
    for s2 in (1,-1):
        base = (0, s1*1.0, s2*phi)
        for cyc in range(3):
            ICO_V.append(tuple(np.roll(base, cyc)))
ICO_V = list(dict.fromkeys(ICO_V))
D = np.linalg.norm(np.array(ICO_V)[:,None,:]-np.array(ICO_V)[None,:,:],axis=2)
mind = D[D>1e-9].min()
ICO_E = [(i,j) for i in range(len(ICO_V)) for j in range(i+1,len(ICO_V)) if abs(D[i,j]-mind)<1e-6]
print("icosa: verts", len(ICO_V), "edges", len(ICO_E))

# dodecahedron: (±1,±1,±1) + cyclic perms of (0, ±1/phi, ±phi)
DOD_V = [(x,y,z) for x in (1,-1) for y in (1,-1) for z in (1,-1)]
for s1 in (1,-1):
    for s2 in (1,-1):
        base = (0, s1/phi, s2*phi)
        for cyc in range(3):
            DOD_V.append(tuple(np.roll(base, cyc)))
DOD_V = list(dict.fromkeys([tuple(np.round(v,9)) for v in DOD_V]))
D2 = np.linalg.norm(np.array(DOD_V)[:,None,:]-np.array(DOD_V)[None,:,:],axis=2)
mind2 = D2[D2>1e-9].min()
DOD_E = [(i,j) for i in range(len(DOD_V)) for j in range(i+1,len(DOD_V)) if abs(D2[i,j]-mind2)<1e-6]
print("dodeca: verts", len(DOD_V), "edges", len(DOD_E))

for V,E,name,exp_ in [(ICO_V,ICO_E,'icosahedron',16096166), (DOD_V,DOD_E,'dodecahedron',2423206)]:
    t0=time.time()
    vperms = rot_group_from_verts(V,E)
    print(f"{name}: |rot group| = {len(vperms)}  ({time.time()-t0:.1f}s)")
    t0=time.time()
    nc = connected_count(len(V), E)
    print(f"{name}: N_conn = {nc}  ({time.time()-t0:.1f}s)")
    t0=time.time()
    pl = planar_connected_count(V,E,kmax=7)
    print(f"{name}: planar connected = {pl}  ({time.time()-t0:.1f}s)")
    t0=time.time()
    burnside(V,E,vperms,nc,pl,name,exp_)
    print(f"  burnside: {time.time()-t0:.1f}s")
