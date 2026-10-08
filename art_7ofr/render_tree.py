# The finite tree of chains a_{n+1} = a_n * s(a_{n+1}) from 1 (MO 515823) as a radial firework:
# radius = number of digits of a, angle = leaf order (each subtree gets a wedge ~ its leaf count),
# hue = angle on the sorbet wheel, every chain ends in a blossom; the longest chain in coral.
import numpy as np, json, sys, math
from PIL import Image, ImageDraw, ImageFilter
WHEEL=np.array([[0.98,0.60,0.66],[1.0,0.74,0.58],[1.0,0.88,0.55],[0.78,0.92,0.58],[0.58,0.90,0.78],[0.58,0.80,0.97],[0.68,0.70,0.98],[0.84,0.66,0.96],[0.98,0.64,0.86],[0.98,0.60,0.66]])
def wheel(u):
    u=(u%1.0)*(len(WHEEL)-1); i=int(min(u,len(WHEEL)-2)); fr=u-i
    return WHEEL[i]**(1-fr)*WHEEL[i+1]**fr
CORAL=np.array([0.95,0.40,0.38])

def load(b):
    T=json.load(open(f'tree{b}.json'))
    import gmpy2
    val=[gmpy2.mpz(v) for v,_,_,_ in T]; par=[p for _,p,_,_ in T]; dep=[d for _,_,d,_ in T]
    nd=[len(gmpy2.digits(v,b)) + float(gmpy2.log(v/ (gmpy2.mpz(b)**(len(gmpy2.digits(v,b))-1)) ) )/math.log(b) if v>0 else 0 for v in val]
    lg=[float(gmpy2.log(v))/math.log(b) if v>1 else 0.0 for v in val]
    return val,par,dep,lg

def layout(par,lg):
    n=len(par); ch=[[] for _ in range(n)]
    for i,p in enumerate(par):
        if p>=0: ch[p].append(i)
    # leaf counts weighted toward long chains so deep tendrils get room
    w=[0.0]*n
    for i in range(n-1,-1,-1):
        w[i]=1.0 if not ch[i] else sum(w[c] for c in ch[i])
    ang=[0.0]*n; lo=[0.0]*n; hi=[0.0]*n
    lo[0],hi[0]=0.0,1.0
    order=[0]
    while order:
        i=order.pop()
        a=lo[i]; tot=w[i]
        # children sorted by subtree weight, heavy in the middle
        cs=sorted(ch[i],key=lambda c:w[c])
        cs=cs[0::2]+cs[1::2][::-1]
        for c in cs:
            lo[c]=a; hi[c]=a+(hi[i]-lo[i])*w[c]/tot; a=hi[c]; order.append(c)
        ang[i]=(lo[i]+hi[i])/2
    return ch,w,ang

def render(b=3,W=2048,out='_tree.png',ss=3,rmax=None,gamma=0.75,ang0=0.0,title=None):
    val,par,dep,lg=load(b)
    ch,w,ang=layout(par,lg)
    n=len(par); Lmax=max(lg) if rmax is None else rmax
    S=W*ss; cx=cy=S/2; R=0.44*S
    def pos(i,a=None):
        r=R*(lg[i]/Lmax)**gamma if lg[i]>0 else 0
        t=2*math.pi*((ang[i] if a is None else a)+ang0)
        return cx+r*math.sin(t), cy-r*math.cos(t)
    img=Image.new('RGB',(S,S),(253,251,249))
    lay=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(lay)
    # longest chain
    deepest=max(range(n),key=lambda i:lg[i]); chain=set(); j=deepest
    while j>=0: chain.add(j); j=par[j]
    sub=[0]*n
    for i in range(n-1,0,-1): sub[i]+=1; sub[par[i]]+=sub[i]
    def col(i,k=1.0,a=255):
        c=CORAL if i in chain else wheel(ang[i]+ang0)
        c=c**k
        return tuple(int(255*v) for v in c)+(a,)
    # edges: polar curve from parent radius/angle to child radius/angle (angle eases in first)
    for i in range(1,n):
        p=par[i]
        wd=max(1.2*ss,ss*(1.0+1.35*math.log1p(sub[i])))*W/2048
        pts=[]
        for s in np.linspace(0,1,24):
            a=ang[p]+(ang[i]-ang[p])*min(1,s*2.2)**0.8
            r=lg[p]+(lg[i]-lg[p])*s
            rr=R*(r/Lmax)**gamma if r>0 else 0
            t=2*math.pi*(a+ang0); pts.append((cx+rr*math.sin(t),cy-rr*math.cos(t)))
        d.line(pts,fill=col(i,1.35,235),width=int(wd)+2*ss,joint='curve')
        d.line(pts,fill=col(i,0.75,255),width=max(1,int(wd*0.55)),joint='curve')
    img.paste(lay,(0,0),lay)
    lay=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(lay)
    # blossoms at chain ends
    for i in range(n):
        if ch[i]: continue
        x,y=pos(i); r0=(5.5 if i!=deepest else 14)*ss*W/2048
        c=col(i,1.0,255); cd=col(i,1.6,255)
        t0=2*math.pi*(ang[i]+ang0)
        for k in range(5):
            t=t0+2*math.pi*k/5
            px,py=x+0.62*r0*math.sin(t),y-0.62*r0*math.cos(t)
            d.ellipse([px-0.55*r0,py-0.55*r0,px+0.55*r0,py+0.55*r0],fill=c,outline=cd,width=max(1,ss//2))
        d.ellipse([x-0.32*r0,y-0.32*r0,x+0.32*r0,y+0.32*r0],fill=(255,236,170,255))
    # root
    r0=10*ss*W/2048; d.ellipse([cx-r0,cy-r0,cx+r0,cy+r0],fill=(255,244,214,255),outline=(240,120,110,255),width=2*ss)
    img.paste(lay,(0,0),lay)
    img=img.resize((W,W),Image.LANCZOS)
    img.save(out); print(out,n,'nodes','leaves',sum(1 for i in range(n) if not ch[i]),'max digits',Lmax)

if __name__=="__main__":
    render(int(sys.argv[1]),W=int(sys.argv[2]),out=sys.argv[3])
