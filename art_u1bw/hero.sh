#!/bin/bash
# final hero: seed 278 tray of broken sticks (scene_hero.bin from stickscene.build_rows(278, sat=0.52, absk=0.42, beadmat=0, rb=0.42))
./sticks scene_hero.bin 4096 4096 64 out/hero.f32 y0=60 rc=30 kel=19 kaz=140 krad=4 ekey=1.8 kph=6e8 cms=0.012 cx0=-60 cx1=60 cu0=-110 cu1=60 cblur=2 \
  cel=31 caz=-72 dist=20 fov=48 lx=18.5 ly=-22.5 lz=1 ap=0.18 fd=16.08 pfr=0.975 pfg=0.95 pfb=0.965 \
  atr=0.72 atg=0.70 atb=0.82 abr=0.52 abg=0.48 abb=0.56 grain=0.02 keyvis=0 && touch out/hero.done
