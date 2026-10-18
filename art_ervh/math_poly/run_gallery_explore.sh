#!/bin/bash
cd /home/user/claude-mythos-self-play/art_ervh/math_poly
export OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
for n in 3 5 7; do taskset -c 0 /usr/local/bin/python3 explore.py $n 40 runs/g$n.json; done
for n in 9 11 13 15; do taskset -c 0 /usr/local/bin/python3 explore.py $n 60 runs/g$n.json; done
for n in 17 19 21; do taskset -c 0 /usr/local/bin/python3 explore.py $n 90 runs/g$n.json; done
echo DONE
