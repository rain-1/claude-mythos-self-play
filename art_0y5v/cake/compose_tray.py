import sys; sys.path.insert(0,'..')
from PIL import Image
from caption import caption
img=Image.open('tray_raw.png').convert('RGB'); W,H=img.size; s=W/4096
title='Only the Round One Insists'
line=('Nine petits fours, each cut into three convex slices with equal cake and equal edge. Colour = congruence class: '
      'eight shapes allow three strangers; only the disc forces twins.')
legend=('Triangle, square, pentagon / ellipse b:a = 0.8, disc, hexagon / half-disc (two chords), Reuleaux triangle, '
        '1.5 : 1 rectangle. A fair Y-cut has 5 unknowns and 4 equations, so fair cuts come in loops; a disc’s loop is only '
        'its own rotation. CONJ: the disc is the only convex shape that cannot be cut fairly into three different pieces. (MO 516282)')
img,y=caption(img,title,line,legend,int(300*s),int(H*0.80),int(3500*s),scale=s*1.12,fade=(int(H*0.76),int(H*0.80),(228,238,252)))
img.save('../only_the_round_one.png'); print(y/H)
