"""E8 root system (240 roots) and its Coxeter-plane projection (h=30)."""
import numpy as np, itertools

def roots():
    R=[]
    # type 1: +-e_i +- e_j
    for i in range(8):
        for j in range(i+1,8):
            for si in (1,-1):
                for sj in (1,-1):
                    v=np.zeros(8); v[i]=si; v[j]=sj; R.append(v)
    # type 2: (+-1/2)^8 with even number of minus signs
    for signs in itertools.product((1,-1),repeat=8):
        if signs.count(-1)%2==0:
            R.append(0.5*np.array(signs,float))
    return np.array(R)

def simple_roots():
    e=np.eye(8)
    a=np.zeros((8,8))
    a[0]=0.5*(e[0]+e[7])-0.5*(e[1]+e[2]+e[3]+e[4]+e[5]+e[6])
    a[1]=e[0]+e[1]
    a[2]=e[1]-e[0]
    a[3]=e[2]-e[1]
    a[4]=e[3]-e[2]
    a[5]=e[4]-e[3]
    a[6]=e[5]-e[4]
    a[7]=e[6]-e[5]
    return a

def reflection_matrix(al):
    return np.eye(8)-2*np.outer(al,al)/np.dot(al,al)

def coxeter_element():
    C=np.eye(8)
    for al in simple_roots():
        C=reflection_matrix(al)@C
    return C

def coxeter_plane():
    C=coxeter_element()
    w,v=np.linalg.eig(C)
    target=np.exp(2j*np.pi/30)
    k=int(np.argmin(np.abs(w-target)))
    z=v[:,k]; u=np.real(z); t=np.imag(z)
    u/=np.linalg.norm(u); t=t-np.dot(t,u)*u; t/=np.linalg.norm(t)
    return u,t,C

if __name__=="__main__":
    R=roots(); print("num roots",len(R))
    print("norms all 2:",np.allclose((R*R).sum(1),2))
    u,t,C=coxeter_plane()
    P=np.stack([R@u,R@t],1); rad=np.round(np.linalg.norm(P,axis=1),3)
    import collections
    print("ring radii (count):",dict(collections.Counter(rad.tolist())))
    # Coxeter element order
    M=np.eye(8)
    for n in range(1,40):
        M=C@M
        if np.allclose(M,np.eye(8),atol=1e-9): print("Coxeter order",n); break
