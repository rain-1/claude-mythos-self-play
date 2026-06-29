import numpy as np
from PIL import Image

S3=np.sqrt(3)
# triangular lattice basis (nearest-center spacing = s)
def basis(s): return np.array([[s,0],[s/2, s*S3/2]])
Minv_cache={}
def axial_round(qf,rf):
    # cube rounding
    xf=qf; zf=rf; yf=-xf-zf
    rx=np.round(xf); ry=np.round(yf); rz=np.round(zf)
    dx=np.abs(rx-xf); dy=np.abs(ry-yf); dz=np.abs(rz-zf)
    # fix the largest
    cond1=(dx>dy)&(dx>dz)
    cond2=(dy>dz)&~cond1
    rx=np.where(cond1, -ry-rz, rx)
    ry=np.where(cond2, -rx-rz, ry)
    rz=np.where(~cond1&~cond2, -rx-ry, rz)
    return rx.astype(np.int64), rz.astype(np.int64)
def hexcolor_of_points(P, s):
    B=basis(s); Minv=np.linalg.inv(B.T)  # P = [q r] @ B  => [q r] = P @ Minv? careful
    # p = q*a1 + r*a2 = [q,r] @ B  (B rows are a1,a2). So [q,r] = p @ inv(B). B is 2x2 rows a1,a2.
    QR = P @ np.linalg.inv(B)
    q,r=axial_round(QR[...,0],QR[...,1])
    return (q-2*r)%7, q, r

def verify(s, ntrials=200000, seed=1):
    rng=np.random.default_rng(seed)
    P=rng.uniform(-20,20,size=(ntrials,2))
    ang=rng.uniform(0,2*np.pi,size=ntrials)
    Q=P+np.stack([np.cos(ang),np.sin(ang)],1)  # unit distance
    cP,_,_=hexcolor_of_points(P,s); cQ,_,_=hexcolor_of_points(Q,s)
    viol=np.sum(cP==cQ)
    return viol


if __name__=="__main__":
    for s in [0.70,0.72,0.75,0.78,0.80,0.82]:
        v=verify(s)
        print(f"s={s}  unit-dist same-color violations: {v}")
