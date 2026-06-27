#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "=== 03 dilogarithm (2048) ==="
python3 p03_dilog.py 2048 2
echo "=== 02 bing house (2048) ==="
CAMX=1.25 CAMY=1.12 CAMZ=2.95 python3 p02_bing.py 2048 2 0.56
echo "=== 01 braid centerpiece (4096) ==="
BODY_FLOOR=0.32 python3 p01_braid.py 4096 20 12 2
echo "=== ALL FINALS DONE ==="
