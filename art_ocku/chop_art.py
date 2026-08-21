import json
from collections import deque
from chopsticks import solve

states, sidx, val, succ, winmove = solve('A')
N = len(states)
# DTM: recompute retrograde with depths
depth = [0]*N
deg = [0]*N
pred = [[] for _ in range(N)]
for i in range(N):
    for j in succ[i]: pred[j].append(i)
val2 = [0]*N
q = deque()
for i,(m,o,mcd,ocd) in enumerate(states):
    if m == (0,0):
        val2[i] = -1; depth[i] = 0; q.append(i)
    elif winmove[i]:
        val2[i] = 1; depth[i] = 1; q.append(i)
    else:
        deg[i] = len(succ[i])
        if deg[i]==0: val2[i]=-1; depth[i]=0; q.append(i)
while q:
    j = q.popleft()
    for i in pred[j]:
        if val2[i] != 0: continue
        if val2[j] == -1:
            val2[i] = 1; depth[i] = depth[j]+1; q.append(i)
        else:
            deg[i] -= 1
            if deg[i] == 0:
                val2[i] = -1; depth[i] = depth[j]+1; q.append(i)
assert val2 == val
print("max depth:", max(depth[i] for i in range(N) if val[i]!=0))
start = sidx[((1,1),(1,1),0,0)]
print("start value:", val[start])
# opening analysis: value of each successor (from opponent's perspective)
def describe(i):
    m,o,mcd,ocd = states[i]
    return f"m={m} o={o} cd={mcd}{ocd}"
print("start moves:")
for j in succ[start]:
    # val[j] is from the NEXT mover's perspective: +1 means next player wins => this move LOSES for player 1
    tag = {1:'LOSES (opponent wins)', -1:'WINS', 0:'keeps the draw'}[val[j]]
    print("  ->", describe(j), ":", tag, f"(depth {depth[j]})" if val[j] else "")
json.dump({'states':[[list(s[0]),list(s[1]),s[2],s[3]] for s in states],
           'val':val, 'depth':depth,
           'succ':[list(x) for x in succ],
           'winmove':winmove, 'start':start}, open('chop_data.json','w'))
print("dumped")
