# exact min |±1^k ± ... ± n^k| by big-int bitset DP (Python ints as bitsets)
import sys
def mins(k, nmax):
    R = 1  # bit m set <=> m is a subset sum of {1^k..n^k}
    T = 0
    out = []
    for n in range(1, nmax+1):
        w = n**k
        R |= R << w
        T += w
        # closest subset sum to T/2 from below: signed sum = T-2m
        h = T//2
        low = R & ((1 << (h+1)) - 1)
        m = low.bit_length() - 1
        out.append(T - 2*m)
    return out
if __name__ == "__main__":
    k = int(sys.argv[1]); nmax = int(sys.argv[2])
    v = mins(k, nmax)
    par = [(n*(n+1)//2) % 2 for n in range(1, nmax+1)]
    print("k=%d" % k, v)
    bad = [n for n in range(1, nmax+1) if v[n-1] != par[n-1]]
    print(" failures:", bad)
