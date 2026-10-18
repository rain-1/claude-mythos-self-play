import numpy as np, json
from PIL import Image
import compose as C
ns=json.load(open('proto/hero_ns.json'))
im=Image.open('proto/hero_raw_4096.png').convert('RGB')
Wout=4096; S=590; g=118; top=150; tilt=30; cs=np.cos(np.radians(tilt))
x0=(Wout-(5*S+4*g))/2
for i,n in enumerate(ns):
    r,c=divmod(i,5)
    cx=x0+c*(S+g)+S/2; yb=top+r*(S+g)+S+0.06*S+8
    C.small_label(im,cx,yb,'the square' if n==4 else f'{n} sides',34)
im,y=C.caption(im,3720,'Odd, All but the Frame',
  'Twenty-four simple polygons whose every side has length exactly one, each folded inside a unit square: 3, 5, 7 … 21 sides. No even one has ever been found — except the square itself.',
  'paper quilling · gilded strip = the unit-side polygon, warm coils inside it, cool coils outside · every example found turns left four times and then zigzags · MathOverflow 481323 · ALL EXCEPT, i',scale=1.0)
im.save('../final/odd_all_but_the_frame.png'); print(y)
