# Independent checker: verify.py file.json  (file = list of d vertex-lists)  or  verify.py solutions.json
import sys, json
def check(cycles):
    d=len(cycles); n=1<<d; arcs=set()
    for c in cycles:
        assert len(c)==n and sorted(c)==list(range(n)), 'not a Hamiltonian vertex sequence'
        for k in range(n):
            a,b=c[k],c[(k+1)%n]; x=a^b
            assert x and x&(x-1)==0 and x<n, 'not a cube edge'
            assert (a,b) not in arcs, 'arc repeated'
            arcs.add((a,b))
    assert len(arcs)==d*n
    return d
J=json.load(open(sys.argv[1]))
if isinstance(J,dict):
    for k,v in J.items():
        if k=='d4_orbit_representatives':
            for r in v: assert check(r['cycles'])==4
            print('d=4:',len(v),'orbit representatives all valid decompositions')
        elif k=='d5_all_shift_invariant_orbit_reps':
            rho=lambda x,j:((x<<j)|(x>>(5-j)))&31
            for r in v: assert check([[rho(x,j) for x in r['C']] for j in range(5)])==5
            print('d=5:',len(v),'shift-invariant orbit representatives all valid')
        elif k[0]=='d' and k[1:].isdigit():
            sol=v
            print(k,': valid decomposition into',check(sol),'directed Hamiltonian cycles')
else: print('valid decomposition, d =',check(J))
