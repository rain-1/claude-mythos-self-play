from PIL import Image, ImageDraw, ImageFont
FF='/usr/share/fonts/truetype/freefont/'
INK=(92,77,102)
def caption(img, x, y, lines, scale=1.0, align='left', ink=INK):
    """lines: list of (text, kind) kind in title/italic/small. x,y top-left (or top-right if align=right). sizes relative to width."""
    d=ImageDraw.Draw(img); W=img.width
    spec={'title':('FreeSerifBold.ttf',0.030),'italic':('FreeSerifItalic.ttf',0.017),'small':('FreeSerif.ttf',0.0125),'caps':('FreeSerif.ttf',0.0135)}
    for text,kind in lines:
        fn,sz=spec[kind]; f=ImageFont.truetype(FF+fn,int(W*sz*scale))
        if kind=='caps':
            text=' '.join(text.upper())
        bb=d.textbbox((0,0),text,font=f)
        xx=x if align=='left' else x-(bb[2]-bb[0])
        if align=='center': xx=x-(bb[2]-bb[0])/2
        d.text((xx,y),text,font=f,fill=ink)
        y+=int((bb[3]-bb[1])*1.0+W*sz*scale*0.62)
    return img
