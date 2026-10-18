#!/bin/bash
cd /home/user/claude-mythos-self-play/art_ervh/math_poly
export OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
for n in 13 15 17 19 21; do taskset -c 0 /usr/local/bin/python3 explore.py $n 45 runs/g$n.json; done
taskset -c 0 /usr/local/bin/python3 gallery.py
taskset -c 0 /usr/local/bin/python3 even.py 6 120 0.005 runs/even6.json
for n in 8 10 12; do taskset -c 0 /usr/local/bin/python3 even.py $n 200 0.005 runs/even$n.json; done
echo EVENDONE
