#!/bin/bash
# usage: prev.sh out W H spp kph [extra key=val]
out=$1; W=$2; H=$3; spp=$4; kph=$5; shift 5
./sticks scene.bin $W $H $spp $out.f32 y0=200 rc=25 kel=26 kaz=100 krad=4 ekey=2.6 kph=$kph cms=0.03 cx0=-75 cx1=75 cu0=-285 cu1=-115 cblur=2 \
  cel=52 caz=-90 dist=150 fov=32 lx=0 ly=0 lz=0 atr=0.50 atg=0.48 atb=0.62 abr=0.40 abg=0.36 abb=0.44 grain=0.02 keyvis=0 "$@"
