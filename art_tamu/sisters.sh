#!/bin/bash
# companion: three maps with multiplier 3, same petals
cd "$(dirname "$0")"
O=10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25
A="--S 1360 --octs $O --rin 0.2 --rout 0.85 --A 0.06 --Qa 24 --Qb 120 --pleat 0.18 --mix 0.0 --light 0.08"
/usr/bin/python3 carnation/medallion.py $A --edge 3 --out sis_m1.png
/usr/bin/python3 carnation/medallion.py $A --src math_collatz/gen_d5.u32 --edge 1 --out sis_d5.png
/usr/bin/python3 carnation/medallion.py $A --src math_collatz/gen_d13.u32 --edge 1 --out sis_d13.png
/usr/bin/python3 - <<'PY'
from PIL import Image, ImageDraw, ImageFont
W,H=4096,1980; c=Image.new('RGB',(W,H),(253,252,250)); FD='/usr/share/fonts/truetype/'
for i,f in enumerate(['sis_m1','sis_d5','sis_d13']): c.paste(Image.open(f+'.png'),(8+1360*i,250))
d=ImageDraw.Draw(c); INK=(92,77,102)
ft=ImageFont.truetype(FD+'dejavu/DejaVuSerif-Bold.ttf',100); fl=ImageFont.truetype(FD+'dejavu/DejaVuSerif.ttf',54)
fi=ImageFont.truetype(FD+'liberation/LiberationSerif-Italic.ttf',50)
d.text((W/2,110),'Three Maps, One Scale',font=ft,fill=INK,anchor='mm')
d.text((W/2,195),'n → (3n + d)/2ᵛ on odd n below 2²⁶, sixteen paper sheets per flower, one per octave; each edge is the density of the largest basin around the circle of pitch',font=fi,fill=INK,anchor='mm')
for i,(t,s) in enumerate([('3n − 1','three cycles: 1 · 5 · 17'),('3n + 5','five cycles: 1 · 19 · 23 · 187 · 347'),('3n + 13','nine cycles')]):
    x=8+1360*i+680; d.text((x,1660),t,font=fl,fill=INK,anchor='mm'); d.text((x,1730),s,font=fi,fill=INK,anchor='mm')
d.text((W/2,1870),'the cycles differ, the song does not: every map that multiplies by 3 keeps the frequencies where 3¹² ≈ 2¹⁹ and 3⁵³ ≈ 2⁸⁴: twelve petals near the centre, fifty-three frills at the rim',font=fi,fill=INK,anchor='mm')
c.save('three_maps_one_scale.png')
PY
rm -f sis_m1.png sis_d5.png sis_d13.png
