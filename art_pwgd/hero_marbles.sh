#!/bin/bash
# 4096² hero: photon map once, then 3 strips in parallel, then stitch.
cd "$(dirname "$0")"
S="ex=-1 ey=-10 ez=5.5 b2=2.2,0.9 b0=-2.4,0.6 b1=0.1,-1.5 lx=0.0 ly=0.0 lz=0.8 fov=0.33 sx=-0.1752 sy=0.9691 sz=0.1736 ap=0.10 focus=10.4 dens=1.0 ksun=0.95 kamb=0.30 pat=dots gk=0.8"
python3 render_marbles.py 4096 4096 big/pm.png $S pmy=2100 pmx=2700 nph=4000000 pb=24 pmsig=1.4 pmsave=big/pm.npy > big/pm.log 2>&1
for k in 0 1 2; do
  r0=$((k*1366)); r1=$(( (k+1)*1366 )); [ $k = 2 ] && r1=4096
  python3 render_marbles.py 4096 4096 big/strip$k.png $S pmy=2100 pmx=2700 pmload=big/pm.npy passes=24 r0=$r0 r1=$r1 > big/strip$k.log 2>&1 &
done
wait
python3 -c "
import numpy as np
a=[np.load(f'big/strip{k}_lin.npy') for k in range(3)]
np.save('big/hero_lin.npy', np.concatenate(a,0))
print('stitched')"
echo ALLDONE
