#!/bin/bash
cd "$(dirname "$0")"
CEL=64 DIST=92 LY=0 FD=92 KPH=1.2e9 CMS=0.016 ./render.sh 4096 3072 40 tray.f32 && /usr/bin/python3 tone.py tray.f32 4096 3072 tray_raw.png && touch tray.done
