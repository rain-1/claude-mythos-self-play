for spec in "R:1:1.2:0" "P:1:0.22:0.8" "C:1:1.6:0.8" "Y:1:1.6:0.6"; do
  t=${spec:0:1}
  ./halo tmp/S_$t 700000000 22 "$spec" 0 89.999 1400 1400 0.47 1024 $RANDOM > tmp/S_$t.log 2>&1
done
