import numpy as np, random
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from patterns import catalan_upto, uniform_av231, avoids_231
from figkit import annotate
import time

def render(n=3000, S=1500, seed=7):
    t0=time.time(); rng=random.Random(seed)
    C=catalan_upto(n)
    p=np.array(uniform_av231(n,C,rng))
    assert avoids_231(p.tolist())
    G=int(S*0.72)
    d=np.zeros((G,G))
    xi=((np.arange(n))/n*(G-1)).astype(int); yi=((n-1-p+1-1)/n*(G-1)).astype(int)
    np.add.at(d,(yi,xi),1.0)
    d=gaussian_filter(d,1.0); d/=np.percentile(d[d>0],99.5); d=np.clip(d,0,1)**0.7
    img=np.zeros((G,G,3)); col=np.array([1.0,0.55,0.25])
    for k in range(3): img[...,k]=d*col[k]+0.4*gaussian_filter(d*col[k],2)
    img=np.clip(img,0,1)
    canvas=Image.new("RGB",(S,G+10),(8,8,12)); canvas.paste(Image.fromarray((img*255).astype(np.uint8)),(8,5))
    dr=ImageDraw.Draw(canvas)
    try:
        fnt=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(S*0.017))
        fsm=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(S*0.013))
    except: fnt=fsm=ImageFont.load_default()
    dr.text((24,12),f"uniform 231-avoiding permutation, n={n}",font=fnt,fill=(255,210,150))
    # small worked example: a 231-avoiding perm matrix + a 'forbidden 231' glyph
    rng2=random.Random(3); sp=uniform_av231(9,C,rng2)
    x0=int(S*0.70); y0=int(G*0.06); cell=int(S*0.026)
    dr.text((x0,y0-int(cell*1.2)),"small example (n=9):",font=fsm,fill=(220,220,230))
    for i,v in enumerate(sp):
        X=x0+i*cell; Y=y0+(9-v)*cell
        dr.rectangle([X,Y,X+cell-3,Y+cell-3],fill=(255,180,110))
    # forbidden pattern glyph
    yp=y0+int(cell*10.2)
    dr.text((x0,yp),"forbidden:  2 3 1",font=fsm,fill=(255,140,140))
    pat=[2,3,1]
    for i,v in enumerate(pat):
        X=x0+i*cell; Y=yp+int(cell*1.2)+(3-v)*cell
        dr.rectangle([X,Y,X+cell-3,Y+cell-3],outline=(255,120,120),width=2)
    body=("A permutation AVOIDS the pattern 231 if no three positions i<j<k carry values in the relative order "
          "2-3-1 (a value, a larger one, then a smaller-than-both). The 231-avoiders of length n number exactly the "
          f"Catalan number C_n (verified: 1,2,5,14,42,132,429,...) - and so do the avoiders of ANY single length-3 "
          "pattern (all six are Wilf-equivalent). They are precisely Knuth's STACK-SORTABLE permutations. Sampled here "
          "EXACTLY uniformly via the recursive Catalan decomposition sigma = L (max) R. At scale the matrix reveals the "
          "class's permuton limit shape - structure that a uniform permutation (white noise) has no trace of.")
    fig=annotate(canvas,"FIGURE 7 - PATTERN AVOIDANCE","Catalan's Permutations",body,accent=(245,160,90))
    fig.save("07_patterns.png"); print("saved",fig.size,"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
