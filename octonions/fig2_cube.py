"""Figure 2 — the Fano plane as the corners of a cube (finite-geometry lens).
The 7 imaginary units = the 7 nonzero vectors of F_2^3 (3-bit codes); the 7
Fano lines = the triples whose bitwise XOR is zero. Lines drawn as translucent
triangular planes inside the cube."""
import numpy as np, sys
sys.path.insert(0,'octonions')
import octo, figkit
from PIL import Image, ImageDraw

def project(P3, rot, W, scale, persp=0.22):
    p=(rot@P3.T).T
    z=p[:,2]
    f=1.0/(1.0-persp*z)          # mild perspective, independent of pixel scale
    x=W/2+p[:,0]*scale*f; y=W/2-p[:,1]*scale*f
    return np.stack([x,y],1), z

def rotm(ax,ay):
    cx,sx=np.cos(ax),np.sin(ax); cy,sy=np.cos(ay),np.sin(ay)
    Rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]); Ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
    return Rx@Ry

def render(W=1600):
    # cube vertices, i = b0+2b1+4b2  -> position (b0,b1,b2)
    V=np.array([[ (i>>0)&1, (i>>1)&1, (i>>2)&1] for i in range(8)],float)-0.5
    rot=rotm(0.62,0.785)
    scr,z=project(V,rot,W,W*0.40)
    img=Image.new("RGB",(W,W),(9,10,18)); d=ImageDraw.Draw(img,"RGBA")
    def rgb(c,f=1.0): return tuple(min(255,int(255*v*f)) for v in c)
    # all 7 Fano lines as faint coloured web (context), behind the cube
    tris=sorted([((z[a]+z[b]+z[c])/3, li,(a,b,c)) for li,(a,b,c) in enumerate(octo.LINES)])
    for zc,li,(a,b,c) in tris:
        col=octo.UNIT_RGB[li+1]
        for (p,q) in [(a,b),(b,c),(c,a)]:
            d.line([tuple(scr[p]),tuple(scr[q])],fill=rgb(col,1.0)+(45,),width=2)
    # cube edges (bold near-white) : connect corners differing in one bit
    for i in range(8):
        for j in range(i+1,8):
            if bin(i^j).count("1")==1:
                far=(z[i]+z[j])/2
                br=185 if far<0 else 245
                d.line([tuple(scr[i]),tuple(scr[j])],fill=(br,br,255 if br>240 else br,235),width=6)
    # highlight ONE worked example line: e1 e2 = e3   (001 XOR 010 = 011)
    a,b,c=1,2,3; hi=octo.UNIT_RGB[3]
    d.polygon([tuple(scr[a]),tuple(scr[b]),tuple(scr[c])],fill=rgb(hi,1.0)+(55,))
    for (p,q) in [(a,b),(b,c),(c,a)]:
        d.line([tuple(scr[p]),tuple(scr[q])],fill=rgb(hi,1.0)+(255,),width=7)
    # origin 000 (the missing 8th corner) faint hollow
    o=0
    d.ellipse([scr[o,0]-16,scr[o,1]-16,scr[o,0]+16,scr[o,1]+16],outline=(110,116,140,200),width=4)
    fb=figkit.font("DejaVuSans-Bold.ttf",34); fs=figkit.font("DejaVuSans.ttf",24)
    # vertices 1..7 glowing + labels
    order=np.argsort(z)
    for i in order:
        if i==0: continue
        col=rgb(octo.UNIT_RGB[i]); x,y=scr[i]
        r=27
        d.ellipse([x-r-7,y-r-7,x+r+7,y+r+7],fill=rgb(octo.UNIT_RGB[i],1.0)+(60,))
        d.ellipse([x-r,y-r,x+r,y+r],fill=col,outline=(255,255,255,235),width=4)
    # labels drawn on RGB layer for crispness
    d2=ImageDraw.Draw(img)
    bits=lambda i:f"{(i>>2)&1}{(i>>1)&1}{i&1}"
    for i in range(1,8):
        x,y=scr[i]; col=rgb(octo.UNIT_RGB[i])
        lab=octo.sub(i)
        # offset label outward from cube centre
        dirv=np.array([x-W/2,y-W/2]); dirv=dirv/ (np.linalg.norm(dirv)+1e-9)
        lx,ly=x+dirv[0]*44, y+dirv[1]*44
        w=d2.textlength(lab,font=fb); d2.text((lx-w/2,ly-22),lab,font=fb,fill=col)
        w2=d2.textlength(bits(i),font=fs); d2.text((lx-w2/2,ly+16),bits(i),font=fs,fill=(150,158,180))
    x,y=scr[0]; d2.text((x+22,y-14),"000",font=fs,fill=(120,126,150))
    # on-figure worked equation
    feq=figkit.font("DejaVuSans-Bold.ttf",36)
    eq="e₁ · e₂ = e₃      (001 ⊕ 010 = 011)"
    d2.text((60,W-70),eq,font=feq,fill=rgb(octo.UNIT_RGB[3]))
    return img

if __name__=="__main__":
    viz=render(1600)
    body=("Label each imaginary unit e_i with the binary digits of its index: e_1=001, e_2=010, "
          "e_3=011, … e_7=111. These are exactly the seven non-zero points of the vector space "
          "F_2^3 — the seven corners of a cube (the eighth corner, 000, is the empty origin shown "
          "hollow). A Fano LINE is then nothing more than a triple of units whose bitwise XOR is "
          "zero: e_i e_j = e_k precisely when i XOR j = k. The faint coloured web shows all seven "
          "of these XOR-lines; one is highlighted in green — e_1 · e_2 = e_3, because 001 ⊕ 010 = "
          "011. So the Fano plane is the projective plane PG(2,2) over the two-element field, and "
          "octonion multiplication is, at heart, addition mod 2 carrying a sign.")
    fig=figkit.caption(viz,"FIGURE 2 · FINITE GEOMETRY","The Fano plane is a cube over F₂",
                       body,accent=(120,220,255))
    figkit.save(fig,"octonions/02_fano_cube.png")
    print("done",fig.size)
