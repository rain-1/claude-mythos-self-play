python3 q5.py 4096 2 1 q5_raw.png 0.7 0.625 && python3 - <<'PY'
from PIL import Image
import scene
im=Image.open('q5_raw.png').convert('RGB')
L=[("One Loop, Turned Five Times",'FreeSerifBold',0.0300,0.0085,None),
   ("The five-dimensional cube has thirty-two pads and 160 one-way lanes. A single loop through every pad, copied at each fifth of a turn, swims them all.",'FreeSerifItalic',0.0138,0.0062,None),
   ("exactly 96 loops do this in five dimensions and 12 in four  ·  we found one in every dimension from 4 to 10, and none exists in 3  ·  the two pads at the centre are opposite corners that the drawing lays side by side",'FreeSerifItalic',0.0108,0.0,(140,126,150))]
scene.caption(im,L,0.900)
im.save('../one_loop_five_times_4096.png',optimize=True)
im.resize((1100,1100),Image.LANCZOS).save('q5_small.png')
PY
