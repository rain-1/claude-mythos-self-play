def maj(w): return sum(i+1 for i in range(len(w)-1) if w[i]>w[i+1])
def inv(w): return sum(1 for i in range(len(w)) for j in range(i+1,len(w)) if w[i]>w[j])

def foata(w):
    """Foata's second fundamental transformation: inv(foata(w)) == maj(w)."""
    w=list(w)
    if not w: return []
    v=[w[0]]
    for a in w[1:]:
        if v[-1]<=a:
            # split after each element <= a, cyclic-shift each block (last->front), then append a
            blocks=[]; cur=[]
            for y in v:
                cur.append(y)
                if y<=a: blocks.append(cur); cur=[]
            if cur: blocks.append(cur)
        else:
            blocks=[]; cur=[]
            for y in v:
                cur.append(y)
                if y>a: blocks.append(cur); cur=[]
            if cur: blocks.append(cur)
        v=[]
        for blk in blocks:
            v += [blk[-1]]+blk[:-1]
        v.append(a)
    return v

if __name__=="__main__":
    from itertools import permutations
    for n in range(1,8):
        bad=0; seen=set()
        for p in permutations(range(1,n+1)):
            fp=tuple(foata(p)); seen.add(fp)
            if inv(fp)!=maj(p): bad+=1
        print(f"S_{n}: inv(foata)==maj mismatches {bad}, bijection(distinct images)={len(seen)}=={len(list(permutations(range(1,n+1))))}")
