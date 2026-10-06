#!/bin/bash
# The Opened Pearl: the packing from outside, top cap sliced away, physical sun + sky on the polka-dot cloth
cd "$(dirname "$0")"
./indra opened.bin 2560 2560 20 big_opened.f32 ex=-4 ey=-7 ez=12 lx=0 ly=0 lz=3.3 fov=0.36 mtint=0.25 F0=0.32 nacre=0.75 glowk=0.15 kamb=0.6 sx=-0.3 sy=0.35 sz=0.88 ap=0.04 2> opened.log
echo ALLDONE
