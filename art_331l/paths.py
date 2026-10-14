# enumerate all simple paths between opposite corners of an m x m grid graph
import numpy as np, sys
def grid_paths(m):
    N=m*m; adj=[[] for _ in range(N)]
    for y in range(m):
        for x in range(m):
            v=y*m+x
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                X,Y=x+dx,y+dy
                if 0<=X<m and 0<=Y<m: adj[v].append(Y*m+X)
    out=[]; seen=[False]*N; path=[0]; seen[0]=True
    def dfs(v):
        if v==N-1: out.append(list(path)); return
        for w in adj[v]:
            if not seen[w]:
                seen[w]=True; path.append(w); dfs(w); path.pop(); seen[w]=False
    dfs(0); return out
if __name__=="__main__":
    for m in range(2,6): print(m,len(grid_paths(m)))
