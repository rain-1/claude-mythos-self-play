#!/bin/bash
set -e
cd /home/user/claude-mythos-self-play/art_euhx
sigmas=(-6.0 -3.0 -1.0 0.0 1.0 3.0 6.0)
for i in "${!sigmas[@]}"; do
  echo "=== launching shift $i sigma=${sigmas[$i]} ==="
  python3 anderson_shift.py "${sigmas[$i]}" "$i"
done
echo "ALL SHIFTS DONE"
