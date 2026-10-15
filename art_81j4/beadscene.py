import numpy as np, struct
# sorbet glass absorption (per unit radius) — light tints; complementary of the hue is absorbed
GLASS = {
 'strawberry': (0.10, 0.95, 0.60),
 'butter':     (0.05, 0.18, 0.95),
 'mint':       (0.80, 0.10, 0.45),
 'sky':        (0.85, 0.35, 0.06),
 'lilac':      (0.45, 0.75, 0.08),
 'peach':      (0.05, 0.45, 0.85),
 'coral':      (0.05, 0.75, 0.85),
}
CANDY = {'coral': (0.98, 0.52, 0.45), 'pearl': (0.96, 0.94, 0.95)}
class Scene:
    def __init__(s): s.sph=[]; s.cap=[]
    def bead(s,x,y,r,kind,col,z=None):
        z = r if z is None else z
        if kind=='glass': s.sph.append((x,y,z,r,0,*GLASS[col]))
        else: s.sph.append((x,y,z,r,1,*(CANDY[col] if isinstance(col,str) else col)))
    def thread(s,pts,z,rt,col=(0.93,0.90,0.92),closed=True):
        n=len(pts); m=n if closed else n-1
        for i in range(m):
            a=pts[i]; b=pts[(i+1)%n]
            s.cap.append((a[0],a[1],z,b[0],b[1],z,rt,*col))
    def save(s,fn):
        with open(fn,'wb') as f:
            f.write(struct.pack('ii',len(s.sph),len(s.cap)))
            f.write(np.array(s.sph,dtype=np.float64).tobytes())
            if s.cap: f.write(np.array(s.cap,dtype=np.float64).tobytes())
def ring(S, word, cmap, cx, cy, r, gap=1.06, rot=0.0, kind='glass', spacers=None, thread=True):
    n=len(word); R = n*2*r*gap/(2*np.pi)
    pts=[]
    for i,ch in enumerate(word):
        a = rot + 2*np.pi*i/n
        x,y = cx+R*np.cos(a), cy+R*np.sin(a); pts.append((x,y))
        S.bead(x,y,r,kind,cmap[ch])
    fine=[(cx+R*np.cos(rot+2*np.pi*t/(6*n)), cy+R*np.sin(rot+2*np.pi*t/(6*n))) for t in range(6*n)]
    if thread: S.thread(fine, r, 0.07*r, col=(0.96,0.86,0.93))
    return R
