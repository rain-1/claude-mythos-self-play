"""Aerial storybook park of a pseudoline arrangement: height field + colour field, sun shadows (numba)."""
import numpy as np, sys, json, time
from scipy import ndimage as ndi
from PIL import Image, ImageDraw
import numba as nb
import arrangement as AR

def hexrgb(h): h=h.lstrip('#'); return np.array([int(h[i:i+2],16)/255 for i in (0,2,4)],np.float32)
PAPER=np.array([0.992,0.985,0.975],np.float32)
LAWN=hexrgb('d8eecb'); LAWN2=hexrgb('cbe8c0'); HEDGE=hexrgb('b3e2bb'); HEDGE2=hexrgb('a6dcb2')
GRAVEL=hexrgb('f6ece0'); STONE=hexrgb('efe6f0'); WATER=hexrgb('a9dcf2')
# path hues (sorbet wheel), 9 paths
PATHHUES=[hexrgb(h) for h in ['f59fb3','f8b48f','f6d77e','c8e38b','8fdcc2','92cdee','a7b4f2','c9a8ef','f3a6d9']]
TULIPSETS=[[hexrgb(h) for h in hs] for hs in (['f59cc0','fbc0d8','f7b0cf'],['fbe08a','fdeaa8','fff3c4'],['c3ecd9','ffffff','a8e2c8'],
  ['c9a8ef','dcc6f7','b9a6ee'],['fbb0c8','ffffff','fdd1dc'],['9fd3f2','c3e4f7','ffffff'])]
CORAL=[hexrgb(h) for h in ['ff7f68','ff9a80','ff8c70','ffb09a']]
LAV=[hexrgb(h) for h in ['b9a6ee','cbb8f4','a99be6']]
BUTTER=[hexrgb(h) for h in ['fbe08a','fdeaa8','f8d46e']]
MEADOW=[hexrgb(h) for h in ['fbe08a','f7a8c0','ffffff','b9a6ee','9fd3f2']]
TREE=[hexrgb(h) for h in ['a8dca0','b6e3a2','9dd6b0','c3e6a0']]
BLOSSOM=[hexrgb(h) for h in ['f9c6d6','fbd3e0','f6b8cc']]

@nb.njit(parallel=True,fastmath=True)
def shadow(H,lx,ly,lz,step,maxd):
    HMAX=H.max(); h,w=H.shape; S=np.ones((h,w),np.float32)
    for y in nb.prange(h):
        for x in range(w):
            h0=H[y,x]; t=step; occ=0.0
            while t<maxd and h0+lz*t<HMAX:
                px=x+lx*t; py=y+ly*t
                if px<0 or py<0 or px>=w-1 or py>=h-1: break
                ix=int(px); iy=int(py); fx=px-ix; fy=py-iy
                hh=(H[iy,ix]*(1-fx)*(1-fy)+H[iy,ix+1]*fx*(1-fy)+H[iy+1,ix]*(1-fx)*fy+H[iy+1,ix+1]*fx*fy)
                d=hh-(h0+lz*t)
                if d>0:
                    o=min(1.0,d/(0.6+0.02*t))   # soft penumbra
                    if o>occ: occ=o
                    if occ>=1: break
                t+=step*(1+t*0.004)
            S[y,x]=1-occ
    return S

def polyline_mask(shape,pts,width=1):
    im=Image.new('L',(shape[1],shape[0]),0); d=ImageDraw.Draw(im)
    d.line([tuple(p) for p in pts],fill=255,width=width); return np.array(im)>0

