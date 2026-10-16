#!/bin/bash
# final hero v2: stickscene.build_rows(278, sat=0.52, absk=0.42, beadcol=(0.05,0.08,0.12), beadmat=0, rb=0.42, tall=True) -> scene_hero2.bin
./sticks2 scene_hero2.bin 4096 4096 96 out/hero2.f32 y0=60 rc=30 kel=19 kaz=140 krad=4 ekey=1.8 kph=6e8 cms=0.012 cx0=-60 cx1=60 cu0=-110 cu1=60 cblur=2 \
  cel=28 caz=-72 dist=16 fov=48 lx=19.2 ly=-23.6 lz=1.3 ap=0.14 fd=13.17 pfr=0.975 pfg=0.95 pfb=0.965 \
  atr=0.72 atg=0.70 atb=0.82 abr=0.52 abg=0.48 abb=0.56 grain=0.02 keyvis=0 && touch out/hero2.done
