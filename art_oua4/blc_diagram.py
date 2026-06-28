"""Tromp lambda diagrams: abstraction = horizontal bar, variable = vertical line up to its
binding bar, application = horizontal link joining the two function/argument spines.
Returns line segments in integer grid units (y grows DOWN)."""
import numpy as np

class Vert:
    __slots__=('x','ytop','ybot','rem')
    def __init__(s,x,ytop,ybot,rem): s.x,s.ytop,s.ybot,s.rem=x,ytop,ybot,rem

def _shiftright(D,dx):
    for v in D['verts']: v.x+=dx
    D['hbars']=[(y,x0+dx,x1+dx) for y,x0,x1 in D['hbars']]
    D['links']=[(y,x0+dx,x1+dx) for y,x0,x1 in D['links']]
def _shiftdown(D,dy):
    for v in D['verts']: v.ytop+=dy; v.ybot+=dy
    D['hbars']=[(y+dy,x0,x1) for y,x0,x1 in D['hbars']]
    D['links']=[(y+dy,x0,x1) for y,x0,x1 in D['links']]
def _height(D):
    h=0
    for y,_,_ in D['hbars']: h=max(h,y+1)
    for v in D['verts']: h=max(h,v.ybot)
    for y,_,_ in D['links']: h=max(h,y+1)
    return h

def lay(t):
    if t[0]=='V':
        v=Vert(0,0,1,t[1])
        return dict(w=1,hbars=[],links=[],verts=[v],spine=v)
    if t[0]=='L':
        D=lay(t[1]); _shiftdown(D,2)
        D['hbars'].append((0,0,max(0,D['w']-1)))
        for v in D['verts']:
            if v.rem is not None:
                if v.rem==0: v.ytop=0; v.rem=None
                else: v.ytop=0; v.rem-=1
        return D
    # App
    Df=lay(t[1]); Da=lay(t[2]); GAP=2
    _shiftright(Da,Df['w']+GAP)
    H=max(_height(Df),_height(Da))
    Df['spine'].ybot=max(Df['spine'].ybot,H+1)
    Da['spine'].ybot=max(Da['spine'].ybot,H+1)
    link=(H,Df['spine'].x,Da['spine'].x)
    return dict(w=Df['w']+GAP+Da['w'],
                hbars=Df['hbars']+Da['hbars'],
                links=Df['links']+Da['links']+[link],
                verts=Df['verts']+Da['verts'],
                spine=Df['spine'])

def segments(t):
    """Return (W,H, hsegs, vsegs) in grid units. hsegs/vsegs lists of (a,b,c):
       hseg=(y,x0,x1) ; vseg=(x,y0,y1).  Combines lambda bars + application links as h."""
    D=lay(t)
    H=_height(D); Wd=D['w']
    hsegs=[(y,x0,x1) for (y,x0,x1) in D['hbars']] + [(y,x0,x1) for (y,x0,x1) in D['links']]
    vsegs=[(v.x,v.ytop,v.ybot) for v in D['verts']]
    return Wd,H,hsegs,vsegs

# bar kinds for colouring: lambda bars vs application links
def segments_typed(t):
    D=lay(t); H=_height(D); Wd=D['w']
    lam=[(y,x0,x1) for (y,x0,x1) in D['hbars']]
    app=[(y,x0,x1) for (y,x0,x1) in D['links']]
    vsegs=[(v.x,v.ytop,v.ybot) for v in D['verts']]
    return Wd,H,lam,app,vsegs

if __name__=="__main__":
    import blc
    for name,t in [("I",blc.I),("K",blc.K),("S",blc.S),("c2",blc.church(2)),("c3",blc.church(3))]:
        Wd,H,lam,app,v=segments_typed(t)
        print(f"{name:3} grid {Wd}x{H}  lam-bars={len(lam)} app-links={len(app)} verts={len(v)}")
