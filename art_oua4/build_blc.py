import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
import blc, blc_diagram as bd

# Programs Are Bitstrings — Binary Lambda Calculus. Every closed lambda term IS a bitstring
# (Tromp's BLC), and its universal-prior weight is exactly 2^-|bits|. Here are fundamental
# programs as Tromp lambda diagrams (blue = abstraction bar, gold = application link,
# white = variable line to its binder), each with its actual binary code and its weight.
S=int(sys.argv[1]) if len(sys.argv)>1 else 2048
tag=sys.argv[2] if len(sys.argv)>2 else ""

Y=blc.L(blc.A(blc.L(blc.A(blc.V(1),blc.A(blc.V(0),blc.V(0)))),
              blc.L(blc.A(blc.V(1),blc.A(blc.V(0),blc.V(0))))))
Omega=blc.Omega
gallery=[
 ("I","λx. x  — identity",blc.I),
 ("0","λf x. x  — zero / false",blc.church(0)),
 ("K","λx y. x  — true / const",blc.K),
 ("1","λf x. f x  — one",blc.church(1)),
 ("2","λf x. f (f x)  — two",blc.church(2)),
 ("succ","λn f x. f (n f x)",blc.SUCC),
 ("3","three",blc.church(3)),
 ("S","λx y z. x z (y z)",blc.S),
 ("plus","λm n f x. m f (n f x)",blc.PLUS),
 ("4","four",blc.church(4)),
 ("Y","λf.(λx.f(x x))(λx.f(x x))  — fixpoint",Y),
 ("Ω","(λx.x x)(λx.x x)  — never halts",Omega),
]
# sort by program length (= -log2 prior)
gallery=sorted(gallery,key=lambda g: len(blc.enc(g[2])))

COL_LAM=np.array([90,175,255.]); COL_APP=np.array([255,195,105.]); COL_VAR=np.array([240,242,250.])

def diagram_img(t, target_h, target_w, ss=3):
    Wd,H,lam,app,v=bd.segments_typed(t)
    # choose unit so it fits target box
    u=max(3,int(min(target_w/(Wd+2.0), target_h/(H+2.0))))
    pad=u
    Wp=(Wd)*u+2*pad; Hp=(H)*u+2*pad
    im=Image.new('RGB',(Wp*1,Hp*1),(0,0,0)); d=ImageDraw.Draw(im)
    lw=max(2,int(u*0.16))
    def L(x0,y0,x1,y1,c):
        d.line([(pad+x0*u,pad+y0*u),(pad+x1*u,pad+y1*u)],fill=tuple(int(x) for x in c),width=lw)
    for y,x0,x1 in lam: L(x0,y,x1,y,COL_LAM)
    for y,x0,x1 in app: L(x0,y,x1,y,COL_APP)
    for x,y0,y1 in v:   L(x,y0,x,y1,COL_VAR)
    a=np.asarray(im,np.float32)
    glow=gaussian_filter(a,sigma=(u*0.22,u*0.22,0))
    out=a+glow*0.7
    return np.clip(out,0,255), Wp, Hp

W=S
img=np.zeros((W,W,3),np.float32); img[:]=np.array([7,9,16])
COLS,ROWS=3,4
top=int(0.085*W); botpad=int(0.015*W)
cw=W//COLS; ch=(W-top-botpad)//ROWS
fb=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(0.0125*W))
fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",int(0.0090*W))
fm=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",int(0.0082*W))

tmp=Image.fromarray(img.astype(np.uint8)); draw=ImageDraw.Draw(tmp)

for k,(name,desc,t) in enumerate(gallery):
    bits=blc.enc(t); nb=len(bits)
    gx=k%COLS; gy=k//COLS
    cx=gx*cw; cy=top+gy*ch
    # name + desc
    draw.text((cx+int(0.02*W),cy+int(0.006*W)),name,fill=(232,224,205),font=fb)
    draw.text((cx+int(0.02*W),cy+int(0.024*W)),desc,fill=(120,140,165),font=fs)
    # diagram
    box_h=int(ch*0.52); box_w=int(cw*0.80)
    dimg,dw,dh=diagram_img(t, box_h, box_w)
    ox=cx+(cw-dw)//2; oy=cy+int(ch*0.20)
    oy=min(oy, cy+ch-dh-int(0.06*W))
    sub=img[oy:oy+dh, ox:ox+dw]
    img[oy:oy+dh, ox:ox+dw]=np.maximum(sub, dimg[:sub.shape[0],:sub.shape[1]])

# composite text/diagram already in img array; now redraw labels (bitstring + weight) after
out=Image.fromarray(np.clip(img,0,255).astype(np.uint8))
draw=ImageDraw.Draw(out)
# title
draw.text((int(0.02*W),int(0.028*W)),"PROGRAMS ARE BITSTRINGS",fill=(232,224,205),
          font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(0.020*W)))
draw.text((int(0.02*W),int(0.056*W)),
          "Binary Lambda Calculus — every closed λ-term is a bitstring; its universal-prior weight is exactly 2⁻ⁿ.  "
          "blue=λ  gold=application  white=variable→binder.",
          fill=(120,140,165),font=fs)
# redraw name/desc (they were on tmp not img) + bitstring + weight per cell
for k,(name,desc,t) in enumerate(gallery):
    bits=blc.enc(t); nb=len(bits)
    gx=k%COLS; gy=k//COLS; cx=gx*cw; cy=top+gy*ch
    draw.text((cx+int(0.02*W),cy+int(0.004*W)),name,fill=(236,228,208),font=fb)
    draw.text((cx+int(0.02*W),cy+int(0.022*W)),desc,fill=(120,140,165),font=fs)
    # bitstring as small cells
    bw=min(int(0.010*W), int((cw*0.86)/nb)); bw=max(3,bw); bh=int(bw*1.5)
    bx0=cx+int(0.02*W); by=cy+ch-int(0.052*W)
    for i,ch_ in enumerate(bits):
        col=(255,200,110) if ch_=='1' else (30,46,60)
        draw.rectangle([bx0+i*bw,by,bx0+i*bw+bw-1,by+bh],fill=col)
    draw.text((cx+int(0.02*W),cy+ch-int(0.030*W)),
              f"{bits}",fill=(110,128,150),font=fm)
    draw.text((cx+cw-int(0.20*W),cy+int(0.006*W)),
              f"|p|={nb}b   2^-{nb}",fill=(150,170,150),font=fm)
out.save(f"/home/user/claude-mythos-self-play/art_oua4/blc{tag}.png")
print("saved", f"blc{tag}.png  terms:", [(g[0],len(blc.enc(g[2]))) for g in gallery])
