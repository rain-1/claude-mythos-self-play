"""Mathieu Fig 2 — S(5,8,24), the octads, on a 4x6 grid (MOG-style)."""
import numpy as np, sys, math
sys.path.insert(0,'mathieu'); sys.path.insert(0,'octonions'); sys.path.insert(0,'triality')
import golay, figkit
from tdraw import Canvas

def grid_pos(p, x0,y0,cell):
    r=p%4; c=p//4
    return (x0+c*cell+cell/2, y0+r*cell+cell/2)

def draw_grid(cv, octad, x0,y0,cell, big=False):
    W=cv.W
    on=set(np.where(octad)[0].tolist())
    for p in range(24):
        x,y=grid_pos(p,x0,y0,cell)
        if p in on:
            cv.splat((x,y),(1.0,0.78,0.30),radius=cell*0.18,bright=1.7)
            cv.splat((x,y),(1,1,1),radius=cell*0.07,bright=1.3)
        else:
            cv.splat((x,y),(0.32,0.38,0.55),radius=cell*0.09,bright=0.9)

def render(W=1600):
    O=golay.octads()
    Hh=1180
    cv=Canvas(W,bg=(0.012,0.013,0.024))
    # main octad (pick a balanced-looking one)
    main=O[120]
    cell=W*0.085; x0=W*0.30; y0=Hh*0.10
    # grid frame lines
    draw_grid(cv,main,x0,y0,cell,big=True)
    # three small example octads
    sc=W*0.045
    for i,oi in enumerate([3,400,700]):
        draw_grid(cv,O[oi], W*0.10+i*W*0.0, Hh*0.62+0, sc)  # placeholder, redone below
    img=cv.finish(W,bloom=(W*0.0007+0.6,W*0.005),gloss=(0.45,0.28),expo=1.2)
    from PIL import ImageDraw
    d=ImageDraw.Draw(img)
    # redraw small octads cleanly as separate mini grids with PIL after glow? simpler: new canvas
    return img, main

def render_full(W=1600):
    O=golay.octads()
    Hh=1220
    cv=Canvas(W,bg=(0.012,0.013,0.024))
    cell=W*0.080; x0=W*0.32; y0=Hh*0.085
    draw_grid(cv,O[120],x0,y0,cell)
    # three mini grids along bottom
    mc=W*0.030
    minis=[O[3],O[260],O[700]]
    mx=[W*0.09,W*0.40,W*0.71]; my=Hh*0.70
    for g,xx in zip(minis,mx):
        draw_grid(cv,g,xx,my,mc)
    img=cv.finish(W,bloom=(1.4,W*0.004),gloss=(0.32,0.20),expo=1.15)
    from PIL import ImageDraw
    d=ImageDraw.Draw(img)
    fb=figkit.font("DejaVuSans-Bold.ttf",40); fs=figkit.font("DejaVuSans.ttf",30)
    d.text((x0,y0-58),"one octad  (8 of the 24 points)",font=fs,fill=(255,205,120))
    d.text((W*0.045,Hh*0.625),"three more of the 759 octads:",font=fs,fill=(170,180,205))
    fe=figkit.font("DejaVuSans-Bold.ttf",38)
    d.text((W*0.045,Hh-92),"S(5,8,24):  every 5 of the 24 points lie in exactly ONE octad   ·   759 octads",
           font=figkit.font("DejaVuSans-Bold.ttf",34),fill=(235,240,250))
    return img.crop((0,0,W,Hh))

if __name__=="__main__":
    viz=render_full(1600)
    body=("Take 24 points (here a 4×6 grid, the layout Conway called the Miracle Octad Generator). "
          "There is a way to choose 759 special 8-element subsets — OCTADS — with a magical "
          "property: any 5 of the 24 points lie in exactly one octad. No fewer determine it, no "
          "more are needed; five points name a unique eight. This is the Steiner system S(5,8,24), "
          "and the octads are exactly the weight-8 codewords of the binary Golay code (verified "
          "here: weight distribution 1, 759, 2576, 759, 1). Its symmetry group — all permutations "
          "of the 24 points that send octads to octads — is the Mathieu group M₂₄, of order "
          "244,823,040, one of the 26 sporadic simple groups and 5-fold transitive. The humble "
          "Fano plane was the Steiner system S(2,3,7); this is its giant, miraculous sibling.")
    fig=figkit.caption(viz,"MATHIEU · THE DESIGN","S(5,8,24) — five points name an eight",
                       body,accent=(255,205,120))
    figkit.save(fig,"mathieu/02_octads_mog.png")
    print("done",fig.size)
