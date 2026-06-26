"""Still 6 — the 24-cell is three interlocking 16-cells.
Its 24 vertices split into three 16-cells (4-orthoplexes / cross-polytopes) of
8 vertices each: 8_v, 8_s, 8_c. Drawing each 16-cell with its OWN edges (every
pair of non-antipodal vertices) gives three interpenetrating jewels, azure /
gold / rose. Triality is the rotation that carries each onto the next."""
import numpy as np, sys, itertools
sys.path.insert(0,'triality')
import t4d, tdraw

def intra_edges(V, cls):
    E=[]; EC=[]
    for c in (0,1,2):
        idx=[i for i in range(len(V)) if cls[i]==c]
        for a in range(len(idx)):
            for b in range(a+1,len(idx)):
                i,j=idx[a],idx[b]
                if np.linalg.norm(V[i]+V[j])>1e-6:   # skip antipodal pairs
                    E.append((i,j)); EC.append(tdraw.CLASS_COL[c])
    return E,EC

def render(S=2048, ss=2, R4=None, R3=None):
    V,cls=t4d.cell24_weights()
    E,EC=intra_edges(V,cls)
    if R4 is None: R4=tdraw.rot4(0,3,0.62)@tdraw.rot4(1,2,0.42)
    if R3 is None: R3=tdraw.rot3(0,1,0.25)@tdraw.rot3(1,2,-0.5)
    return tdraw.render_4d(V,E,cls,S=S,ss=ss,R4=R4,R3=R3,scale_frac=1.5,
        edge_bright=0.34,vtx_bright=0.85,vtx_r_frac=0.0058,gloss=(0.35,0.22),
        expo=1.16,edge_w=1.3,bloom_frac=(0.0006,0.005),edge_colors=EC,
        zrange=(-0.6,0.6))

if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=='preview':
        render(750,2).save('triality/proto/_16c.png')
    else:
        render(2048,2).save('triality/06_three_interlocking_16cells.png')
    print('done')
