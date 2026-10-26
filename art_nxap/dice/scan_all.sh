for e in 0.3 0.5 0.7; do
python3 fairscan.py 3 30000 $e 0.4 15 0.5 1.3 9
python3 fairscan.py 5 30000 $e 0.4 15 1.3 1.9 7
python3 fairscan.py 7 30000 $e 0.4 15 1.4 2.4 6
python3 fairscan.py 9 30000 $e 0.4 15 1.5 2.7 7
python3 fairscan.py 11 30000 $e 0.4 15 1.6 3.0 8
done
