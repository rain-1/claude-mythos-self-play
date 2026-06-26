"""Still 3 — the 24-cell, geometric home of triality (3D hero).
The unique self-dual regular 4-polytope: 24 vertices, 96 edges, 24 octahedral
cells. Its vertices are the three 16-cells 8_v / 8_s / 8_c; the symmetry that
cycles them is triality. A 4D->3D->2D projection, glowing."""
import numpy as np, sys
sys.path.insert(0,'triality')
import t4d, tdraw

def render(S=4096, ss=2):
    V,cls=t4d.cell24_weights(); E,_=t4d.edges_of(V)
    # near-symmetric 'hexagonal' projection, slightly tilted for depth
    R4=tdraw.rot4(0,3,np.pi/4)@tdraw.rot4(1,2,np.pi/4)@tdraw.rot4(0,1,0.10)
    R3=tdraw.rot3(1,2,-0.40)@tdraw.rot3(0,2,0.12)
    return tdraw.render_4d(V,E,cls,S=S,ss=ss,R4=R4,R3=R3,scale_frac=1.55,
        edge_bright=0.5,vtx_bright=0.82,vtx_r_frac=0.0055,gloss=(0.35,0.22),
        expo=1.15,edge_w=1.35,bloom_frac=(0.0006,0.005),zrange=(-0.6,0.6))

if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=='preview':
        render(750,2).save('triality/proto/_hero.png')
    else:
        render(4096,2).save('triality/03_the_24cell.png')
    print('done')
