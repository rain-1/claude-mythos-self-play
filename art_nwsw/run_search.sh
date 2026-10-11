#!/bin/bash
# one queue per argument group; usage: run_search.sh LOG BUDGET M1 M2 ...
LOG=$1; B=$2; shift 2
for M in "$@"; do /usr/bin/python3.13 -u search2.py $M 1e-3 $B; done > $LOG 2>&1
