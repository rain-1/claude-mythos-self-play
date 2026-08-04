"""Run ./wheels k m, convert weighted counts to exact probabilities, verify sum=1."""
import subprocess, sys
from fractions import Fraction
from math import factorial

def qtable_c(k, m):
    out = subprocess.run(['./wheels', str(k), str(m)], capture_output=True, text=True)
    # denominator: sum over words weight*(k-1)! must equal C(k,m)/... : total pairs = ((k-1)!)^2
    # count_total * m!(k-m)!/k = (k-1)!^2  check
    res = {}
    for line in out.stdout.strip().split('\n'):
        tp, c = line.split(':')
        nu = tuple(int(x) for x in tp.strip().split(','))
        res[nu] = int(c)
    scale = Fraction(factorial(m)*factorial(k-m), k)
    tot = sum(res.values())*scale
    assert tot == Fraction(factorial(k-1))**2, (tot, k, m)
    return {nu: Fraction(c)*scale/Fraction(factorial(k-1))**2 for nu, c in sorted(res.items())}

if __name__ == '__main__':
    k, m = int(sys.argv[1]), int(sys.argv[2])
    for nu, q in qtable_c(k, m).items():
        print(k, m, ','.join(map(str,nu)), q)
