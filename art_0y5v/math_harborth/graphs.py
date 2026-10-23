"""Graph definitions with float reference plane drawings (used only to read off the faces)."""
import math
def octahedron():
    edges=[(0,1),(1,2),(0,2),(3,4),(4,5),(3,5),(3,1),(3,2),(4,0),(4,2),(5,0),(5,1)]
    ref=[(0,10),(-8.66,-5),(8.66,-5),(0,-2),(1.7,1),(-1.7,1)]
    return 6,edges,ref
def icosahedron():
    EDGES = [(0,1),(0,2),(1,2),(9,10),(10,11),(9,11),
         (3,4),(4,5),(5,6),(6,7),(7,8),(8,3),
         (0,3),(0,4),(0,5),(1,5),(1,6),(1,7),(2,7),(2,8),(2,3),
         (9,4),(9,5),(9,6),(10,6),(10,7),(10,8),(11,8),(11,3),(11,4)]
    P={}
    for i in range(3): P[i]=(10*math.cos(math.radians(90+120*i)),10*math.sin(math.radians(90+120*i)))
    for j in range(6): P[3+j]=(4*math.cos(math.radians(90+60*(j-1))),4*math.sin(math.radians(90+60*(j-1))))
    for i in range(3): P[9+i]=(1.5*math.cos(math.radians(150+120*i)),1.5*math.sin(math.radians(150+120*i)))
    ref=[(-x,y) for x,y in [P[i] for i in range(12)]]
    return 12,EDGES,ref
def pent_bipyramid():
    # equator 0..4 (pentagon), apex 5 inside, apex 6 outside -> outer face must be a triangle: use apex 6 + edge (0,1)
    edges=[(i,(i+1)%5) for i in range(5)]+[(i,5) for i in range(5)]+[(i,6) for i in range(5)]
    # drawing: outer triangle 6,0,1 ; vertices 2,3,4 inside, 5 inside pentagon
    ref=[(-6,-4),(6,-4),(4,1),(0,3),(-4,1),(0,-0.5),(0,12)]
    return 7,edges,ref
def tutte(n, edges, outer):
    import numpy as np
    adj=[set() for _ in range(n)]
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    P=np.zeros((n,2)); fixed={}
    for i,v in enumerate(outer):
        fixed[v]=(10*math.cos(2*math.pi*i/3+math.pi/2),10*math.sin(2*math.pi*i/3+math.pi/2))
    A=np.zeros((n,n)); bx=np.zeros(n); by=np.zeros(n)
    for v in range(n):
        if v in fixed: A[v,v]=1; bx[v],by[v]=fixed[v]
        else:
            A[v,v]=len(adj[v])
            for u in adj[v]: A[v,u]-=1
    return [(float(x),float(y)) for x,y in zip(np.linalg.solve(A,bx),np.linalg.solve(A,by))]
def snub_disphenoid_old():
    # 8 vertices, 18 edges, degrees 4,4,4,4,5,5,5,5. Built as: two degree-4 'tips' ... from coordinates via convex hull
    import itertools
    import numpy as np
    from scipy.spatial import ConvexHull
    q=0.169530; r=math.sqrt(q); s=math.sqrt(2-2*q); t=math.sqrt(2*q+2)
    s3=math.sqrt(3)
    # standard coordinates (Wikipedia): (+-t, r, 0), (0, -r, +-t)?? use generic ones
    pts=[(t,r,0),(-t,r,0),(0,-r,t),(0,-r,-t),(1,-s,0),(-1,-s,0),(0,s,1),(0,s,-1)]
    h=ConvexHull(np.array(pts))
    E=set()
    for f in h.simplices:
        for a,b in itertools.combinations(sorted(f),2): E.add((int(a),int(b)))
    return 8,sorted(E),None
def snub_disphenoid():
    import itertools, numpy as np
    from scipy.spatial import ConvexHull
    q=float(np.real([x for x in np.roots([2,11,4,-1]) if 0<x.real<1][0])); r=math.sqrt(q); s=math.sqrt((1-q)/(2*q)); t=2*r*s
    pts=[(t,r,0),(-t,r,0),(0,-r,t),(0,-r,-t),(1,-s,0),(-1,-s,0),(0,s,1),(0,s,-1)]
    h=ConvexHull(np.array(pts)); E=set()
    for f in h.simplices:
        for a,b in itertools.combinations(sorted(f),2): E.add((int(a),int(b)))
    E=sorted(E); f0=[int(x) for x in h.simplices[0]]
    return 8,E,tutte(8,E,f0)
def triakis_tetrahedron():
    # K4 on 0..3 plus a degree-3 vertex in each face; outer face is one stacked triangle
    edges=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
    faces=[(0,1,2),(0,1,3),(0,2,3),(1,2,3)]
    for i,f in enumerate(faces):
        for v in f: edges.append((v,4+i))
    return 8,edges,tutte(8,edges,(0,1,4))
def k4():
    return 4,[(0,1),(1,2),(0,2),(0,3),(1,3),(2,3)],[(0,10),(-9,-5),(9,-5),(0,0)]
def snub_disphenoid_m():
    n,E,_=snub_disphenoid()
    return n,E,tutte(n,E,(0,6,7))
