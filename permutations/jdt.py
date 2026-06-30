from bisect import bisect_right
import random

def rsk_P(word):
    P=[]
    for x in word:
        r=0; v=x
        while True:
            if r==len(P): P.append([v]); break
            row=P[r]; j=bisect_right(row,v)
            if j==len(row): row.append(v); break
            row[j],v=v,row[j]; r+=1
    return [tuple(r) for r in P]

def reading_word(cells):
    # cells: dict (r,c)->val ; reading word = bottom rows to top, left to right
    rows=sorted(set(r for r,c in cells))
    word=[]
    for r in reversed(rows):
        for c in sorted(c for (rr,c) in cells if rr==r): word.append(cells[(r,c)])
    return word

def inner_corners(filled, mu_cells):
    # an inner corner of mu = hole cell with no hole directly below or to the right? 
    # standard: pick an inner corner = a cell of mu that is a corner (no mu cell below or right)
    res=[]
    for (r,c) in mu_cells:
        if (r+1,c) not in mu_cells and (r,c+1) not in mu_cells: res.append((r,c))
    return res

def slide_once(filled, mu_cells, corner):
    # forward jdt slide starting at hole 'corner'
    mu=set(mu_cells); r,c=corner; mu.discard((r,c))
    while True:
        right=filled.get((r,c+1)); down=filled.get((r+1,c))
        if right is None and down is None: break
        if down is None or (right is not None and right<down):
            filled[(r,c)]=right; del filled[(r,c+1)]; c=c+1
        else:
            filled[(r,c)]=down; del filled[(r+1,c)]; r=r+1
    return filled, mu

def rectify(filled, mu_cells, record=False):
    filled=dict(filled); mu=set(mu_cells); steps=[]
    while mu:
        cor=inner_corners(filled,mu)[0]
        if record: steps.append((dict(filled),set(mu),cor))
        filled,mu=slide_once(filled,mu,cor)
    if record: steps.append((dict(filled),set(),None))
    return filled, steps

if __name__=="__main__":
    # build a random skew SYT, verify rectification == RSK of reading word, and slide-order independence
    rng=random.Random(1); bad=0; conf=0
    for trial in range(400):
        # random skew shape: outer lam, inner mu
        # pick small: outer rows
        lam=[5,4,2,1]; mu=[2,1,0,0]
        cells=[(r,c) for r in range(len(lam)) for c in range(lam[r])]
        muc=set((r,c) for r in range(len(mu)) for c in range(mu[r]))
        skew=[x for x in cells if x not in muc]
        vals=list(range(1,len(skew)+1)); 
        # random standard filling of skew (increasing along rows and cols)
        # generate by random linear extension
        import itertools
        order=[]; remaining=set(skew); 
        while remaining:
            mins=[x for x in remaining if (x[0],x[1]-1) not in remaining and (x[0]-1,x[1]) not in remaining]
            ch=rng.choice(mins); order.append(ch); remaining.discard(ch)
        fill={cell:i+1 for i,cell in enumerate(order)}
        rect,_=rectify(fill,muc)
        # RSK of reading word
        rw=reading_word(fill); P=rsk_P(rw)
        rectrows=[tuple(rect[(r,c)] for c in sorted(cc for (rr,cc) in rect if rr==r)) for r in sorted(set(r for r,c in rect))]
        if rectrows!=P: bad+=1
    print(f"jeu de taquin: rectification==RSK(reading word) mismatches {bad}/400")
