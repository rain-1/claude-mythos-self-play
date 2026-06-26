"""Mathieu Fig 3 — the weight distribution of the binary Golay code [24,12,8]."""
import sys, math
sys.path.insert(0,'mathieu'); sys.path.insert(0,'octonions')
import golay, figkit
from PIL import Image, ImageDraw

def render(W=1600):
    wd=golay.weight_dist()        # {0:1,8:759,12:2576,16:759,24:1}
    Hh=1080
    img=Image.new("RGB",(W,Hh),(10,11,19)); d=ImageDraw.Draw(img)
    items=sorted(wd.items())
    base=Hh*0.80; maxh=Hh*0.56
    mx=max(c for _,c in items)
    n=len(items); slot=W*0.74/n; x0=W*0.16
    cols=[(120,160,255),(255,205,110),(120,235,160),(255,205,110),(120,160,255)]
    fnum=figkit.font("DejaVuSans-Bold.ttf",40); fw=figkit.font("DejaVuSans-Bold.ttf",34); fs=figkit.font("DejaVuSans.ttf",30)
    for i,(w,c) in enumerate(items):
        h=maxh*(c/mx)**0.5
        cx=x0+slot*(i+0.5); bw=slot*0.5
        col=cols[i]
        d.rectangle([cx-bw/2,base-h,cx+bw/2,base],fill=col)
        d.rectangle([cx-bw/2,base-h,cx+bw/2,base],outline=(255,255,255),width=2)
        cnt=str(c); ww=d.textlength(cnt,font=fnum); d.text((cx-ww/2,base-h-52),cnt,font=fnum,fill=col)
        lab=f"wt {w}"; wl=d.textlength(lab,font=fw); d.text((cx-wl/2,base+18),lab,font=fw,fill=(210,216,235))
    d.line([(x0,base),(x0+W*0.74,base)],fill=(80,86,108),width=3)
    title="2¹² = 4096 codewords      ·      bar height ∝ √count"
    d.text((W*0.16,Hh*0.10),title,font=fs,fill=(170,180,205))
    d.text((W*0.16,Hh*0.045),"The binary Golay code  [24, 12, 8]",font=figkit.font("DejaVuSans-Bold.ttf",46),fill=(235,240,250))
    return img

if __name__=="__main__":
    viz=render(1600)
    body=("The whole of M₂₄ rests on one astonishingly rigid object: the binary Golay code, a set "
          "of 4096 length-24 binary strings (a 12-dimensional subspace of 𝔽₂²⁴) in which any two "
          "differ in at least 8 places. Its weight distribution — how many codewords have each "
          "number of 1s — is perfectly symmetric and almost empty: 1 word of weight 0, then "
          "nothing until 759 words of weight 8 (the OCTADS), 2576 of weight 12 (the dodecads), 759 "
          "of weight 16, and a single all-ones word of weight 24. The forbidden gaps (no weights "
          "1–7, 9–11, …) are exactly what make the code correct up to 3 errors and what force the "
          "Steiner system S(5,8,24) into existence. This severe, gap-toothed spectrum is the "
          "fingerprint of one of the most perfect structures in mathematics.")
    fig=figkit.caption(viz,"MATHIEU · CODING THEORY","The Golay code's weight spectrum",
                       body,accent=(120,235,160))
    figkit.save(fig,"mathieu/03_golay_weights.png")
    print("done",fig.size)
