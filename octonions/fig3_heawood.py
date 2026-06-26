"""Figure 3 — the Heawood graph: the Fano plane as incidence (graph-theory lens).
14 nodes = 7 points + 7 lines; an edge joins a point to each line through it.
This is the (3,6)-cage: 3-regular, girth 6, the smallest such graph. Drawn on a
Hamiltonian cycle so the point<->line duality of the Fano plane is laid bare."""
import numpy as np, sys, math
sys.path.insert(0,'octonions'); sys.path.insert(0,'triality')
import octo, figkit
from tdraw import Canvas

def incidence():
    P=list(range(1,8)); L=octo.LINES
    # node ids: 0..6 points, 7..13 lines
    adj={i:set() for i in range(14)}
    for li,line in enumerate(L):
        for p in line:
            pi=p-1; lj=7+li
            adj[pi].add(lj); adj[lj].add(pi)
    return adj

def hamiltonian(adj):
    n=14; path=[0]; used={0}
    def dfs():
        if len(path)==n:
            return path[-1] in adj[path[0]]
        for nb in adj[path[-1]]:
            if nb not in used:
                used.add(nb); path.append(nb)
                if dfs(): return True
                used.remove(nb); path.pop()
        return False
    dfs(); return path

def render(W=1600):
    adj=incidence(); cyc=hamiltonian(adj)
    pos={}
    R=W*0.40; cx=cy=W/2
    for k,v in enumerate(cyc):
        a=2*math.pi*k/14 - math.pi/2
        pos[v]=(cx+R*math.cos(a), cy+R*math.sin(a))
    cv=Canvas(W,bg=(0.012,0.013,0.024))
    cyc_set=set()
    for k in range(14):
        cyc_set.add(frozenset((cyc[k],cyc[(k+1)%14])))
    WARM=np.array([255,180,70])/255; COOL=np.array([90,200,255])/255; CH=np.array([255,110,180])/255
    # edges: Hamiltonian cycle (bright neutral) + chords (rose)
    drawn=set()
    for u in range(14):
        for v in adj[u]:
            e=frozenset((u,v))
            if e in drawn: continue
            drawn.add(e)
            p,q=pos[u],pos[v]
            if e in cyc_set:
                cv.line(p,q,(0.8,0.85,1.0),(0.8,0.85,1.0),width=2.2,bright=0.5)
            else:
                cv.line(p,q,CH,CH,width=2.2,bright=0.45)
    # nodes: points warm squares-ish (disk), lines cool
    for v in range(14):
        col=WARM if v<7 else COOL
        cv.splat(pos[v],col,radius=W*0.012,bright=1.6)
        cv.splat(pos[v],(1,1,1),radius=W*0.004,bright=1.3)
    img=cv.finish(W,bloom=(W*0.0007+0.6,W*0.006),gloss=(0.5,0.3),expo=1.2)
    # labels
    from PIL import ImageDraw
    d=ImageDraw.Draw(img); f=figkit.font("DejaVuSans-Bold.ttf",30)
    for v in range(14):
        x,y=pos[v]; dirv=np.array([x-cx,y-cy]); dirv=dirv/(np.linalg.norm(dirv)+1e-9)
        lx,ly=x+dirv[0]*46, y+dirv[1]*46
        lab=(octo.sub(v+1) if v<7 else "L"+str(v-6))
        col=(255,200,120) if v<7 else (130,210,255)
        w=d.textlength(lab,font=f); d.text((lx-w/2,ly-18),lab,font=f,fill=col)
    return img

if __name__=="__main__":
    viz=render(1600)
    body=("Draw a dot for each of the 7 points (e₁…e₇, warm) and each of the 7 lines (L1…L7, cool) "
          "of the Fano plane, and connect a point to every line that passes through it. Because "
          "each point lies on 3 lines and each line holds 3 points, every node has exactly 3 "
          "edges. The result is the HEAWOOD GRAPH — the unique (3,6)-cage: the smallest 3-regular "
          "graph with no cycle shorter than 6. Its perfect symmetry encodes the Fano plane's "
          "self-duality (swap 'point' and 'line' and nothing changes); its automorphism group is "
          "PGL(2,7) of order 336, and it is the smallest graph that needs a torus, not a plane, to "
          "be drawn without crossings.")
    fig=figkit.caption(viz,"FIGURE 3 · GRAPH THEORY","The Heawood graph — Fano incidence",
                       body,accent=(255,150,90))
    figkit.save(fig,"octonions/03_heawood_graph.png")
    print("done",fig.size)
