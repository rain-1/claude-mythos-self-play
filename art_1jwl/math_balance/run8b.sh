#!/bin/sh
# k=8 certificates, n = 231..580: first every n not in the locked classes (fast), then the locked ones
for n in $(seq 231 580); do r=$((n % 8)); if [ $r -ne 3 ] && [ $r -ne 4 ]; then ./ss_red 8 $n $n 52 64 | cut -c1-40; fi; done
for n in $(seq 231 580); do r=$((n % 8)); if [ $r -eq 3 ] || [ $r -eq 4 ]; then ./ss_red 8 $n $n 56 64 | cut -c1-40; fi; done
