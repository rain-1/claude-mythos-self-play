import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from promotion import promotion
from figkit import annotate
import colorsys, time

def render(rows=(4,4,4,4)):
    import random
    t0=time.time(); n=sum(rows)
    shape=[(r,c) for r in range(len(rows)) for c in range(rows[r])]
    def rand_syt(rng):
        rem=set(shape); T={}; v=1
        while rem:
            mins=[x for x in rem if (x[0],x[1]-1) not in rem and (x[0]-1,x[1]) not in rem]
            ch=rng.choice(mins); T[ch]=v; v+=1; rem.discard(ch)
        return T
    def orblen(T):
        seen=[dict(T)]; U=promotion(T)
        while U!=seen[0]: seen.append(dict(U)); U=promotion(U)
        return len(seen)
    rng=random.Random(0); T0=None; best=0
    for _ in range(300):
        T=rand_syt(rng); L=orblen(T)
        if L>best: best=L; T0=dict(T)
        if best>=n: break
    orb=[dict(T0)]; U=promotion(T0)
    while U!=orb[0]: orb.append(dict(U)); U=promotion(U)
    assert all(promotion(orb[i])==orb[(i+1)%len(orb)] for i in range(len(orb)))
    print("orbit length",len(orb),"n",n)
    R=len(rows); Cc=rows[0]
    cell=110; pad=40; W=Cc*cell+2*pad; H=R*cell+2*pad+70
    def hue(v): return colorsys.hls_to_rgb((v-1)/n*0.85,0.5,0.62)
    try: fnt=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",46)
    except: fnt=ImageFont.load_default()
    def draw(T, step):
        im=Image.new("RGB",(W,H),(10,11,16)); dr=ImageDraw.Draw(im)
        for (r,c),v in T.items():
            X=pad+c*cell; Y=pad+r*cell+50
            col=tuple(int(255*x) for x in hue(v))
            dr.rounded_rectangle([X+4,Y+4,X+cell-4,Y+cell-4],radius=12,fill=col)
            s=str(v); tw=dr.textlength(s,font=fnt)
            dr.text((X+cell/2-tw/2,Y+cell/2-28),s,font=fnt,fill=(250,250,255))
        dr.text((pad, 14),f"promotion  ∂^{step}",font=fnt,fill=(230,215,150))
        return im
    frames=[draw(orb[i], i) for i in range(len(orb))]
    frames_big=[f.resize((W*2,H*2),Image.LANCZOS) for f in frames]
    frames_big[0].save("21_promotion.gif",save_all=True,append_images=frames_big[1:],
                       duration=520,loop=0,disposal=2)
    # static montage of first 8 (or all if <=8) frames as PNG
    k=min(8,len(orb)); cols=4; rows2=(k+cols-1)//cols
    th=frames[0].height; tw=frames[0].width
    mont=Image.new("RGB",(cols*tw+ (cols+1)*14, rows2*th+(rows2+1)*14),(14,14,20))
    for i in range(k):
        r,c=divmod(i,cols); mont.paste(frames[i],(14+c*(tw+14),14+r*(th+14)))
    body=("Schutzenberger PROMOTION, animated. Delete the 1 from a standard Young tableau, slide the hole out by jeu de "
          f"taquin, subtract 1 from every entry, and drop {n} into the vacated corner - one tick of a clock on tableaux. "
          f"On a rectangle it has finite order (here the {len(orb)}-step orbit of a {rows[0]}x{len(rows)} tableau returns "
          "exactly to the start, verified). The orbit sizes are governed by the CYCLIC SIEVING PHENOMENON of "
          "Reiner-Stanton-White: substitute a root of unity into the q-analogue of the hook-length formula and you read "
          "off, exactly, how many tableaux each rotation fixes. (Animated version: 21_promotion.gif.)")
    fig=annotate(mont,"FIGURE 21 - PROMOTION & CYCLIC SIEVING","A Clock on Tableaux",body,accent=(235,205,120),W=1600)
    fig.save("21_promotion.png"); print("saved gif+png",fig.size,"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
