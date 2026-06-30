import numpy as np
from bisect import bisect_right

def rsk_P(perm):
    P=[]
    for x in perm:
        r=0; v=x
        while True:
            if r==len(P): P.append([v]); break
            row=P[r]; j=bisect_right(row,v)
            if j==len(row): row.append(v); break
            row[j],v=v,row[j]; r+=1
    return P

def shadow_lines(points):
    """points list of (x,y). Repeatedly peel SW-minimal antichain (Pareto frontier toward SW).
       Each line returned as list of (x,y) sorted by x ascending (=> y descending)."""
    pts=set(points); lines=[]
    while pts:
        # minimal points: no q with q.x<p.x and q.y<p.y
        cur=[]
        for p in pts:
            if not any((q[0]<p[0] and q[1]<p[1]) for q in pts):
                cur.append(p)
        cur.sort()
        lines.append(cur)
        for p in cur: pts.discard(p)
    return lines

def viennot_P(perm):
    """build P row by row via shadow lines + NE corners recursion; return rows (each a sorted list)."""
    n=len(perm)
    points=[(i+1, perm[i]) for i in range(n)]
    rows=[]
    while points:
        lines=shadow_lines(points)
        # row entry per line = min y on that line (the lowest point)
        row=sorted(min(p[1] for p in line) for line in lines)
        rows.append(row)
        # NE corners: for each line sorted by x asc (y desc), corner (x_{i+1}, y_i)
        corners=[]
        for line in lines:
            L=sorted(line)  # x asc
            for a in range(len(L)-1):
                corners.append((L[a+1][0], L[a][1]))
        points=corners
    return rows

if __name__=="__main__":
    from itertools import permutations
    import random
    bad=0; tot=0
    for n in range(1,8):
        for perm in permutations(range(1,n+1)):
            tot+=1
            if viennot_P(list(perm))!=rsk_P(list(perm)): bad+=1
    print(f"exhaustive S1..S7: viennot_P == rsk_P mismatches = {bad}/{tot}")
    # spot random larger
    rng=random.Random(0); b2=0
    for _ in range(300):
        p=list(range(1,40)); rng.shuffle(p)
        if viennot_P(p)!=rsk_P(p): b2+=1
    print("random n=39 x300 mismatches:",b2)
