#!/bin/sh
cd /home/user/claude-mythos-self-play/art_lrjr/math_cover
python3 run_main.py 0.95 660 52 1 runs_R0.95.json > log_R095.txt 2>&1
python3 run_main.py 1.05 660 48 1 runs_R1.05.json > log_R105.txt 2>&1
