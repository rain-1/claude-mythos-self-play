#!/bin/bash
set -e
cd /home/user/claude-mythos-self-play/art_gy5v
lcm() { python3 -c "from math import lcm; print(lcm(*range(1,$1+1)))"; }
for n in 9 12 14 16 18 20 22 24; do
  L=$(lcm $n)
  SPAN=$L
  if [ "$L" -gt 300000000 ]; then SPAN=300000000; fi
  ./knap $L $n shore/rle_$n.txt $SPAN > shore/res_$n.txt 2>/dev/null
  cat shore/res_$n.txt
done
for n in 21 23 25 26 27 28; do
  L=$(lcm $n)
  ./knap $L $n > shore/res_$n.txt 2>/dev/null
  cat shore/res_$n.txt
done
echo ALLDONE
