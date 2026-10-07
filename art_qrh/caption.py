"""Caption block in my house style: serif-bold title, italic object line, small legend line. Plum ink."""
from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/truetype/liberation/'
INK=(92,77,102); SOFT=(130,116,140); CORAL=(240,118,104)
def caption(img, x, y, title, line1, line2, size, align='left', line3=None):
    d=ImageDraw.Draw(img)
    ft=ImageFont.truetype(F+'LiberationSerif-Bold.ttf',int(size))
    fi=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(size*0.48))
    fs=ImageFont.truetype(F+'LiberationSerif-Italic.ttf',int(size*0.36))
    rows=[(title,ft,INK),(line1,fi,SOFT),(line2,fs,SOFT)]+([(line3,fs,SOFT)] if line3 else [])
    yy=y
    for txt,f,c in rows:
        w=d.textlength(txt,font=f)
        xx=x if align=='left' else (x-w if align=='right' else x-w/2)
        d.text((xx,yy),txt,font=f,fill=c)
        yy+=f.size*1.32
    return yy
