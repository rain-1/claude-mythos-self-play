from analyze import *
import math
for n in range(5,14):
    S=set(tuple(map(int,l.split())) for l in open(f'sols_{n}.txt'))
    if not S: continue
    shiftb=sum(all(tuple((x+b)%n for x in q) in S for b in range(n)) for q in S)
    neg=sum(tuple((-x)%n for x in q) in S for q in S)
    negcomp=sum(tuple((-x)%n for x in q[::-1]) in S for q in S)
    inv=sum(tuple(sorted(range(n),key=lambda j:q[j])) in S for q in S)
    print(n,len(S),'closed under all b-shifts:',shiftb,'neg:',neg,'inverse perm:',inv)
    if n in (7,8,9): 
        for q in sorted(S):
            if not linear(q): print('  ',q)
