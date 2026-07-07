"""
PIECE 3 :: THE FEWEST FLIPS  (the Tamari lattice / associahedron)
Triangulations of a convex polygon, connected by a single diagonal FLIP.
Oriented by the Tamari rule (right rotation of the associated binary tree) this
flip graph becomes a LATTICE -- the 1-skeleton of the associahedron.  We draw
the Hasse diagram: every node is a little triangulated polygon, stacked by
height (flips from the minimal fan), edges = flips coloured by the diagonal
introduced.  Out of C_n ways to associate, the cost 'number of flips' imposes a
single graded order with one bottom (all-left) and one top (all-right).
"""
import numpy as np, time, sys
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

# ---- binary trees with n internal nodes (nested tuples; None = leaf) ----
def gen_trees(n):
    if n==0:
        yield None; return
    for i in range(n):
        for L in gen_trees(i):
            for R in gen_trees(n-1-i):
                yield (L,R)

def leaves(t):
    if t is None: return 1
    return leaves(t[0])+leaves(t[1])

# ---- triangulation (diagonal set) from a binary tree on polygon 0..m-1 ----
def tri_diagonals(t, a, b, out):
    """sub-polygon on vertices a..b, root edge (a,b). record internal diagonals."""
    if t is None:            # single edge, no triangle
        return
    L,R=t
    k=a+leaves(L)            # apex
    if k-a>=2: out.add((a,k) if a<k else (k,a))
    if b-k>=2: out.add((k,b) if k<b else (b,k))
    tri_diagonals(L,a,k,out)
    tri_diagonals(R,k,b,out)

def tree_to_diags(t,m):
    out=set(); tri_diagonals(t,0,m-1,out); return frozenset(out)

# ---- Tamari covers via right rotation (upward) ----
def covers(t):
    if t is None: return
    L,R=t
    if L is not None:
        LL,LR=L
        yield (LL,(LR,R))
    for L2 in covers(L): yield (L2,R)
    for R2 in covers(R): yield (L,R2)

def build_lattice(n):
    trees=list(gen_trees(n)); m=n+2
    index={t:i for i,t in enumerate(trees)}
    N=len(trees)
    up=[[] for _ in range(N)]        # i -> list of covers above
    indeg=[0]*N
    for i,t in enumerate(trees):
        for c in set(covers(t)):
            j=index[c]; up[i].append(j); indeg[j]+=1
    # height = longest path from a source (indeg 0) via topological order
    # compute longest path to each node
    from collections import deque
    order=[]; deg=indeg[:]
    dq=deque([i for i in range(N) if deg[i]==0])
    ht=[0]*N
    while dq:
        i=dq.popleft(); order.append(i)
        for j in up[i]:
            if ht[i]+1>ht[j]: ht[j]=ht[i]+1
            deg[j]-=1
            if deg[j]==0: dq.append(j)
    diags=[tree_to_diags(t,m) for t in trees]
    edges=[(i,j) for i in range(N) for j in up[i]]
    return trees,diags,ht,edges,m

# ---- layout: layered by height, ordered within layer by barycentre ----
def layout(N,ht,edges):
    H=max(ht)+1
    layers=[[] for _ in range(H)]
    for i in range(N): layers[ht[i]].append(i)
    adj=[[] for _ in range(N)]
    for i,j in edges: adj[i].append(j); adj[j].append(i)
    pos=[0.0]*N
    for L in layers:
        for k,i in enumerate(L): pos[i]=k
    for sweep in range(220):
        # alternate median (odd) and barycentre (even) sweeps for crossing reduction
        use_med = (sweep%2==0)
        rng_layers = layers if sweep%4<2 else layers[::-1]
        for L in rng_layers:
            for i in L:
                nb=[pos[j] for j in adj[i]]
                if nb:
                    val=np.median(nb) if use_med else np.mean(nb)
                    pos[i]=0.8*val+0.2*pos[i]
        for L in layers:
            order=sorted(L,key=lambda i:pos[i])
            for k,i in enumerate(order): pos[i]=k - (len(L)-1)/2.0
    xy=np.zeros((N,2))
    for r,L in enumerate(layers):
        for i in L:
            xy[i,0]=pos[i]
            xy[i,1]=r
    # normalize
    xy[:,0]=(xy[:,0]-xy[:,0].min())/(np.ptp(xy[:,0])+1e-9)
    xy[:,1]=xy[:,1]/(H-1)
    return xy,layers

