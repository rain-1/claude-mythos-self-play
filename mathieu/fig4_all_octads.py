"""Mathieu Fig 4 — all 759 octads of S(5,8,24), each a mini 4x6 MOG glyph."""
import numpy as np, sys, math
sys.path.insert(0,'mathieu'); sys.path.insert(0,'octonions')
import golay, figkit
from PIL import Image, ImageDraw, ImageFilter
import colorsys

def render(W=1650):
    O=golay.octads()                       # (759,24)
    # sort for visual structure: by integer value of the codeword
    keys=[int("".join(map(str,o)),2) for o in O]
    O=O[np.argsort(keys)]
    cols,rows=33,23                          # 759
    margin=70; gut=10
    cellW=(W-2*margin-(cols-1)*gut)/cols
    cellH=cellW*4/6
    Hh=int(margin*2+rows*cellH+(rows-1)*gut)+10
    img=Image.new("RGB",(W,Hh),(9,10,18)); d=ImageDraw.Draw(img)
    dotR=cellW/6*0.36
    for n in range(len(O)):
        gr=n//cols; gc=n%cols
        x0=margin+gc*(cellW+gut); y0=margin+gr*(cellH+gut)
        hue=(n/len(O))*0.85
        r,g,b=colorsys.hsv_to_rgb(hue,0.55,1.0); lit=(int(r*255),int(g*255),int(b*255))
        on=set(np.where(O[n])[0].tolist())
        for p in range(24):
            rr=p%4; cc=p//4
            cx=x0+(cc+0.5)*cellW/6; cy=y0+(rr+0.5)*cellH/4
            if p in on:
                d.ellipse([cx-dotR,cy-dotR,cx+dotR,cy+dotR],fill=lit)
            else:
                d.ellipse([cx-dotR*0.5,cy-dotR*0.5,cx+dotR*0.5,cy+dotR*0.5],fill=(34,38,52))
    # gentle bloom
    arr=np.asarray(img).astype(np.float32)/255
    from scipy.ndimage import gaussian_filter
    g2=np.stack([gaussian_filter(arr[...,c],1.4) for c in range(3)],-1)
    out=1.0-np.exp(-1.25*(arr+0.4*g2))
    return Image.fromarray((np.clip(out,0,1)*255).astype('uint8'))

if __name__=="__main__":
    viz=render(1650)
    body=("Every single one of the 759 OCTADS — the special 8-point blocks of the Steiner system "
          "S(5,8,24) — drawn at once, each as a little 4×6 grid with its 8 points lit (here sorted "
          "by codeword value and tinted across the spectrum so the tapestry's structure shows). "
          "These 759 patterns are the weight-8 words of the binary Golay code, and they are "
          "miraculously interlocked: any 5 of the 24 points you could name appear together in "
          "exactly ONE of these 759 pictures, never two. The Mathieu group M₂₄ is precisely the set "
          "of permutations of the 24 points that shuffle these 759 octads among themselves. It is "
          "rare to be able to hold an entire 5-transitive design in one image — but here is the "
          "whole of S(5,8,24).")
    fig=figkit.caption(viz,"MATHIEU · ALL OF THEM","The 759 octads, all at once",
                       body,accent=(255,205,120),W=1650)
    figkit.save(fig,"mathieu/04_all_octads.png")
    print("done",fig.size)
