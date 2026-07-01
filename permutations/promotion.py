def promotion(T):
    T=dict(T); n=len(T)
    # cell with value 1
    hole=[c for c,v in T.items() if v==1][0]; del T[hole]
    r,c=hole
    while True:
        right=T.get((r,c+1)); down=T.get((r+1,c))
        if right is None and down is None: break
        if down is None or (right is not None and right<down):
            T[(r,c)]=right; del T[(r,c+1)]; c+=1
        else:
            T[(r,c)]=down; del T[(r+1,c)]; r+=1
    for k in list(T): T[k]-=1
    T[(r,c)]=n
    return T

def all_syt(shape):
    """all standard Young tableaux of given shape (list of row lengths)."""
    cells=[(r,c) for r in range(len(shape)) for c in range(shape[r])]
    n=len(cells); res=[]
    def rec(T, k):
        if k>n: res.append(dict(T)); return
        for (r,c) in cells:
            if (r,c) in T: continue
            if (r-1,c) in cells and (r-1,c) not in T: continue
            if (r,c-1) in cells and (r,c-1) not in T: continue
            T[(r,c)]=k; rec(T,k+1); del T[(r,c)]
    rec({},1); return res

def orbit(T):
    seen=[dict(T)]; U=promotion(T)
    while U!=seen[0]:
        seen.append(dict(U)); U=promotion(U)
    return seen

if __name__=="__main__":
    for shape in [(2,2),(3,3),(4,3),(2,2,2)]:
        syts=all_syt(shape); n=sum(shape)
        images={frozenset(T.items()):frozenset(promotion(T).items()) for T in syts}
        bij=len(set(images.values()))==len(syts)
        lens=sorted(set(len(orbit(T)) for T in syts))
        def powid(T):
            U=dict(T)
            for _ in range(n): U=promotion(U)
            return U==T
        rect = len(set(shape))==1
        print(f"shape {shape} (n={n}): #SYT={len(syts)}, bijection={bij}, orbit lengths={lens}, promotion^n==id: {all(powid(T) for T in syts)} (rectangle:{rect})")
