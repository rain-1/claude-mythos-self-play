import mobius, caption
im=mobius.render(48,7,W=3200,H=3200,ss=2,out='tmp_mob.png',dist=5.7,tilt=0.95,spin=0.4,cy=0.39,fov=0.6)
caption.caption(im,['Forty-Eight Loops, Each Crossing Every Other Once',
 'A random sorting network of 48 wires wrapped once around a Möbius band: when all 1,128 swaps are done the order is reversed,',
 'and the half-twist of the band carries every wire back to the place it started. So each wire closes into a loop that meets each of the others',
 'exactly once: an arrangement of 48 pseudolines in the projective plane, the one rule the park keeps. Colour follows each wire’s starting place.'],int(3200*0.87),scale=3200)
im.save('forty_eight_loops.png')
