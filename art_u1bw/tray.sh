#!/bin/bash
# trayscene.tray([1.52,3.52,2.67,4.53,3.43,2.33], pitch=9.4, rr=0.24, rb=0.5, sat=0.58) -> scene_tray.bin
./sticks2 scene_tray.bin 4096 3072 64 out/tray.f32 y0=300 kel=30 kaz=125 krad=4 ekey=1.7 kph=4e8 cms=0.012 cx0=-40 cx1=40 cu0=-350 cu1=-250 cblur=2 \
  cel=50 caz=-90 dist=84 fov=33 lx=0 ly=-1.5 lz=0 atr=0.72 atg=0.70 atb=0.82 abr=0.52 abg=0.48 abb=0.56 grain=0.02 keyvis=0 pfr=0.975 pfg=0.95 pfb=0.965 && touch out/tray.done
