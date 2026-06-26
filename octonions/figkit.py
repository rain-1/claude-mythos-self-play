"""Figure compositor: a visualization panel + an annotation block at the bottom."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTDIR="/usr/share/fonts/truetype/dejavu/"
def font(name,sz):
    for p in [FONTDIR+name, name]:
        try: return ImageFont.truetype(p,sz)
        except Exception: pass
    return ImageFont.load_default()

def wrap(draw,text,fnt,maxw):
    out=[]
    for para in text.split("\n"):
        words=para.split(" "); line=""
        for w in words:
            t=(line+" "+w).strip()
            if draw.textlength(t,font=fnt)<=maxw: line=t
            else:
                if line: out.append(line)
                line=w
        out.append(line)
    return out

def caption(viz, tag, title, body, accent=(120,200,255), W=None,
            pad=54, title_sz=46, body_sz=31, tag_sz=27, bg=(8,9,16)):
    """viz: PIL image (will be width-matched). Returns composed figure."""
    if W is None: W=viz.width
    if viz.width!=W:
        viz=viz.resize((W,int(viz.height*W/viz.width)),Image.LANCZOS)
    ft=font("DejaVuSans-Bold.ttf",title_sz)
    fb=font("DejaVuSans.ttf",body_sz)
    fg=font("DejaVuSans-Bold.ttf",tag_sz)
    tmp=Image.new("RGB",(10,10)); dd=ImageDraw.Draw(tmp)
    maxw=W-2*pad
    blines=wrap(dd,body,fb,maxw)
    lh=int(body_sz*1.42)
    cap_h=pad + tag_sz+14 + title_sz+22 + len(blines)*lh + pad
    H=viz.height+cap_h
    fig=Image.new("RGB",(W,H),bg)
    fig.paste(viz,(0,0))
    d=ImageDraw.Draw(fig)
    y0=viz.height
    # separator + left accent bar
    d.rectangle([0,y0,W,y0+4],fill=tuple(int(c*0.5) for c in accent))
    d.rectangle([0,y0,10,H],fill=accent)
    y=y0+pad
    d.text((pad,y),tag,font=fg,fill=accent); y+=tag_sz+14
    d.text((pad,y),title,font=ft,fill=(238,242,250)); y+=title_sz+22
    for ln in blines:
        d.text((pad,y),ln,font=fb,fill=(176,186,205)); y+=lh
    return fig

def save(fig,path):
    fig.save(path); return path
