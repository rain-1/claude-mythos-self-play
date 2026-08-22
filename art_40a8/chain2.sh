#!/bin/bash
cd /home/user/claude-mythos-self-play/art_40a8
echo "CHAIN2: nhunt 51 24000 start $(date +%T)"
nice -n 5 ./nhunt 51 24000 64 > nhunt51_T24000.txt 2> nhunt51_T24000.err
echo "CHAIN2: nhuntw 17 60000 start $(date +%T)"
nice -n 5 ./nhuntw 17 60000 128 > nhunt17_T60000.txt 2> nhunt17_T60000.err
echo "CHAIN2_ALL_DONE $(date +%T)"
