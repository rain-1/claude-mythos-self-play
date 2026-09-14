for m in 5 6; do OMP_NUM_THREADS=2 ./tripod $m 2 | tail -1; done
for m in 5 6 7 8; do OMP_NUM_THREADS=2 ./tripod $m 3 | tail -1; done
