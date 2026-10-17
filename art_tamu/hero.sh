#!/bin/bash
# 4096^2 hero: Twelve Petals, Then Fifty-Three
cd "$(dirname "$0")"
/usr/bin/python3 carnation/medallion.py --S 4096 --octs 10,12,14,16,18,20,22,24,26,28,30,31 --coral 24 --rin 0.18 --rout 0.67 --A 0.048 --Qa 24 --pleat 0.18 --mix 0.12 --light 0.08 --cy 0.12 --npy hero.npy --out hero_raw.png
/usr/bin/python3 carnation/finish.py --npy hero.npy --cy 0.12 --rnames 0.79 --out twelve_petals_then_fifty_three.png
touch hero.done
