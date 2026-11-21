import sys
M=int(sys.argv[1]); divs=[[] for _ in range(M+2)]
for d in range(1,(M+1)//2+1):
    for m in range(2*d,M+2,d): divs[m].append(d)
ev=[]; prac_miss=0
for N in range(3,M+2,2):
    ds=divs[N]
    if sum(ds)<N-1: continue
    bits=1
    for d in ds: bits|=bits<<d
    if (bits>>(N-1))&1: ev.append(N-1)
print('even camel numbers <=',M,':',len(ev),ev[:12])
