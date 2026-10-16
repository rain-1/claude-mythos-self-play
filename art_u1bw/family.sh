#!/bin/bash
# pipescene.family3(place=[(3,-30,-24),(7,-19,-24),(31,27,-15),(127,0,34)], rings=[(-3,-22,4.5),(60,-1,8.0)], sat=0.45, absk=0.3, bsat=0.6, babsk=0.4, br=0.40)

./sticks2 scene_family3.bin 4096 2731 40 out/family.f32 y0=300 kel=24 kaz=115 krad=4 ekey=1.6 kph=4e8 cms=0.025 cx0=-100 cx1=130 cu0=-345 cu1=-150 cblur=2 \
  cel=40 caz=-100 dist=123 fov=44 lx=1 ly=10 lz=0 atr=0.86 atg=0.80 atb=0.92 abr=0.55 abg=0.5 abb=0.58 grain=0.02 keyvis=0 pfr=0.975 pfg=0.95 pfb=0.965 && touch out/family.done
