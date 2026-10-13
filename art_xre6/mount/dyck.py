def sym_prim(nmax):
    """all symmetric primitive Dyck paths with area<=nmax, as full height lists"""
    out={}
    # half path: P0=0,P1=1, P_j>=1, area = 2*sum_{j<h}P_j + P_h
    def rec(path, s):   # s = sum of path[:-1]... compute on the fly
        h=len(path)-1
        a=2*sum(path[:-1])+path[-1]
        if h>=1 and a<=nmax:
            full=path+path[-2::-1]
            out.setdefault(a,[]).append(full)
        # extend
        last=path[-1]
        base=2*sum(path)  # area lower bound for any extension: 2*sum(path)+next
        for nxt in (last+1,last-1):
            if nxt>=1 and base+nxt<=nmax: rec(path+[nxt],0)
    rec([0,1],0)
    return out
if __name__=='__main__':
    o=sym_prim(80)
    print([len(o.get(n,[])) for n in range(81)])