from PIL import ImageFont, ImageFilter
FS='/usr/share/fonts/truetype/freefont/'
INK=(92,77,102)
def add_caption(im,S,cx,cy,R):
    im=im.convert('RGBA'); d=ImageDraw.Draw(im)
    f1=ImageFont.truetype(FS+'FreeSerifBold.ttf',int(S*0.024))
    f2=ImageFont.truetype(FS+'FreeSerifItalic.ttf',int(S*0.0135))
    f3=ImageFont.truetype(FS+'FreeSerif.ttf',int(S*0.0118))
    y=int(S*0.885)
    def ctext(t,f,y,fill):
        w=d.textlength(t,font=f); d.text(((S-w)/2,y),t,font=f,fill=fill)
    ctext('Eight Fountains, and a Path No Ruler Could Draw',f1,y,INK)
    ctext('Nine garden paths in the projective plane: every two cross exactly once, and leaving by any gate brings you back in through the opposite one.',f2,y+int(S*0.036),INK)
    ctext('Fountains mark the eight triple crossings of a Pappus configuration. Straight paths through all eight would be forced, by Pappus’ theorem, through a ninth;',f3,y+int(S*0.060),(120,104,128))
    ctext('the coral-edged path swerves instead, and the coral bed is the triangle it leaves behind. Tulips grow in triangles, lavender in pentagons, lawn in the rest.',f3,y+int(S*0.078),(120,104,128))
    # little park sign on the apron, lower left
    a=np.deg2rad(222); sx=cx+R*1.085*np.cos(a); sy=cy-R*1.085*np.sin(a)
    sw,sh_=S*0.10,S*0.034
    sign=Image.new('RGBA',im.size,(0,0,0,0)); sd=ImageDraw.Draw(sign)
    sd.rounded_rectangle([sx-sw/2+S*0.004,sy-sh_/2+S*0.006,sx+sw/2+S*0.004,sy+sh_/2+S*0.006],radius=S*0.006,fill=(120,110,170,70))
    sign=sign.filter(ImageFilter.GaussianBlur(S*0.003)); im=Image.alpha_composite(im,sign); d=ImageDraw.Draw(im)
    d.rounded_rectangle([sx-sw/2,sy-sh_/2,sx+sw/2,sy+sh_/2],radius=S*0.006,fill=(255,247,236),outline=(246,170,150),width=max(1,int(S*0.0012)))
    fs=ImageFont.truetype(FS+'FreeSerifItalic.ttf',int(S*0.0088))
    for k,t in enumerate(('There are no rules','in this park.')):
        w=d.textlength(t,font=fs); d.text((sx-w/2,sy-sh_*0.36+k*S*0.0105),t,font=fs,fill=INK)
    return im.convert('RGB')
