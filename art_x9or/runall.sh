#!/bin/bash
cd /home/user/claude-mythos-self-play/art_x9or
OMP_NUM_THREADS=4 /usr/bin/python3.13 hero.py 4096 > hero.log 2>&1
OMP_NUM_THREADS=4 /usr/bin/python3.13 sheet.py 1000 > sheet.log 2>&1
