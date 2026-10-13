def minper(s):
    n=len(s)
    for p in range(1,n+1):
        if n%p==0 and s==s[p:]+s[:p]: return p
def info(N):
    out={}
    for c in sorted(set(N)):
        r=N.replace(c,''); out[c]=(len(r),minper(r))
    return len(N),minper(N),out
EX={2:'AABB',3:'ABCCBBCACBBCCB',4:'ABCDBACDABDCBACDABCDBADC',
5:'EABCDBACDABDCBACDABCDEBADCABCDBACDABDCBACDEABCDBADCABCDBACDABDCEBACDABCDBADCABCDBACDEABDCBACDABCDBADCABCDEBACDABDCBACDABCDBADC'}
if __name__=='__main__':
    for k,N in EX.items(): print(k,info(N), {c:N.count(c) for c in sorted(set(N))})
