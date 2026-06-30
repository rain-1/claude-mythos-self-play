import numpy as np
from bisect import bisect_left, bisect_right

# ---------- Edelman-Greene insertion (word of w0 -> SYT Q of staircase) ----------
def eg_insert_word(word):
    P=[]; Q=[]
    for t,a in enumerate(word,1):
        x=a; r=0
        while True:
            if r==len(P):
                P.append([x]); Q.append([t]); break
            row=P[r]
            if x>row[-1]:
                row.append(x); Q[r].append(t); break
            j=bisect_right(row,x)      # smallest index with row[j] > x
            b=row[j]
            if b==x+1 and (j>0 and row[j-1]==x):   # special: x and x+1 both present
                x=b                                 # bump x+1, row unchanged
            else:
                row[j]=x; x=b                       # normal: replace b, bump b
            r+=1
    return P,Q

# ---------- inverse EG (SYT Q [+ known P] -> word) ----------
def eg_uninsert(P, r, c):
    v=P[r].pop(c)
    for rr in range(r-1,-1,-1):
        R=P[rr]
        if v in R:                      # SPECIAL (row kept a copy of v)
            x=v-1
        else:                           # NORMAL
            j=bisect_left(R,v)-1; x=R[j]; R[j]=v
        v=x
    return v

def word_from_Q(Q):
    # need P; reconstruct P by replaying? We know final P for w0 is P0, but to be safe
    # rebuild P from Q is not direct. Instead: we get P by EG-inserting the (unknown) word...
    # For w0, P is fixed = P0[i][j]=i+j+1. Build it from Q's shape.
    shape=[len(row) for row in Q]
    P=[[i+j+1 for j in range(shape[i])] for i in range(len(shape))]
    # positions of each value t in Q
    N=sum(shape); pos={}
    for i,row in enumerate(Q):
        for j,val in enumerate(row): pos[val]=(i,j)
    word=[]
    for t in range(N,0,-1):
        r,c=pos[t]
        word.append(eg_uninsert(P,r,c))
    return word[::-1]

# ---------- uniform SYT of staircase via GNW hook walk ----------
def staircase_cells(n):
    return [(i,j) for i in range(n-1) for j in range(n-1-i)]

def uniform_syt_staircase(n, rng):
    # shape as set of cells; fill N..1 by hook-walking to corners
    rowlen=[n-1-i for i in range(n-1)]      # current row lengths
    collen=[ (n-1)- (0) ]  # we'll compute column lengths on the fly
    cells=set(staircase_cells(n))
    N=len(cells)
    T={}
    def is_corner(i,j):
        return (i+1,j) not in cells and (i,j+1) not in cells
    cur_cells=set(cells)
    # maintain row lengths and column heights
    rlen={}; 
    for (i,j) in cur_cells: rlen[i]=max(rlen.get(i,0),j+1)
    # column heights
    def col_h(j): return max((i for (ii,jj) in cur_cells for i in [ii] if jj==j), default=-1)
    for val in range(N,0,-1):
        # pick uniform random cell
        i,j=tuple(np.array(list(cur_cells))[rng.integers(0,len(cur_cells))])
        i=int(i); j=int(j)
        while True:
            # hook of (i,j): cells to the right in row i, cells below in col j, within cur_cells
            right=[(i,jj) for jj in range(j+1, rlen.get(i,0)) if (i,jj) in cur_cells]
            below=[(ii,j) for ii in range(i+1, n-1) if (ii,j) in cur_cells]
            hook=right+below
            if not hook: break
            i,j=hook[rng.integers(0,len(hook))]
        T[(i,j)]=val
        cur_cells.discard((i,j))
        # update rlen
        rlen[i]=max((jj+1 for (ii,jj) in cur_cells if ii==i), default=0)
    # build Q as list of rows
    Q=[[T[(i,j)] for j in range(n-1-i)] for i in range(n-1)]
    return Q

# ---------- sorting network trajectories from a reduced word ----------
def trajectories(word, n):
    L=len(word); slot=list(range(n)); pos=np.zeros((n,L+1))
    pos[:,0]=slot
    where=list(range(n))   # where[label]=slot
    slot_label=list(range(n)) # slot_label[slot]=label
    for t,i in enumerate(word):  # letter i swaps slots i-1,i (1-indexed)
        a=slot_label[i-1]; b=slot_label[i]
        slot_label[i-1],slot_label[i]=b,a
        pos[a,t+1]=i; pos[b,t+1]=i-1
        for lab in range(n):
            if lab!=a and lab!=b: pos[lab,t+1]=pos[lab,t]
    return pos

def reduced_words_w0(n, limit=None):
    """enumerate reduced words of w0 by DFS (small n only)."""
    target=tuple(range(n-1,-1,-1)); N=n*(n-1)//2; out=[]
    def dfs(perm, word):
        if len(word)==N:
            out.append(tuple(word)); return
        if limit and len(out)>=limit: return
        for i in range(n-1):
            if perm[i]<perm[i+1]:   # applying s_i increases inversions (reduced)
                p2=list(perm); p2[i],p2[i+1]=p2[i+1],p2[i]
                dfs(tuple(p2), word+[i+1])
    dfs(tuple(range(n)), [])
    return out

if __name__=="__main__":
    # 1) bijection counts
    for n,exp in [(3,2),(4,16),(5,768)]:
        words=reduced_words_w0(n)
        Qs=set()
        okP=True
        P0=[[i+j+1 for j in range(n-1-i)] for i in range(n-1)]
        for w in words:
            P,Q=eg_insert_word(w)
            if P!=P0: okP=False
            Qs.add(tuple(tuple(r) for r in Q))
        print(f"S_{n}: #reduced words={len(words)} (exp {exp}? {len(words)==exp}); distinct Q={len(Qs)}; allP==P0:{okP}")
    # 2) round-trip inverse on all of S_4, S_5
    for n in [4,5]:
        words=reduced_words_w0(n); bad=0
        for w in words:
            P,Q=eg_insert_word(w)
            w2=word_from_Q(Q)
            if tuple(w2)!=w: bad+=1
        print(f"S_{n}: round-trip mismatches = {bad} / {len(words)}")
