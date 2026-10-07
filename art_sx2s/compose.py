import numpy as np, sys
from PIL import Image, ImageDraw
from caption import caption, CORAL
which=sys.argv[1]
if which=='hero':
    im=Image.open('hero_raw2.png').convert('RGB'); d=ImageDraw.Draw(im)
    x,y,r=2048,(4.85+np.pi/6*10)/11.6*4096,15
    d.ellipse([x-r,y-r,x+r,y+r],fill=CORAL,outline=(255,255,255),width=4)
    caption(im,2048,3655,'Every Copy Winds Once More',
      'Riemann’s function φ(t) = Σ exp(iπn²t) / iπn², 0 ≤ t ≤ 2, drawn as the closed curve it is',
      'each paper sheet is one more turn of its winding number, up to 27  ·  hue = the moment t of the nearest stretch of curve, one step per sheet',
      110,align='center',line3='coral: t = 0, where the curve leaves and, at t = 2, comes home')
    im.save('every_copy_winds_once_more.png',optimize=True)
elif which=='zoom':
    im=Image.open('zoom_raw2.png').convert('RGB'); a=np.asarray(im).astype(np.float32)
    H,W=a.shape[:2]; y=np.arange(H)[:,None,None]; y0=H-330; f=np.clip((y-(y0-140))/140,0,1)*0.93
    a=a*(1-f)+np.array([252.5,251,249.5])*f
    im=Image.fromarray(a.astype(np.uint8))
    caption(im,W/2,y0-10,'Both Wings Come Home at t = 1',
      'the same curve near φ(1) = iπ/12, enlarged 13×: copies of the whole heart, smaller and smaller, arriving from both sides at once',
      'sixty-odd nested paper sheets, one hue step per copy  ·  the pinch in the middle is φ(1) itself, the one point the copies never reach',
      92,align='center')
    im.save('both_wings_come_home.png',optimize=True)
