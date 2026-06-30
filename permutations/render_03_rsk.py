import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from figkit import annotate
from bisect import bisect_left, bisect_right
import time

def lis_chain(seq):
    n=len(seq); tails=[]; tails_idx=[]; parent=[-1]*n
    for i,x in enumerate(seq):
        j=bisect_left(tails,x)
        if j==len(tails): tails.append(x); tails_idx.append(i)
        else: tails[j]=x; tails_idx[j]=i
        parent[i]=tails_idx[j-1] if j>0 else -1
    # reconstruct
    chain=[]; k=tails_idx[-1]
    while k!=-1: chain.append(k); k=parent[k]
    return chain[::-1]

def rsk(perm):
    P=[]; Q=[]
    for t,x in enumerate(perm,1):
        r=0; v=x
        while True:
            if r==len(P): P.append([v]); Q.append([t]); break
            row=P[r]; j=bisect_right(row,v)
            if j==len(row): row.append(v); Q[r].append(t); break
            row[j],v=v,row[j]; r+=1
    return P,Q

def render(n=500, S=1600, seed=4):
    t0=time.time(); rng=np.random.default_rng(seed)
    perm=rng.permutation(n)
    chain=lis_chain(perm.tolist())
    G=int(S*0.74)
    field=np.zeros((G,G,3))
    px=(np.arange(n)/n*(G-1)).astype(int); py=((n-1-perm)/n*(G-1)).astype(int)
    # all points dim teal
    for ox in (0,1):
      for oy in (0,1):
        np.add.at(field.reshape(-1,3),np.clip(py+oy,0,G-1)*G+np.clip(px+ox,0,G-1),np.array([0.18,0.5,0.55]))
    # LIS chain gold polyline + points
    cx=px[chain]; cy=py[chain]
    for a in range(len(chain)-1):
        L=int(max(2,abs(cx[a+1]-cx[a])+abs(cy[a+1]-cy[a])))
        tt=np.linspace(0,1,L)
        xs=(cx[a]+(cx[a+1]-cx[a])*tt).astype(int); ys=(cy[a]+(cy[a+1]-cy[a])*tt).astype(int)
        for ox in (0,1):
          for oy in (0,1):
            np.add.at(field.reshape(-1,3),np.clip(ys+oy,0,G-1)*G+np.clip(xs+ox,0,G-1),np.array([1.0,0.82,0.35])*0.5)
    for a in range(len(chain)):
        yy,xx=cy[a],cx[a]; field[max(0,yy-2):yy+3,max(0,xx-2):xx+3]+=np.array([1.0,0.9,0.5])*0.8
    field/=np.percentile(field[field>0],99.7); field=np.clip(field,0,1)
    img=field.copy()
    for k in range(3): img[...,k]+=0.5*gaussian_filter(field[...,k],2.0)
    img=np.clip(img,0,1)
    canvas=Image.new("RGB",(S,G+10),(8,8,12))
    canvas.paste(Image.fromarray((img*255).astype(np.uint8)),(10,5))
    dr=ImageDraw.Draw(canvas)
    try:
        fnt=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(S*0.018))
        fsm=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(S*0.014))
    except: fnt=fsm=ImageFont.load_default()
    dr.text((30,12),f"LIS length = {len(chain)}    2*sqrt(n) = {2*np.sqrt(n):.0f}",font=fnt,fill=(255,220,120))
    # worked RSK inset (small perm)
    small=[3,1,4,2,5]; P,Q=rsk(small)
    x0=int(S*0.62); y0=int(G*0.06); cell=int(S*0.030)
    dr.text((x0,y0-int(cell*1.1)),"RSK:  word 3 1 4 2 5  ->  (P, Q)",font=fsm,fill=(220,220,230))
    def draw_tab(T,ox,oy,col):
        for r,row in enumerate(T):
            for c,val in enumerate(row):
                X=ox+c*cell; Y=oy+r*cell
                dr.rectangle([X,Y,X+cell-3,Y+cell-3],outline=col,width=2)
                dr.text((X+cell*0.28,Y+cell*0.16),str(val),font=fsm,fill=col)
    draw_tab(P,x0,y0,(120,200,255)); dr.text((x0,y0+3*cell+4),"P (insert)",font=fsm,fill=(120,200,255))
    draw_tab(Q,x0+int(S*0.17),y0,(255,180,120)); dr.text((x0+int(S*0.17),y0+3*cell+4),"Q (record)",font=fsm,fill=(255,180,120))
    body=("Robinson-Schensted-Knuth (RSK) bijects each permutation with a pair of standard Young tableaux (P,Q) of the "
          "same shape (verified inset). The first row's length equals the LONGEST INCREASING SUBSEQUENCE - the gold chain "
          f"through the n={n} point-matrix (here length {len(chain)}). Patience sorting computes it in O(n log n). "
          "Logan-Shepp/Vershik-Kerov + Baik-Deift-Johansson: for a random permutation the LIS concentrates at 2*sqrt(n) "
          "with Tracy-Widom fluctuations of order n^(1/6) - the same RSK shape whose limit is the curve in the main "
          "set's piece 05.")
    fig=annotate(canvas,"FIGURE 3 - RSK & ULAM'S PROBLEM","The Longest Increasing Subsequence",body,accent=(245,210,110))
    fig.save("03_rsk.png"); print("saved",fig.size,"LIS",len(chain),"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
