import sys, math
sys.path.insert(0,'.'); from pin_check import orbits
n=int(sys.argv[1]); O=orbits(n); nb=n*n
# reproduce C orbit order: C iterates cells row-major, orbit order same as pin_check (row-major first cell) 
vals=[sum(1<<(nb-1-(a*n+b)) for a,b in o) for o in O]
forced={}
for k,o in enumerate(O):
    cells=[a*n+b for a,b in o]
    if 0 in cells: forced[k]=1
    if nb-2 in cells or nb-3 in cells: forced[k]=0
base=sum(vals[k] for k,v in forced.items() if v==1)
cnt=sq=0
for f in sys.argv[2:]:
    fr=None
    for line in open(f):
        if line.startswith('FREE'): fr=list(map(int,line.split()[1:]))
        elif line.startswith('SURV'):
            mk=int(line.split()[1]); N=base+sum(vals[fr[i]] for i in range(len(fr)) if mk>>i&1)
            cnt+=1; r=math.isqrt(N)
            if r*r==N: sq+=1; print('SQUARE',N)
print('checked',cnt,'squares',sq)
