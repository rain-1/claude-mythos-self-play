#!/bin/bash
cd /home/user/claude-mythos-self-play/art_l0ks
echo "HUNT_CHAIN start $(date +%T)"
nice -n 10 ./hunt25 400000000000 560000000000 > hc1.out 2> hc1.err
echo "HUNT_CHUNK1_DONE $(date +%T)"
nice -n 10 ./hunt25 560000000000 720000000000 > hc2.out 2> hc2.err
echo "HUNT_CHUNK2_DONE $(date +%T)"
nice -n 10 ./hunt25 720000000000 880000000000 > hc3.out 2> hc3.err
echo "HUNT_CHAIN_ALL_DONE $(date +%T)"
