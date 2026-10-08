# Caption block on paper: serif-bold title, italic statement line(s), small legend line(s). Plum ink.
from PIL import Image, ImageDraw, ImageFont
FS='/usr/share/fonts/truetype/freefont/'
INK=(92,77,102); CORAL=(232,104,98)
def caption(img, x, y, title, lines, legend, scale=1.0, align='left', width=None):
    d=ImageDraw.Draw(img); W=img.size[0]
    ft=ImageFont.truetype(FS+'FreeSerifBold.ttf', int(64*scale))
    fi=ImageFont.truetype(FS+'FreeSerifItalic.ttf', int(34*scale))
    fl=ImageFont.truetype(FS+'FreeSerif.ttf', int(28*scale))
    def put(txt,f,yy,fill):
        w=d.textlength(txt,font=f)
        xx=x if align=='left' else (x-w if align=='right' else x-w/2)
        d.text((xx,yy),txt,font=f,fill=fill)
    put(title,ft,y,INK); y+=int(86*scale)
    for l in lines: put(l,fi,y,INK); y+=int(46*scale)
    y+=int(8*scale)
    for l in legend:
        fill=CORAL if l.startswith('coral') else INK
        put(l,fl,y,fill); y+=int(38*scale)
    return img
