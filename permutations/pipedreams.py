from itertools import combinations

def inv(w): return sum(1 for i in range(len(w)) for j in range(i+1,len(w)) if w[i]>w[j])

def perm_from_word(word, n):
    p=list(range(1,n+1))
    for g in word: p[g-1],p[g]=p[g],p[g-1]
    return tuple(p)

def staircase_cells(n):
    # cells (i,j), i,j>=1, i+j<=n  (row i has cols 1..n-i)
    return [(i,j) for i in range(1,n) for j in range(1,n-i+1)]

def reading_word(D):
    # rows top->bottom (i asc), within row cols right->left (j desc); cross (i,j)->generator i+j-1
    return [i+j-1 for (i,j) in sorted(D, key=lambda c:(c[0],-c[1]))]

def reduced_pipe_dreams(w):
    n=len(w); L=inv(w); cells=staircase_cells(n); out=[]
    for D in combinations(cells, L):
        if perm_from_word(reading_word(D), n)==tuple(w): out.append(frozenset(D))
    return out

def trace_pipes(D, n):
    """return dict pipe_start_row -> list of (i,j) cells occupied (for drawing); pipes enter left of each row, exit top."""
    Dset=set(D)
    def is_cross(i,j): return (i,j) in Dset
    pipes={}
    for start in range(1,n+1):
        path=[]; i=start; j=0; dr=(0,1)  # start just left of (start,1), moving right
        # move into grid
        i,j=start,1; direction='R'
        # we allow the grid rows 1..n, cols 1..n; elbows outside staircase
        while 1<=i<=n and 1<=j<=n:
            path.append((i,j,direction))
            cross = is_cross(i,j)
            if cross:
                # keep direction
                if direction=='R': j+=1
                else: i-=1
            else:  # elbow: R->U, U->R
                if direction=='R': direction='U'; i-=1
                else: direction='R'; j+=1
        pipes[start]=path
    return pipes

if __name__=="__main__":
    from itertools import permutations
    # verify w0 has exactly 1 reduced pipe dream (full staircase)
    for n in [3,4,5]:
        w0=tuple(range(n,0,-1))
        pd=reduced_pipe_dreams(w0)
        print(f"S_{n} w0: #reduced pipe dreams = {len(pd)} (expect 1), size={len(next(iter(pd)))}=C(n,2)={n*(n-1)//2}")
    # counts for all of S_3, S_4 and sanity: sum over w of (#pd) equals ?
    for n in [3,4]:
        tot=0
        for w in permutations(range(1,n+1)):
            k=len(reduced_pipe_dreams(w)); tot+=k
        print(f"S_{n}: total reduced pipe dreams over all w = {tot}")
    # show counts per w in S4 (a few)
    n=4
    for w in [(1,4,3,2),(2,4,1,3),(1,3,4,2),(3,1,4,2)]:
        print(w,"-> #pipe dreams",len(reduced_pipe_dreams(w)),"inv",inv(w))
