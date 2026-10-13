#!/bin/bash
./beads2 flower.bin 4096 4096 128 flower_4096.f32 dist=200 fov=23 cel=64 caz=-90 ly=-3 sunel=22 sunaz=105 sunrad=1.0 nph=1.2e9 cmarg=25 cmn=8192 pr=0.99 pg=0.975 pb=0.95 zr=0.78 zg=0.82 zb=0.96 > flower.log 2>&1
./beads2 pairs.bin 3200 3200 128 pairs_3200.f32 dist=150 fov=21.5 cel=68 caz=-90 ly=-1.2 sunel=24 sunaz=110 sunrad=1.1 nph=8e8 cmarg=20 cmn=8192 pr=0.99 pg=0.975 pb=0.95 zr=0.78 zg=0.82 zb=0.96 > pairs.log 2>&1
./beads2 hero.bin 4096 4096 128 hero2_4096.f32 dist=150 fov=23.5 cel=66 caz=-90 ly=-1.6 sunel=24 sunaz=110 sunrad=1.1 nph=1.2e9 cmarg=20 cmn=8192 pr=0.99 pg=0.975 pb=0.95 zr=0.78 zg=0.82 zb=0.96 > hero2.log 2>&1
echo done > chain.done
