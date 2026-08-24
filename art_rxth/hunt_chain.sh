#!/bin/bash
# Atlas 44 chain: recovery scan then relay continuation.
cd /home/user/claude-mythos-self-play/art_rxth
echo "recovery scan [8.3e11, 8.8e11) start $(date -u)" >> hunt_chain_log.txt
./hunt44 830000000000 880000000000 >> hunt_chain_log.txt 2>&1
echo "recovery done $(date -u)" >> hunt_chain_log.txt
echo "continuation [8.8e11, 1.2e12) start $(date -u)" >> hunt_chain_log.txt
./hunt44 880000000000 1200000000000 >> hunt_chain_log.txt 2>&1
echo "ALLCHAINDONE $(date -u)" >> hunt_chain_log.txt
