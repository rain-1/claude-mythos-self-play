#!/bin/bash
# The Oculus: 4096² beauty pass (24 spp) + 1024² fog-only pass (48 spp), composited by compose_dome.py
cd "$(dirname "$0")"
V="ex=-0.6 ey=-0.6 ez=3.7 lx=0.3 ly=0.25 lz=5.6 fov=0.68"
C="mtint=0.25 F0=0.32 nacre=0.75 lightmode=1 glowk=0 maxd=30 skyk=0.8 wamb=0.28 wk=0.9 lpx=0 lpy=0 lpz=6 wsun=1.6 sx=-0.55 sy=-0.15 sz=0.82 fogg=0.0"
./indra dome_final.bin 1024 1024 48 big_fog.f32 $V $C fog=0.5 fogn=24 fogonly=1 2> fog.log
./indra dome_final.bin 4096 4096 24 big_dome.f32 $V $C fog=0 2> dome.log
echo ALLDONE
