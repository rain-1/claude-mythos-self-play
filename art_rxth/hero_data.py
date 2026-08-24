"""Data prep for THE DYNASTY OF CHAMPIONS hero: champion rivers + ordinary fog."""
import numpy as np, json, math, random

R = [int(l.split()[1]) for l in open('b006877.txt') if l.strip() and not l.startswith('#')]

def path_vals(n):
    p=[n]
    while n!=1:
        n = 3*n+1 if n&1 else n>>1
        p.append(n)
    return p

# champion rivers: (t_remaining, log2 value) per point
paths=[]
for n in R:
    p = path_vals(n)
    d = len(p)-1
    t = np.arange(d, -1, -1, dtype=np.float32)          # steps remaining
    y = np.array([math.log2(v) for v in p], dtype=np.float32)
    paths.append((t, y))

# link types for star classes (share fraction from merges.json)
merges = json.load(open('merges.json'))
share = [1.0]  # R_0 = 1 (trivial); index aligned to champion k
for j1,j2,d1,d2,a,b in merges:
    share.append(1 - j2/d2 if d2>0 else 0.0)
links = json.load(open('links.json'))
ltype = ['root'] + [t for *_, t in links]

np.savez('hero_paths.npz',
         lens=np.array([len(t) for t,_ in paths]),
         t=np.concatenate([t for t,_ in paths]),
         y=np.concatenate([y for _,y in paths]),
         share=np.array(share, dtype=np.float32),
         d=np.array([len(path_vals(n))-1 for n in R], dtype=np.int32),
         logn=np.array([math.log2(n) for n in R], dtype=np.float32))
with open('hero_ltype.json','w') as f: json.dump(ltype, f)
print('champions saved:', len(paths), 'total pts', sum(len(t) for t,_ in paths))

# ordinary fog: log-uniform starts, full trajectories
random.seed(20260824)
FOG = 24000
ft=[]; fy=[]
for i in range(FOG):
    n = random.randint(2, 2**63)
    n = 2 + int(2**(random.uniform(4, 63)))
    p = path_vals(n)
    d = len(p)-1
    ft.append(np.arange(d,-1,-1,dtype=np.float32))
    fy.append(np.array([math.log2(v) for v in p], dtype=np.float32))
np.savez('hero_fog.npz',
         lens=np.array([len(a) for a in ft]),
         t=np.concatenate(ft), y=np.concatenate(fy))
print('fog saved:', FOG, 'pts', sum(len(a) for a in ft))
