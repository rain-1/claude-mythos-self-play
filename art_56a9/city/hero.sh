for k in 0 1 2 3 4 5 6 7; do
  y0=$((k*512)); y1=$((y0+512))
  [ -f hero_$k.npy ] || python3 scene.py hero.json hero_$k.npy $y0 $y1
  echo strip $k done $(date +%T)
done
