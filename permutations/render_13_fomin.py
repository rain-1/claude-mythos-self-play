import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from fomin import growth, rsk_shape
from figkit import annotate
import time

def render(perm=(3,7,1,5,2,6,4), S=1600):
    t0=time.time(); n=len(perm)
    C=growth(list(perm)); assert C[n][n]==rsk_shape(list(perm))
    SS=2; W=S*SS
    img=Image.new("RGB",(W,W),(8,8,13)); dr=ImageDraw.Draw(img)
    margin=int(W*0.075); cw=(W-2*margin)/n
    def corner_xy(i,j): return (margin+i*cw, W-margin-j*cw)   # j up
    # grid
    for i in range(n+1):
        dr.line([corner_xy(i,0),corner_xy(i,n)],fill=(34,36,48),width=SS)
        dr.line([corner_xy(0,i),corner_xy(n,i)],fill=(34,36,48),width=SS)
    # X markers (the permutation): cell (i,j) center where perm[i-1]==j
    for i in range(1,n+1):
        j=perm[i-1]
        cx=(corner_xy(i-1,j-1)[0]+corner_xy(i,j)[0])/2; cy=(corner_xy(i-1,j-1)[1]+corner_xy(i,j)[1])/2
        rr=int(cw*0.06); dr.ellipse([cx-rr,cy-rr,cx+rr,cy+rr],fill=(250,230,140))
    # young diagrams at corners
    maxsz=sum(C[n][n])
    def col_for(sz):
        t=sz/max(1,maxsz)
        cs=np.array([[0.25,0.30,0.55],[0.20,0.62,0.78],[0.30,0.82,0.55],[1.0,0.78,0.35]]);pos=np.array([0,0.4,0.7,1.0])
        return tuple(int(255*np.interp(t,pos,cs[:,k])) for k in range(3))
    for i in range(n+1):
        for j in range(n+1):
            lam=C[i][j]; cx,cy=corner_xy(i,j)
            if not lam:
                dr.ellipse([cx-3*SS,cy-3*SS,cx+3*SS,cy+3*SS],outline=(90,90,110),width=SS); continue
            b=cw*0.40/max(max(lam),len(lam),1)            # box size to fit
            col=col_for(sum(lam))
            totw=lam[0]*b; toth=len(lam)*b
            ox=cx-totw/2; oy=cy-toth/2
            for r,part in enumerate(lam):
                for cidx in range(part):
                    X=ox+cidx*b; Y=oy+r*b
                    dr.rectangle([X,Y,X+b-SS,Y+b-SS],fill=col)
    arr=np.asarray(img).astype(np.float32)/255
    g=arr.copy()
    for k in range(3): g[...,k]+=0.28*gaussian_filter(arr[...,k],SS*1.3)
    out=Image.fromarray((np.clip(g,0,1)*255).astype(np.uint8)).resize((S,S),Image.LANCZOS)
    dr2=ImageDraw.Draw(out)
    try: fnt=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(S*0.016))
    except: fnt=ImageFont.load_default()
    dr2.text((int(S*0.04),int(S*0.025)),f"sigma = {''.join(map(str,perm))}   ->   RSK shape {C[n][n]}",font=fnt,fill=(245,230,150))
    body=("A third face of RSK (after row-insertion in Fig 3 and shadow lines in Fig 9): Fomin's GROWTH DIAGRAM. Mark "
          "the permutation as crosses in an n*n grid; label every lattice corner with a Young diagram, starting empty at "
          "the lower-left. Four purely LOCAL rules - depending only on the three corners to the south-west and whether a "
          "cross sits in the square - grow each diagram from its neighbours by at most one box. The shapes swell from the "
          "empty corner to the full RSK shape at the top-right (verified == RSK on all of S1..S7); the diagrams along the "
          "top edge spell the recording tableau, those down the right edge the insertion tableau. RSK, rebuilt with no "
          "insertion and no bumping - just light touches between neighbours.")
    fig=annotate(out,"FIGURE 13 - FOMIN GROWTH DIAGRAMS","RSK as a Lattice of Shapes",body,accent=(120,205,150))
    fig.save("13_fomin.png"); print("saved",fig.size,"shape",C[n][n],"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
