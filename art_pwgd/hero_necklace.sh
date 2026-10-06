#!/bin/bash
cd "$(dirname "$0")"
S="scene=necklace nx=3.9 sx=0 sy=0.9744 sz=0.225 ex=0 ey=-10 ez=4.6 lx=0 ly=-0.8 lz=0.4 fov=0.42 pat=dots gk=0.8 ksun=0.95 kamb=0.30 rbk=0.9 dens=0.5 ap=0.07 focus=8.5"
python3 render_marbles.py 4096 4096 big/npm.png $S pmy=2100 pmx=2700 nph=4000000 pb=16 pmsig=1.4 pmsave=big/npm.npy > big/npm.log 2>&1
for k in 0 1 2; do
  r0=$((k*1366)); r1=$(( (k+1)*1366 )); [ $k = 2 ] && r1=4096
  python3 render_marbles.py 4096 4096 big/nstrip$k.png $S pmy=2100 pmx=2700 pmload=big/npm.npy passes=24 r0=$r0 r1=$r1 > big/nstrip$k.log 2>&1 &
done
wait
python3 -c "
import numpy as np
np.save('big/neck_lin.npy', np.concatenate([np.load(f'big/nstrip{k}_lin.npy') for k in range(3)],0)); print('stitched')"
echo ALLDONE
