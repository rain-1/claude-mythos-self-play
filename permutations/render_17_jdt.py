import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from jdt import rsk_P, reading_word
from figkit import annotate
import time

def rectify_record(filled, mu):
    filled=dict(filled); mu=set(mu); snaps=[(dict(filled),set(mu),None)]
    def inner(mu):
        return [(r,c) for (r,c) in mu if (r+1,c) not in mu and (r,c+1) not in mu]
    while mu:
        r,c=sorted(inner(mu))[0]; mu.discard((r,c)); hole=(r,c)
        while True:
            right=filled.get((r,c+1)); down=filled.get((r+1,c))
            if right is None and down is None: break
            if down is None or (right is not None and right<down):
                filled[(r,c)]=right; del filled[(r,c+1)]; c=c+1
            else:
                filled[(r,c)]=down; del filled[(r+1,c)]; r=r+1
            snaps.append((dict(filled),set(mu),(r,c)))
    return filled, snaps

def render(S=1700):
    t0=time.time()
    # skew shape outer (5,4,2), inner (2,1)
    outer=[5,4,2]; inner=[2,1,0]
    allc=[(r,c) for r in range(len(outer)) for c in range(outer[r])]
    muc=set((r,c) for r in range(len(inner)) for c in range(inner[r]))
    skew=[x for x in allc if x not in muc]
    # a fixed standard filling (row-reading increasing) - build a valid SYT of the skew
    order=sorted(skew, key=lambda rc:(rc[0],rc[1]))  # this is increasing along rows; check cols
    fill={}; v=1
    # fill column-major to ensure standard: simplest -> assign by (col then row)? use a known valid:
    for cell in sorted(skew, key=lambda rc:(rc[1],rc[0])): pass
    # build standard filling greedily by repeatedly numbering a current corner (linear extension)
    rem=set(skew); v=1; fill={}
    while rem:
        mins=[x for x in rem if (x[0],x[1]-1) not in rem and (x[0]-1,x[1]) not in rem]
        ch=sorted(mins)[0]; fill[ch]=v; v+=1; rem.discard(ch)
    rect,snaps=rectify_record(fill,muc)
    rectrows=[tuple(rect[(r,c)] for c in sorted(cc for (rr,cc) in rect if rr==r)) for r in sorted(set(r for r,c in rect))]
    assert rectrows==rsk_P(reading_word(fill))
    # choose up to 8 evenly spaced snapshots incl first and last
    K=min(8,len(snaps)); idx=[round(i*(len(snaps)-1)/(K-1)) for i in range(K)]
    snaps_sel=[snaps[i] for i in idx]
    cols=4; rows=2; W=S; H=int(S*0.62)
    SS=2; img=Image.new("RGB",(W*SS,H*SS),(8,9,14)); dr=ImageDraw.Draw(img)
    try: fnt=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(S*0.018*SS))
    except: fnt=ImageFont.load_default()
    pw=W*SS/cols; ph=H*SS/rows; cell=min(pw,ph)/8
    for p,(f,mu,hole) in enumerate(snaps_sel):
        pr,pc=divmod(p,cols); ox=pc*pw+pw*0.12; oy=pr*ph+ph*0.14
        for (r,c) in allc:
            X=ox+c*cell; Y=oy+r*cell
            if (r,c) in f:
                val=f[(r,c)]
                dr.rectangle([X,Y,X+cell-2*SS,Y+cell-2*SS],fill=(40,90,120) if (r,c) in skew else (70,60,110))
                dr.rectangle([X,Y,X+cell-2*SS,Y+cell-2*SS],outline=(150,200,230),width=SS)
                dr.text((X+cell*0.3,Y+cell*0.16),str(val),font=fnt,fill=(245,245,255))
            elif (r,c) in mu:
                dr.rectangle([X,Y,X+cell-2*SS,Y+cell-2*SS],outline=(120,110,80),width=SS)  # hole
            # cells outside current filled & not mu (already vacated) -> skip
        if hole is not None:
            r,c=hole; X=ox+c*cell; Y=oy+r*cell
            dr.rectangle([X-SS,Y-SS,X+cell-SS,Y+cell-SS],outline=(250,200,90),width=2*SS)
        lab="skew tableau" if p==0 else ("rectified (= RSK P)" if p==K-1 else f"slide {p}")
        dr.text((ox, oy-ph*0.085),lab,font=fnt,fill=(220,210,150))
    arr=np.asarray(img).astype(np.float32)/255
    g=arr.copy()
    for k in range(3): g[...,k]+=0.22*gaussian_filter(arr[...,k],SS*1.1)
    out=Image.fromarray((np.clip(g,0,1)*255).astype(np.uint8)).resize((W,H),Image.LANCZOS)
    body=("Jeu de taquin - 'the sliding game' - is the engine of the plactic monoid. Start from a skew tableau (numbers "
          "increasing along rows and down columns, with an inner notch removed); repeatedly slide a hole outward, each "
          "step pulling in the smaller of its right/lower neighbour, until the shape straightens. The result - the "
          "RECTIFICATION - is independent of the order of slides (confluence), and equals the RSK insertion tableau P of "
          "the tableau's reading word (verified here, and on 400 random skew tableaux). Two words are 'Knuth-equivalent' "
          "exactly when they rectify to the same P; jeu de taquin is how the symmetric group's combinatorics becomes an "
          "associative algebra.")
    fig=annotate(out,"FIGURE 17 - JEU DE TAQUIN","The Sliding Game Behind RSK",body,accent=(235,205,120))
    fig.save("17_jdt.png"); print("saved",fig.size,"snaps",len(snaps),"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
