for h in 22 27 30 31.3 32.2 33.2; do
  ./halo tmp/Z_$h 1000000000 $h "P:1:0.22:0.5" 0 89.999 1200 1200 1.75 512 $RANDOM > tmp/Z_$h.log 2>&1
done
