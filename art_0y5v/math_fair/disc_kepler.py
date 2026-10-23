# Disc reduction: junction p=(r,0); area condition <=> mean anomalies M_i=t_i - r sin t_i equally spaced
import numpy as np, mpmath as mp
def E(M,r,n=60):
    t=M+0*r
    for _ in range(n): t=t-(t-r*np.sin(t)-M)/(1-r*np.cos(t))
    return t
def Q(r,c):
    t=[E(c+2*np.pi*i/3,r) for i in range(3)]
    d=[np.sqrt(1+r*r-2*r*np.cos(x)) for x in t]
    u=[d[i]+r*np.sin(t[i]) for i in range(3)]; v=[d[i]-r*np.sin(t[i]) for i in range(3)]
    return [u[(i+1)%3]+v[i] for i in range(3)]
def G(r,c):
    q=Q(r,c); return np.array([q[0]-q[1],q[1]-q[2]])
if __name__=="__main__":
    for c in [0,np.pi/3]:
        rs=np.linspace(-0.999,0.999,2001); vals=np.array([G(r,c)[0] for r in rs])
        idx=np.where(np.sign(vals[:-1])!=np.sign(vals[1:]))[0]
        print('c',c,'sign changes at r~',rs[idx], 'G2 there', [G(rs[i],c)[1] for i in idx])