def render(S=1024,ss=2,out='park.png',bend=0.075,seed=7,caption=True):
    t0=time.time(); rng=np.random.default_rng(seed)
    W=H_=int(S*ss); Rp=0.385*W; cx=0.5*W; cy=0.445*H_
    paths,lines,C,cmid,order=AR.build(bend=bend)
    V=AR.vertices(paths)
    to_px=lambda P: np.stack([cx+Rp*P[:,0], cy-Rp*P[:,1]],1)
    pw=0.0145*Rp      # path half width
    yy,xx=np.mgrid[0:H_,0:W].astype(np.float32)
    rr=np.hypot(xx-cx,yy-cy)/Rp
    inside=rr<1.0
    # ---- path distance fields
    dmin=np.full((H_,W),1e9,np.float32); pid=np.zeros((H_,W),np.int8)
    for i,k in enumerate(order):
        P=to_px(paths[k]); m=~polyline_mask((H_,W),P,1)
        d=ndi.distance_transform_edt(m).astype(np.float32)
        sel=d<dmin; dmin[sel]=d[sel]; pid[sel]=i
    # plazas
    plaza=np.full((H_,W),1e9,np.float32); pmult=np.zeros((H_,W),np.int8)
    cmp_=AR.stereo(C[cmid][None])[0]
    tri=sorted([p for p,mlt in V if mlt==2],key=lambda p: np.linalg.norm(p-cmp_))[:3]
    VALL=V; V=[(p,mlt) for p,mlt in V if mlt==3]
    for p,mlt in V:
        q=to_px(p[None])[0]; r=(0.052 if mlt==3 else 0.026)*Rp
        d=np.hypot(xx-q[0],yy-q[1])-r
        sel=d<plaza; plaza[sel]=d[sel]; pmult[sel]=mlt
    walk=np.minimum(dmin-pw,plaza)            # <0 on walkable surface
    # ---- faces (beds): complement of walk+verge inside disc, labelled; antipodal merge
    verge=0.012*Rp
    free=(walk>verge)&(rr<1-0.035)
    lab,nl=ndi.label(free)
    # antipodal union via rim samples
    par=list(range(nl+1))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for th in np.linspace(0,2*np.pi,4000,endpoint=False):
        rad=1-0.045
        p1=(int(cy-Rp*rad*np.sin(th)),int(cx+Rp*rad*np.cos(th))); p2=(int(cy+Rp*rad*np.sin(th)),int(cx-Rp*rad*np.cos(th)))
        a,b=lab[p1],lab[p2]
        if a and b: par[f(a)]=f(b)
    root=np.array([f(i) for i in range(nl+1)]); lab=root[lab]
    ids=[i for i in np.unique(lab) if i]
    # degree: distinct paths bordering each face
    near=(walk>verge-3*ss)&(walk<verge+3*ss)
    dil=ndi.grey_dilation(lab,size=(int(7*ss),int(7*ss)))
    info={}
    for i in ids:
        sel=(dil==i)&near&(walk>0)
        ps=set(np.unique(pid[sel]).tolist())
        area=(lab==i).sum()/Rp**2
        info[i]=dict(deg=len(ps),area=area)
    # identify the coral (non-Pappus) triangle: the face nearest the bent C point
    from scipy.spatial import cKDTree
    i_,j_={3:(1,2),2:(1,3),1:(2,3)}[cmid]
    L1,L2=paths[f'A{i_}B{j_}'],paths[f'A{j_}B{i_}']
    def X(a,b):
        d,ix=cKDTree(b).query(a); k=np.argmin(d); return (a[k]+b[ix[k]])/2
    tri=[X(L1,L2),X(paths['p'],L1),X(paths['p'],L2)]
    T=to_px(np.array(tri)); tm=Image.new('L',(W,H_),0); ImageDraw.Draw(tm).polygon([tuple(p) for p in T],fill=1)
    tl=lab[np.array(tm)>0]; tl=tl[tl>0]
    tmask=np.array(tm)>0
    coral_set=set()
    for i in np.unique(tl):
        if (tmask&(lab==i)).sum()>0.6*(lab==i).sum(): coral_set.add(int(i))
    coral_id=-1
    print('tri',T, 'labels',np.unique(tl,return_counts=True))
    print('coral set',coral_set);print('faces',len(ids),'degrees',sorted(v['deg'] for v in info.values()),'coral',coral_id,'%.1fs'%(time.time()-t0),flush=True)

    # ---- height + colour
    Hh=np.zeros((H_,W),np.float32); col=np.zeros((H_,W,3),np.float32); col[:]=PAPER
    # outer surround: soft lawn apron then paper
    apron=(rr>=1.0)&(rr<1.13)
    col[rr<1.13]=LAWN
    # gravel promenade ring outside hedge
    prom=(rr>1.075)&(rr<1.125)
    col[prom]=GRAVEL
    noise=rng.random((H_,W)).astype(np.float32)
    nblur=ndi.gaussian_filter(noise,1.0*ss)
    # lawn everywhere inside with mown stripes (direction per face later)
    col[inside]=LAWN
    # beds
    bedmask=np.zeros((H_,W),bool)
    for i in ids:
        m=lab==i
        if not m.any(): continue
        deg=info[i]['deg']; ys,xs=np.nonzero(m)
        # bed interior = inset by box-hedge border
        dist_in=ndi.distance_transform_edt(m[ys.min()-2:ys.max()+3, xs.min()-2:xs.max()+3]).astype(np.float32)
        sub=(slice(ys.min()-2,ys.max()+3),slice(xs.min()-2,xs.max()+3))
        mm=m[sub]
        th=rng.uniform(0,np.pi)
        X=xx[sub]; Y=yy[sub]
        u=X*np.cos(th)+Y*np.sin(th); v=-X*np.sin(th)+Y*np.cos(th)
        hsub=Hh[sub]; csub=col[sub]
        # box hedge border (low)
        border=mm&(dist_in<2.2*ss*1.6)
        if i in coral_set or deg==3:
            pal=CORAL if i in coral_set else TULIPSETS[i%len(TULIPSETS)]
            sp=0.0135*Rp; rt=0.40*sp
            gu=np.round(u/sp); gv=np.round(v/(sp*0.866))
            uo=u-(gu*sp+ (gv%2)*0.5*sp)  # hex offset
            gu2=np.round((u-(gv%2)*0.5*sp)/sp); uo=u-(gu2*sp+(gv%2)*0.5*sp); vo=v-gv*sp*0.866
            d=np.hypot(uo,vo)/rt
            hk=(gu2*73856093+gv*19349663).astype(np.int64)%997
            cid=(hk%len(pal)).astype(int)
            flower=(d<1)&mm&(dist_in>0.5*sp)
            base=np.where(mm,1,0)
            soil=hexrgb('bfe3b0')
            csub[mm]=soil
            hcap=np.sqrt(np.clip(1-d**2,0,1))*rt*0.9
            pc=np.array(pal)[cid]
            csub[flower]=pc[flower]
            hsub[flower]=np.maximum(hsub[flower],hcap[flower]+0.4*ss)
        elif deg==4 or deg<3:
            stripe=(np.floor(u/(0.03*Rp))%2)==0
            csub[mm&stripe]=LAWN2; csub[mm&~stripe]=LAWN
        elif deg==5:
            sp=0.016*Rp; vv=np.mod(v,sp)-sp/2; uu=np.mod(u,0.6*sp)-0.3*sp
            row=np.abs(vv)<0.36*sp
            soil=hexrgb('e3f1d8'); csub[mm]=soil
            hump=np.sqrt(np.clip(1-(vv/(0.36*sp))**2,0,1))*0.3*sp
            lv=mm&row&(dist_in>0.3*sp)
            gid=(np.floor(v/sp)).astype(np.int64)%3
            csub[lv]=np.array(LAV)[gid[lv]]*(0.92+0.16*nblur[sub][lv,None])
            hsub[lv]=np.maximum(hsub[lv],hump[lv]+0.5*nblur[sub][lv]*ss)
        else:
            # meadow: lawn with scattered tiny flowers
            csub[mm]=hexrgb('d6ecbf')
            fl=mm&(noise[sub]>0.985-0.0*deg)
            k=(noise[sub]*1e4).astype(int)%len(MEADOW)
            csub[fl]=np.array(MEADOW)[k[fl]]
        csub[border]=HEDGE2; hsub[border]=np.maximum(hsub[border],2.2*ss)
        bedmask[sub]|=mm
    # ---- paths: gravel with coloured brick edging
    onpath=(walk<0)&inside
    col[onpath]=GRAVEL*(0.97+0.06*nblur[onpath,None])
    edge=(dmin-pw>-0.30*pw)&(dmin-pw<0)&(plaza>0)&inside
    for i,k in enumerate(order):
        sel=edge&(pid==i); col[sel]=PATHHUES[i] if k!='p' else hexrgb('ff8f78')
    # plazas: paving rings
    for p,mlt in V:
        q=to_px(p[None])[0]; r=(0.052 if mlt==3 else 0.026)*Rp
        d=np.hypot(xx-q[0],yy-q[1])
        ring=(d<r)&((np.floor(d/(0.009*Rp))%2)==0)
        col[ring]=STONE
        rimr=(d<r)&(d>r-0.15*pw); col[rimr]=hexrgb('e4d7ea')
        if mlt==3:
            bas=d<0.6*r; col[bas]=hexrgb('f4f0f8'); Hh[bas]=np.maximum(Hh[bas],1.5*ss)
            wat=d<0.52*r
            ang=np.arctan2(yy-q[1],xx-q[0])
            rip=0.5+0.5*np.cos(d/(0.006*Rp)*2*np.pi)
            col[wat]=WATER[None]*(0.94+0.08*rip[wat,None])
            Hh[wat]=0.6*ss
            jet=d<0.12*r; col[jet]=1.0; Hh[jet]=np.maximum(Hh[jet],(5*ss*np.sqrt(np.clip(1-(d[jet]/(0.12*r))**2,0,1))))
    # ---- hedge ring with gates
    hedge=(rr>1.0)&(rr<1.06)
    gate=np.zeros_like(hedge)
    gates=[]
    for i,k in enumerate(order):
        P=paths[k]
        for e in (P[0],P[-1]):
            q=np.array([cx+Rp*e[0],cy-Rp*e[1]])
            gates.append((q,i))
            gate|=np.hypot(xx-q[0],yy-q[1])<pw*1.25
    hedge&=~gate
    for q,i in gates:
        hedge&=np.hypot(xx-q[0],yy-q[1])>pw*2.8
    lump=ndi.gaussian_filter(rng.random((H_,W)).astype(np.float32),1.3*ss)
    lump=(lump-lump.mean())/lump.std()
    col[hedge]=HEDGE*(0.93+0.07*lump[hedge,None])
    hh=0.05*Rp*(1-((rr-1.03)/0.03)**4)
    Hh[hedge]=np.maximum(Hh[hedge],hh[hedge]+0.0015*Rp*lump[hedge])
    # gate paths continue through to promenade
    gp=gate&(rr>=0.99)&(rr<1.10); col[gp]=GRAVEL
    for q,i in gates:
        g2=(np.hypot(xx-q[0],yy-q[1])<pw*2.8)&(rr>=0.985)&(rr<1.075)&~gate
        col[g2]=hexrgb('e9f3df')
    # gate posts with banners (path hue) on both sides
    for q,i in gates:
        ang=np.arctan2(q[1]-cy,q[0]-cx); tdir=np.array([-np.sin(ang),np.cos(ang)])
        for s in (-1,1):
            pq=q+tdir*s*pw*1.75
            rpst=pw*0.85
            d=np.hypot(xx-pq[0],yy-pq[1]); post=d<rpst
            pc_=PATHHUES[i] if order[i]!='p' else hexrgb('ff8f78')
            col[post]=pc_[None]*(0.9+0.1*(d[post]<0.55*rpst))[:,None]; Hh[post]=np.maximum(Hh[post],0.03*Rp*np.sqrt(np.clip(1-(d[post]/rpst)**2,0,1))+0.07*Rp)
    # ---- pond in the largest non-coral face
    big=max((i for i in ids if i not in coral_set),key=lambda i: info[i]['area'])
    m=lab==big; din=ndi.distance_transform_edt(m)
    yv,xv=np.unravel_index(np.argmax(din),din.shape); rp_=0.62*din[yv,xv]
    ang=np.arctan2(yy-yv,xx-xv); dpd=np.hypot(xx-xv,yy-yv)/(rp_*(1+0.10*np.cos(2*ang+0.7)+0.05*np.cos(3*ang+2)))
    pond=dpd<1; bank=(dpd<1.12)&~pond
    col[bank]=hexrgb('f3ead9'); 
    wv=np.clip(1-dpd,0,1)
    wvp=wv[pond][:,None]; col[pond]=np.array([0.80,0.92,0.98],np.float32)*(1-wvp)+np.array([0.62,0.84,0.96],np.float32)*wvp
    Hh[pond]=-0.004*Rp
    # lily pads
    for _ in range(26):
        a=rng.uniform(0,2*np.pi); rr_=rng.uniform(0.15,0.85)*rp_; px_,py_=xv+rr_*np.cos(a),yv+rr_*np.sin(a); r_=rng.uniform(0.04,0.08)*rp_
        d=np.hypot(xx-px_,yy-py_); nt=np.abs(((np.arctan2(yy-py_,xx-px_)-a+np.pi)%(2*np.pi))-np.pi)<0.35
        lp=(d<r_)&~nt&pond; col[lp]=hexrgb('b9e3a8'); Hh[lp]=0.002*Rp
        if rng.random()<0.45:
            fl=d<0.35*r_; col[fl&pond]=[hexrgb('fbc4d4'),hexrgb('ffffff'),hexrgb('fbe08a')][rng.integers(3)]; Hh[fl&pond]=0.006*Rp
    lab[pond|bank]=0
    # ---- flower border just inside the hedge
    brd=(rr>0.955)&(rr<0.99)&(walk>0.5*pw)
    th_=np.arctan2(yy-cy,xx-cx); cell=np.floor(th_*Rp/(0.009*Rp)).astype(np.int64)
    rad_=(rr-0.9725)*Rp/(0.0085*Rp)
    dd=np.hypot(((th_*Rp/(0.009*Rp))%1)-0.5,rad_*0.5)
    fb=brd&(dd<0.42)
    BORDER=[hexrgb(h) for h in ['f7a8c0','fbe08a','c9b3f2','ffffff','9fd3f2','fbc4a0']]
    col[brd]=hexrgb('c3e6b2'); 
    col[fb]=np.array(BORDER)[cell[fb]%len(BORDER)]; Hh[fb]=np.maximum(Hh[fb],0.008*Rp*np.sqrt(np.clip(1-(dd[fb]/0.42)**2,0,1)))
    # ---- trees in big lawn/meadow faces + scattered along rim inside
    trees=[]
    for i in ids:
        deg=info[i]['deg']
        if deg>=4 and i not in coral_set:
            m=lab==i; din=ndi.distance_transform_edt(m)
            cand=np.argwhere(din>0.05*Rp)
            if len(cand)==0: continue
            ntree=int(np.clip(info[i]['area']*45,1,11))
            pick=[]
            for _ in range(200):
                yv,xv=cand[rng.integers(len(cand))]
                rt_=rng.uniform(0.026,0.05)*Rp
                if din[yv,xv]<rt_+0.012*Rp: continue
                if all(np.hypot(yv-a,xv-b)>r1+rt_+0.006*Rp for a,b,r1 in pick):
                    pick.append((yv,xv,rt_))
                if len(pick)>=ntree: break
            trees+=pick
    for (yv,xv,rt_) in trees:
        y0,y1=int(max(0,yv-rt_-2)),int(min(H_,yv+rt_+3)); x0,x1=int(max(0,xv-rt_-2)),int(min(W,xv+rt_+3))
        Y=yy[y0:y1,x0:x1]-yv; X=xx[y0:y1,x0:x1]-xv
        tc=TREE[rng.integers(len(TREE))] if rng.random()>0.3 else BLOSSOM[rng.integers(len(BLOSSOM))]
        hc=np.zeros_like(X)
        nb_=7; subs=[(0,0,0.62)]+[(0.40*np.cos(a),0.40*np.sin(a),0.50) for a in rng.uniform(0,2*np.pi,1)+np.arange(nb_-1)*2*np.pi/(nb_-1)]
        for (ox,oy,sr) in subs:
            d=np.hypot(X-ox*rt_,Y-oy*rt_)/(sr*rt_)
            hc=np.maximum(hc,(sr*rt_)*np.sqrt(np.clip(1-d**2,0,1))+ (0.55*rt_ if True else 0)*(d<1))
        tex=lump[y0:y1,x0:x1]
        m=hc>0
        hcap=hc+0.004*Rp*tex+0.02*Rp
        sel=m&(hcap>Hh[y0:y1,x0:x1])
        col[y0:y1,x0:x1][sel]=tc*(0.96+0.04*tex[sel,None])
        Hh[y0:y1,x0:x1][sel]=hcap[sel]
    print('trees',len(trees),'%.1fs'%(time.time()-t0),flush=True)
    # ---- lighting
    sun=np.array([-0.62,-0.50,0.60]); sun/=np.linalg.norm(sun)     # from upper-left (screen x right, y down)
    Hs=ndi.gaussian_filter(Hh,0.7*ss)
    gy,gx=np.gradient(Hs)
    nrm=np.stack([-gx,-gy,np.ones_like(gx)],-1); nrm/=np.linalg.norm(nrm,axis=-1,keepdims=True)
    lam=np.clip(nrm@np.array([sun[0],sun[1],sun[2]]),0,1)/sun[2]
    lz=sun[2]/np.hypot(sun[0],sun[1])
    sh=shadow(Hs,-sun[0]/np.hypot(sun[0],sun[1])*-1,-sun[1]/np.hypot(sun[0],sun[1])*-1,lz,0.7*ss,0.25*Rp)
    sh=ndi.gaussian_filter(sh,0.8*ss)
    ao=np.clip(1-0.45*(ndi.gaussian_filter(Hs,6*ss)-Hs)/(0.03*Rp),0.78,1)
    light=0.64+0.36*sh*np.clip(lam,0,1.25)
    shadowtint=np.array([0.80,0.82,1.0],np.float32)   # periwinkle shade
    L=light[...,None]*np.ones(3,np.float32)
    L=L*(1-(1-light[...,None])*0.9*(1-shadowtint))+(1-light[...,None])*0.12*shadowtint            # cool fill
    img=col*L*ao[...,None]
    img=np.clip(img*1.03,0,1)
    # vignette edge of park area into paper
    fade=np.clip((rr-1.13)/0.015,0,1)[...,None]
    img=img*(1-fade)+PAPER*fade
    # soft drop shadow of the round park on paper
    im=Image.fromarray((np.clip(img,0,1)**(1/1.0)*255).astype(np.uint8)).resize((S,S),Image.LANCZOS)
    if caption: im=add_caption(im,S,cx/ss,cy/ss,Rp/ss)
    im.save(out); print('saved',out,'%.1fs'%(time.time()-t0))
    json.dump(dict(coral=int(coral_id),faces={int(k):v for k,v in info.items()}),open(out+'.json','w'))
if __name__=='__main__':
    render(S=int(sys.argv[1]),ss=float(sys.argv[2]),out=sys.argv[3],bend=-0.52)
