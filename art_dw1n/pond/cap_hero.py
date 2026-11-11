from PIL import Image
import scene
im=Image.open('hero_raw.png').convert('RGB')
L=[("Four Schools, Sixteen Lily Pads, No Lane Swum Twice",'FreeSerifBold',0.0300,0.0085,None),
   ("Every edge of the four-dimensional cube is two one-way lanes. Each school visits all sixteen pads and comes home; together they swim every lane exactly once.",'FreeSerifItalic',0.0138,0.0062,None),
   ("one of 3,312 ways, and in 2,856 of them no school swims another’s loop backwards  ·  a fish always leaves a flowering pad for a bare one  ·  with the eight pads of an ordinary cube there is no way at all",'FreeSerifItalic',0.0108,0.0,(140,126,150))]
scene.caption(im,L,0.900)
im.save('../four_schools_4096.png',optimize=True)
im.resize((1100,1100),Image.LANCZOS).save('p_small.png')
