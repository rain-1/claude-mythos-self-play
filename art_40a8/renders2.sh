#!/bin/bash
cd /home/user/claude-mythos-self-play/art_40a8
nice -n 8 python3 hero_render.py final > hero_final.log 2>&1
echo "HERO_FINAL_DONE"
nice -n 8 python3 piece3_render.py final > piece3_final.log 2>&1
echo "PIECE3_FINAL_DONE"
