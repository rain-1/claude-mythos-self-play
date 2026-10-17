#!/bin/bash
cd "$(dirname "$0")"
/usr/bin/python3 lake/lake.py --W 4096 --H 2560 --k0 9 --k1 20 --yf 0.46 --yn 0.87 --sf 0.10 --sn 0.44 --ratio 0.15 --out lake_raw.png && /usr/bin/python3 lake/caption.py --inp lake_raw.png --out every_other_island.png && touch lake.done
