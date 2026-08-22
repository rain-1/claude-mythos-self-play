#!/bin/bash
# Sequential deep hunts on one core, after nhunt17 T=32000 finishes.
cd /home/user/claude-mythos-self-play/art_40a8
while pgrep -x nhunt >/dev/null; do sleep 10; done
echo "CHAIN: famhunt 200000 start $(date +%T)"
nice -n 5 ./famhunt 200000 > famhunt_200000.txt 2> famhunt_200000.err
echo "CHAIN: nhuntw 51 40000 start $(date +%T)"
nice -n 5 ./nhuntw 51 40000 96 > nhunt51_T40000.txt 2> nhunt51_T40000.err
echo "CHAIN: nhuntw 17 60000 start $(date +%T)"
nice -n 5 ./nhuntw 17 60000 128 > nhunt17_T60000.txt 2> nhunt17_T60000.err
echo "CHAIN_ALL_DONE $(date +%T)"
