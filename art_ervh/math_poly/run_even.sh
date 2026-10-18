#!/bin/bash
cd /home/user/claude-mythos-self-play/art_ervh/math_poly
export OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
while ! grep -q DONE runs/gallery_explore.log; do sleep 5; done
taskset -c 0 /usr/local/bin/python3 explore.py 3 30 runs/g3.json
taskset -c 0 /usr/local/bin/python3 gallery.py
taskset -c 0 /usr/local/bin/python3 even.py 4 90 0.005 runs/even4.json
taskset -c 0 /usr/local/bin/python3 even.py 6 240 0.005 runs/even6.json
for n in 8 10 12; do taskset -c 0 /usr/local/bin/python3 even.py $n 400 0.005 runs/even$n.json; done
echo EVENDONE
