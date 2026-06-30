import numpy as np
from PIL import Image, ImageDraw, ImageFont

def _font(sz, bold=True):
    base="/usr/share/fonts/truetype/dejavu/"
    try: return ImageFont.truetype(base+("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), sz)
    except: return ImageFont.load_default()

def wrap(draw, text, font, maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if draw.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines

def annotate(viz_img, tag, title, body, accent=(235,180,70), W=None, pad=48):
    """viz_img: PIL RGB. Returns new PIL with a bottom annotation block."""
    if W is None: W=viz_img.width
    if viz_img.width!=W:
        viz_img=viz_img.resize((W,int(viz_img.height*W/viz_img.width)),Image.LANCZOS)
    f_tag=_font(int(W*0.018)); f_title=_font(int(W*0.032)); f_body=_font(int(W*0.020),bold=False)
    tmp=Image.new("RGB",(10,10)); d=ImageDraw.Draw(tmp)
    bw=W-2*pad-24
    body_lines=wrap(d,body,f_body,bw)
    lh=int(W*0.028)
    block_h=int(W*0.018)+int(W*0.045)+len(body_lines)*lh+int(pad*1.6)
    out=Image.new("RGB",(W,viz_img.height+block_h),(8,8,12))
    out.paste(viz_img,(0,0))
    dr=ImageDraw.Draw(out)
    y0=viz_img.height+int(pad*0.6)
    dr.rectangle([pad,y0,pad+8,y0+int(W*0.018)+int(W*0.045)+2],fill=accent)
    x=pad+24
    dr.text((x,y0),tag,font=f_tag,fill=accent)
    dr.text((x,y0+int(W*0.024)),title,font=f_title,fill=(238,238,245))
    yy=y0+int(W*0.024)+int(W*0.045)
    for ln in body_lines:
        dr.text((x,yy),ln,font=f_body,fill=(170,172,182)); yy+=lh
    return out
