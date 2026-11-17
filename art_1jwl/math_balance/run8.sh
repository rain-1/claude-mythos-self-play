#!/bin/sh
# success certificates for k=8 beyond the proved failures
for n in $(seq 69 580); do
  r=$((n % 8))
  if [ $r -eq 3 ] || [ $r -eq 4 ]; then
    if [ $n -le 200 ]; then p=$(( (n*(n+1)/2) % 2 )); ./lock 8 $n $p 200000 | tail -1; else ./ss_red 8 $n $n 52 64 | cut -c1-40; fi
  else ./ss_red 8 $n $n 52 64 | cut -c1-40; fi
done
