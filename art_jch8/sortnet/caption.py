from PIL import ImageDraw, ImageFont
FS='/usr/share/fonts/truetype/freefont/'
INK=(92,77,102); SOFT=(120,104,128)
def caption(im,lines,y0,scale=None,align='center',x0=None):
    S=scale or im.size[0]; d=ImageDraw.Draw(im); W=im.size[0]
    fonts=[ImageFont.truetype(FS+'FreeSerifBold.ttf',int(S*0.021)),ImageFont.truetype(FS+'FreeSerifItalic.ttf',int(S*0.0122)),ImageFont.truetype(FS+'FreeSerif.ttf',int(S*0.0108))]
    gaps=[0.031,0.020,0.0165]; y=y0
    for k,t in enumerate(lines):
        f=fonts[min(k,2)]; w=d.textlength(t,font=f)
        x=(W-w)/2 if align=='center' else x0
        d.text((x,y),t,font=f,fill=INK if k<2 else SOFT); y+=int(S*gaps[min(k,2)])
    return im
