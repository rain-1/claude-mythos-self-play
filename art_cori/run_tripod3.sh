for m in 5 6 7; do OMP_NUM_THREADS=1 ./tripod $m 3 | tail -1; done
