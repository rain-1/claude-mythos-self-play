"""Enumerate Sol LeWitt's incomplete open cubes from scratch.

Constraints (MO question 508521):
  - subset of the 12 edges of the cube
  - incomplete: not all 12
  - properly 3-dimensional: contains an edge in every axis direction
  - connected (as a graph of chosen edges)
  - up to rotations (24 orientation-preserving symmetries)
Target: 122 classes.  Burnside check: ALL subsets up to rotation = 218.
Also: chirality analysis under the full group (48, with reflections).
"""
import numpy as np
from itertools import product

# vertices of cube: (x,y,z) in {0,1}^3, index = x*4+y*2+z
VERTS = [(x,y,z) for x in (0,1) for y in (0,1) for z in (0,1)]
VIDX = {v:i for i,v in enumerate(VERTS)}

# 12 edges: pairs of vertices differing in one coordinate
EDGES = []
for i,a in enumerate(VERTS):
    for j,b in enumerate(VERTS):
        if i<j and sum(abs(a[k]-b[k]) for k in range(3))==1:
            EDGES.append((i,j))
EDGES.sort()
EIDX = {e:i for i,e in enumerate(EDGES)}
assert len(EDGES)==12
# direction of each edge: axis where endpoints differ
EDIR = []
for (i,j) in EDGES:
    a,b = VERTS[i],VERTS[j]
    EDIR.append([k for k in range(3) if a[k]!=b[k]][0])
EDIR = np.array(EDIR)

def vert_perm_from_matrix(M, t):
    """vertex permutation given orthogonal matrix M and translation t (maps unit cube to itself)"""
    p = []
    for v in VERTS:
        w = tuple(int(round(x)) for x in (M @ np.array(v) + t))
        p.append(VIDX[w])
    return p

def all_symmetries(include_reflections=False):
    """all orthogonal matrices with entries in {-1,0,1} mapping the cube [0,1]^3 to itself (after translation)"""
    perms = []
    mats = []
    for perm in [(0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0)]:
        for signs in product((1,-1),repeat=3):
            M = np.zeros((3,3))
            for r,(c,s) in enumerate(zip(perm,signs)):
                M[r,c] = s
            if not include_reflections and round(np.linalg.det(M))!=1: continue
            # translation: map [0,1]^3 to itself: t_i = 1 if row has a -1
            t = np.array([1 if -1 in M[r] else 0 for r in range(3)], dtype=float)
            perms.append(vert_perm_from_matrix(M,t))
            mats.append((M,t))
    return perms, mats

def edge_perm(vp):
    ep = []
    for (i,j) in EDGES:
        a,b = vp[i],vp[j]
        ep.append(EIDX[(min(a,b),max(a,b))])
    return ep

ROT_V, ROT_M = all_symmetries(False)
FULL_V, FULL_M = all_symmetries(True)
assert len(ROT_V)==24 and len(FULL_V)==48
ROT_E = [edge_perm(vp) for vp in ROT_V]
FULL_E = [edge_perm(vp) for vp in FULL_V]

def apply_ep(mask, ep):
    m = 0
    for e in range(12):
        if mask >> e & 1: m |= 1 << ep[e]
    return m

def canon(mask, group):
    return min(apply_ep(mask, ep) for ep in group)

def connected(mask):
    es = [EDGES[e] for e in range(12) if mask>>e&1]
    if not es: return False
    parent = list(range(8))
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    for a,b in es:
        ra,rb = find(a),find(b)
        if ra!=rb: parent[ra]=rb
    roots = {find(a) for e in es for a in e}
    return len(roots)==1

def three_dim(mask):
    dirs = {EDIR[e] for e in range(12) if mask>>e&1}
    return dirs=={0,1,2}

# Burnside sanity: number of ALL edge-subsets up to rotation
orbit_all = {canon(m, ROT_E) for m in range(4096)}
print("all subsets up to rotation:", len(orbit_all), "(expect 218)")

# LeWitt enumeration
classes = {}
for m in range(4096):
    if m == 4095: continue          # incomplete
    if not three_dim(m): continue   # edge in every direction
    if not connected(m): continue   # connected
    c = canon(m, ROT_E)
    classes.setdefault(c, 0)
    classes[c] += 1
reps = sorted(classes)
print("incomplete open cubes up to rotation:", len(reps), "(expect 122)")

# per-edge-count table
from collections import Counter
cnt = Counter(bin(r).count('1') for r in reps)
print("by edge count:", dict(sorted(cnt.items())))

# chirality: classes under full group; a class is chiral if mirror not rotation-equivalent
full_classes = {canon(r, FULL_E) for r in reps}
print("classes up to rotation+reflection:", len(full_classes))
mirror_map = {}
MIR = FULL_E  # find one reflection edge-perm
refl = [ep for ep,(M,t) in zip(FULL_E, FULL_M) if round(np.linalg.det(M[0:3,0:3]))==-1][0]
chiral_pairs = []
amphichiral = []
seen = set()
for r in reps:
    mr = canon(apply_ep(r, refl), ROT_E)
    mirror_map[r] = mr
    if mr == r: amphichiral.append(r)
    else:
        if r not in seen and mr not in seen:
            chiral_pairs.append((r, mr))
            seen.add(r); seen.add(mr)
print("amphichiral (own mirror):", len(amphichiral), " chiral pairs:", len(chiral_pairs),
      " check:", len(amphichiral)+2*len(chiral_pairs))
# consistency: full-group class count should equal amphi + pairs
assert len(full_classes) == len(amphichiral)+len(chiral_pairs)
assert len(reps) == len(amphichiral)+2*len(chiral_pairs)

np.save('reps.npy', np.array(reps))
import json
json.dump({'reps':reps, 'amphichiral':amphichiral,
           'chiral_pairs':chiral_pairs, 'mirror_map':{str(k):v for k,v in mirror_map.items()},
           'by_edges':{str(k):v for k,v in sorted(cnt.items())}},
          open('enum.json','w'))
print("saved.")
