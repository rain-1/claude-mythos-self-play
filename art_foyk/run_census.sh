#!/bin/bash
cd /home/user/claude-mythos-self-play/art_foyk
# small ones first (fast), 4-way parallel
joblist=()
for k in 7 8 9 10 11 12; do
  for m in $(seq 2 $k); do
    joblist+=("$k $m")
  done
done
printf '%s\n' "${joblist[@]}" | xargs -P 4 -I{} sh -c 'set -- {}; python3 wheels_wrap.py $1 $2 > qdata/q_$1_$2.txt 2>qdata/err_$1_$2.txt && echo done {}'
# the deep one
python3 wheels_wrap.py 13 3 > qdata/q_13_3.txt 2>qdata/err_13_3.txt && echo done 13 3
echo ALL DONE
