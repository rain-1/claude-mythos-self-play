#!/bin/bash
cd /home/user/claude-mythos-self-play/art_331l/math_paths
(nauty-geng -cq 10 0/2 | ./fpaths > census_n10_0.txt 2> log10_0.txt) &
(nauty-geng -cq 10 1/2 | ./fpaths > census_n10_1.txt 2> log10_1.txt) &
wait
