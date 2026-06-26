"""Still 4 — a Cayley diagram in 3D: the permutohedron of S4.
The 24 elements of the symmetric group S4 (= rotation group of the cube, and
24 like the 24-cell) drawn as the truncated octahedron. Each vertex is a
permutation; each edge is an adjacent transposition s1=(12), s2=(23), s3=(34),
coloured azure / gold / rose. Walking an edge = applying a generator. The
square and hexagonal faces are the relations s_i^2=1, (s_i s_{i+1})^3=1,
(s1 s3)^2=1 -- the whole group presentation, made solid."""
import numpy as np, sys, itertools
sys.path.insert(0,'triality')
import tdraw

CV=np.array([70,190,255])/255; CS=np.array([255,200,80])/255; CC=np.array([255,95,180])/255
GENCOL=[CV,CS,CC]

def build():
    perms=list(itertools.permutations(range(4)))
    idx={p:i for i,p in enumerate(perms)}
    V=np.array(perms,float)-1.5
    # 3D basis of the hyperplane sum=0
    B=np.array([[1,-1,0,0],[1,1,-2,0],[1,1,1,-3]],float)
    B=np.array([b/np.linalg.norm(b) for b in B])
    P3=V@B.T
    V4=np.concatenate([P3, np.zeros((len(P3),1))],1)
    edges=[]; ecol=[]
    for p in perms:
        for k in range(3):  # transpose consecutive VALUES k,k+1 (true permutohedron edges)
            q=tuple(k+1 if x==k else (k if x==k+1 else x) for x in p)
            i,j=idx[p],idx[q]
            if i<j: edges.append((i,j)); ecol.append(GENCOL[k])
    return V4, edges, ecol

def render(S=2048, ss=2, preview=False):
    V4,edges,ecol=build()
    R3=tdraw.rot3(1,2,0.42)@tdraw.rot3(0,2,0.25)
    vcols=[np.array([0.85,0.9,1.0]) for _ in range(len(V4))]
    return tdraw.render_4d(V4,edges,[0]*len(V4),S=S,ss=ss,R3=R3,scale_frac=0.95,
        edge_bright=0.5,vtx_bright=0.8,vtx_r_frac=0.006,gloss=(0.35,0.22),expo=1.18,
        edge_w=1.7,bloom_frac=(0.0006,0.005),colors=vcols,edge_colors=ecol,
        bg=(0.012,0.012,0.026))

if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=='preview':
        render(750,2).save('triality/proto/_cayley.png')
    else:
        render(2048,2).save('triality/04_permutohedron_cayley_s4.png')
    print('done')
