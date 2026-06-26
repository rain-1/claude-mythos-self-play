"""Magic Square Fig 3 — the octonionic row as root-system mandalas."""
import numpy as np, sys, math
sys.path.insert(0,'magic_square'); sys.path.insert(0,'octonions')
import roots as RT, figkit
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
import colorsys

def edges_of(R):
    n=len(R); D=np.sqrt(((R[:,None,:]-R[None,:,:])**2).sum(-1))
    md=D[D>1e-6].min()
    E=np.array([(i,j) for i in range(n) for j in range(i+1,n) if abs(D[i,j]-md)<1e-6])
    return E

def panel(P,E,hue0, S=620, ss=2, eb=0.5):
    W=S*ss
    Q=P.copy(); sc=W*0.42/(np.abs(Q).max()+1e-9)
    scr=np.stack([W/2+Q[:,0]*sc, W/2-Q[:,1]*sc],1)
    rad=np.linalg.norm(P,axis=1); rings=np.unique(np.round(rad,3))
    ridx=np.array([int(np.argmin(np.abs(rings-r))) for r in np.round(rad,3)])
    nr=len(rings)
    cols=np.array([colorsys.hsv_to_rgb((hue0+0.30*k/max(1,nr-1))%1,0.55,1.0) for k in range(nr)])
    pcol=cols[ridx]
    img=np.zeros((W,W,3),np.float32)+np.array([0.012,0.013,0.024])
    flat=img.reshape(-1,3)
    if len(E):
        A=scr[E[:,0]]; B=scr[E[:,1]]; ec=0.5*(pcol[E[:,0]]+pcol[E[:,1]])
        K=20; ts=np.linspace(0,1,K)
        XY=A[:,None,:]+(B-A)[:,None,:]*ts[None,:,None]
        EC=np.repeat(ec[:,None,:],K,axis=1).reshape(-1,3)
        Xr=XY[...,0].reshape(-1); Yr=XY[...,1].reshape(-1)
        lw=max(1,int(round(ss*1.2)))
        for ox in range(-lw,lw+1):
            for oy in range(-lw,lw+1):
                wt=math.exp(-(ox*ox+oy*oy)/(2*(lw*0.7)**2))
                X=np.clip((Xr+ox).astype(int),0,W-1); Y=np.clip((Yr+oy).astype(int),0,W-1)
                idx=Y*W+X
                for ch in range(3): np.add.at(flat[:,ch],idx,eb*wt*EC[:,ch])
    img=flat.reshape(W,W,3)
    pr=int(W*0.0075); yy,xx=np.mgrid[-pr:pr+1,-pr:pr+1]; g=np.exp(-(xx**2+yy**2)/(2*(pr*0.5)**2))
    for i in range(len(scr)):
        x,y=int(scr[i,0]),int(scr[i,1])
        if pr<=x<W-pr and pr<=y<W-pr:
            img[y-pr:y+pr+1,x-pr:x+pr+1]+=g[...,None]*pcol[i]*1.3
            img[y-pr:y+pr+1,x-pr:x+pr+1]+=g[...,None]*np.array([1,1,1])*0.5
    tigh=np.stack([gaussian_filter(img[...,c],ss*1.1) for c in range(3)],-1)
    wide=np.stack([gaussian_filter(img[...,c],ss*6.0) for c in range(3)],-1)
    out=1.0-np.exp(-1.25*(img+0.5*tigh+0.28*wide))
    im=Image.fromarray((np.clip(out,0,1)*255).astype('uint8'))
    return im.resize((S,S),Image.LANCZOS)

def render(W=1700):
    systems=[("F₄",48,"52"),("E₆",72,"78"),("E₇",126,"133"),("E₈",240,"248")]
    hues=[0.10,0.33,0.52,0.62]
    pw=380; gap=(W-4*pw)//5
    Hh=pw+260
    img=Image.new("RGB",(W,Hh),(9,10,18)); d=ImageDraw.Draw(img)
    for i,(nm,nroots,dim) in enumerate(systems):
        R,P=RT.system(nm.replace("₄","4").replace("₆","6").replace("₇","7").replace("₈","8"))
        E=edges_of(R)
        pan=panel(P,E,hues[i],S=pw,ss=2,eb=0.5)
        x0=gap+i*(pw+gap); y0=110
        img.paste(pan,(x0,y0))
        fb=figkit.font("DejaVuSans-Bold.ttf",54); fs=figkit.font("DejaVuSans.ttf",30)
        wn=d.textlength(nm,font=fb); d.text((x0+pw/2-wn/2,y0-86),nm,font=fb,fill=(235,240,250))
        info=f"{nroots} roots · dim {dim}"
        wi=d.textlength(info,font=fs); d.text((x0+pw/2-wi/2,y0+pw+16),info,font=fs,fill=(170,180,205))
    return img

if __name__=="__main__":
    viz=render(1700)
    body=("To make the magic square's entries into objects rather than names, here are the four "
          "exceptional Lie algebras of the octonionic row drawn as their ROOT SYSTEMS — the "
          "constellations of vectors that encode each algebra's structure — projected onto their "
          "Coxeter planes. F₄ has 48 roots, E₆ has 72, E₇ has 126, and E₈ has 240, and you can "
          "watch the mandala thicken from one to the next as the algebra grows from dimension 52 to "
          "248. These are the actual geometric skeletons of the groups in the table's bottom row; "
          "the last, E₈, is the largest and most intricate root system that exists. Each is, at "
          "root, a shadow the octonions cast into higher dimensions.")
    fig=figkit.caption(viz,"MAGIC SQUARE · THE OBJECTS","The octonionic row as root-system mandalas",
                       body,accent=(255,180,90),W=1700)
    figkit.save(fig,"magic_square/03_exceptional_roots.png")
    print("done",fig.size)
