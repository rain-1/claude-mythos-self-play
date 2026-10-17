#!/bin/bash
# usage: render.sh W H spp out.f32   (n=5 tray; scene.bin + tex.f32 from tray.py 5 60)
cd "$(dirname "$0")"
./sticks scene.bin $1 $2 $3 $4 tex=1 y0=60 rc=30 kel=24 kaz=115 krad=4 ekey=1.8 kph=${KPH:-4e8} cms=${CMS:-0.03} cx0=-42 cx1=42 cu0=-96 cu1=-24 cblur=2 \
  cel=${CEL:-56} caz=-90 dist=${DIST:-88} fov=${FOV:-44} lx=0 ly=${LY:-1} lz=0 ap=${AP:-0} fd=${FD:-88} pfr=0.975 pfg=0.95 pfb=0.965 atr=0.72 atg=0.70 atb=0.82 abr=0.52 abg=0.48 abb=0.56 grain=0.02 keyvis=0 nph=0 ${@:5}