def poly_pts(cx,cy,rad,m,rot=-np.pi/2):
    a=rot+np.arange(m)*2*np.pi/m
    return np.c_[cx+rad*np.cos(a), cy+rad*np.sin(a)]

def diag_color(d,m):
    # colour by the "span" of the diagonal (short chords cool, long chords warm)
    i,j=d; span=min((j-i)%m,(i-j)%m)
    t=(span-2)/max(1,(m//2-2)) if m//2>2 else 0.5
    import colorsys
    r,g,b=colorsys.hsv_to_rgb(0.58-0.5*t,0.55,1.0)
    return (r,g,b)

def render(n=5, S=1600, save=None):
    trees,diags,ht,edges,m=build_lattice(n)
    N=len(trees)
    xy,layers=layout(N,ht,edges)
    print(f"  n={n} m-gon={m} N={N} (Catalan) height={max(ht)}",flush=True)
    sup=2; Sp=S*sup
    img=Image.new('RGB',(Sp,Sp),(4,4,10))
    dr=ImageDraw.Draw(img,'RGBA')
    mar=0.09*Sp
    def P(i):
        return (mar+xy[i,0]*(Sp-2*mar), (Sp-mar)-xy[i,1]*(Sp-2*mar))
    # glyph radius from layer spacing
    maxlayer=max(len(L) for L in layers)
    rad=min( (Sp-2*mar)/(maxlayer)*0.48, (Sp-2*mar)/(max(ht))*0.40 )
    # edges first (coloured by the diagonal that changes)
    for i,j in edges:
        added=diags[j]-diags[i]
        col=diag_color(next(iter(added)),m) if added else (0.6,0.6,0.6)
        x1,y1=P(i); x2,y2=P(j)
        dr.line([(x1,y1),(x2,y2)],fill=(int(255*col[0]),int(255*col[1]),int(255*col[2]),70),width=max(1,int(1.3*sup)))
    # nodes: triangulated polygon glyphs, faintly tinted by height (poset depth)
    import colorsys
    Hmax=max(ht)
    for i in range(N):
        cx,cy=P(i)
        pv=poly_pts(cx,cy,rad,m)
        h=ht[i]/max(1,Hmax)
        fr,fg,fb=colorsys.hsv_to_rgb(0.62-0.5*h,0.45,0.55)  # low=indigo, high=amber
        dr.polygon([tuple(p) for p in pv],
                   fill=(int(40*fr+6),int(40*fg+6),int(46*fb+12),255),
                   outline=(170,178,205,235))
        dr.line([tuple(p) for p in list(pv)+[pv[0]]],fill=(175,183,210,240),width=max(1,int(0.9*sup)))
        for (a,b) in diags[i]:
            col=diag_color((a,b),m)
            dr.line([tuple(pv[a]),tuple(pv[b])],
                    fill=(int(255*col[0]),int(255*col[1]),int(255*col[2]),255),width=max(1,int(1.25*sup)))
    arr=np.asarray(img).astype(np.float32)/255
    bloom=gaussian_filter(arr,(Sp/700,Sp/700,0))
    arr=np.clip(arr+0.35*bloom,0,1)
    out=Image.fromarray((arr*255).astype(np.uint8)).resize((S,S),Image.LANCZOS)
    if save: out.save(save); print("  ->",save,flush=True)
    return out

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='final':
        render(5,2048,save='/home/user/claude-mythos-self-play/art_bcm8/03_the_fewest_flips.png')
    else:
        for n in [4,5]:
            render(n,1200,save=f'/home/user/claude-mythos-self-play/art_bcm8/prev_tamari_{n}.png')
