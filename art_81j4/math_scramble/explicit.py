"""Explicit Z x Z-scrambling: f(x,y) = x + g(y), g a class-wise affine
complete mapping (orthomorphism) of Z with period 5:
   y = 5t + r:  g = 4t (r=0), 4t+2 (r=1), -8t+5 (r=2), 4t+3 (r=3), -8t+1 (r=4)
Then g is a bijection of Z and so is h(y) = y + g(y):
   h = 9t, 9t+3, -3t+7, 9t+6, -3t+5.
Rows:  x -> x + g(k)            bijective (translation)
Cols:  y -> k + g(y)            bijective since g is
Diags: (y+k, y) -> k + h(y)     bijective since h is
"""
A=(4,4,-8,4,-8); B=(0,2,5,3,1)
def g(y):
    t,r=divmod(y,5); return A[r]*t+B[r]
def f(x,y): return x+g(y)
if __name__=='__main__':
    N=200000
    for name,fn in [('g',g),('y+g',lambda y:y+g(y)),('g-y',lambda y:g(y)-y)]:
        vals=[fn(y) for y in range(-N,N)]
        inj=len(set(vals))==len(vals)
        S=set(vals); M=N//3
        cov=all(v in S for v in range(-M,M))
        print(f'{name}: injective on [-{N},{N}): {inj}; covers [-{M},{M}): {cov}')
    # direct 2D check on a window
    R=60
    ok=True
    for k in range(-R,R+1):
        for line in ([f(x,k) for x in range(-3000,3000)],[f(k,y) for y in range(-3000,3000)],[f(y+k,y) for y in range(-3000,3000)]):
            if len(set(line))!=len(line) or not set(range(-500,500))<=set(line): ok=False
    print('2D rows/cols/diags injective & cover [-500,500) for |k|<=60:',ok)
    for y in range(4,-5,-1): print(' '.join(f'{f(x,y):4d}' for x in range(-4,5)))
