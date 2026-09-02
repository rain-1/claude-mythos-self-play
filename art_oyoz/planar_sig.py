"""planar_sig.py — MO 409058: the divisibility graph of the PROPER divisors of n
(vertices = divisors d of n with 1 < d < n? or 1 <= d < n?) — we test both readings
against the poster's list of non-planar n <= 1000 to fix the convention, then
classify planarity by prime-exponent signature (the graph depends only on the
multiset of exponents).
"""
import networkx as nx
from itertools import product
from sympy import factorint, divisors

NONPLANAR_1000 = set(map(int, """32, 36, 48, 60, 64, 72, 80, 84, 90, 96, 100, 108, 112, 120, 126, 128, 132, 140, 144, 150, 156, 160, 162, 168, 176, 180, 192, 196, 198, 200, 204, 208, 210, 216, 220, 224, 225, 228, 234, 240, 243, 252, 256, 260, 264, 270, 272, 276, 280, 288, 294, 300, 304, 306, 308, 312, 315, 320, 324, 330, 336, 340, 342, 348, 350, 352, 360, 364, 368, 372, 378, 380, 384, 390, 392, 396, 400, 405, 408, 414, 416, 420, 432, 440, 441, 444, 448, 450, 456, 460, 462, 464, 468, 476, 480, 484, 486, 490, 492, 495, 496, 500, 504, 510, 512, 516, 520, 522, 525, 528, 532, 540, 544, 546, 550, 552, 558, 560, 564, 567, 570, 572, 576, 580, 585, 588, 592, 594, 600, 608, 612, 616, 620, 624, 630, 636, 640, 644, 648, 650, 656, 660, 666, 672, 675, 676, 680, 684, 688, 690, 693, 696, 700, 702, 704, 708, 714, 720, 726, 728, 729, 732, 735, 736, 738, 740, 744, 748, 750, 752, 756, 760, 765, 768, 770, 774, 780, 784, 792, 798, 800, 804, 810, 812, 816, 819, 820, 825, 828, 832, 836, 840, 846, 848, 850, 852, 855, 858, 860, 864, 868, 870, 876, 880, 882, 884, 888, 891, 896, 900, 910, 912, 918, 920, 924, 928, 930, 936, 940, 944, 945, 948, 950, 952, 954, 960, 966, 968, 972, 975, 976, 980, 984, 988, 990, 992, 996, 1000""".replace('\n', ' ').split(', ')))

def divgraph(ds):
    G = nx.Graph()
    G.add_nodes_from(ds)
    for i, a in enumerate(ds):
        for b in ds[i + 1:]:
            if b % a == 0:
                G.add_edge(a, b)
    return G

def planar_n(n, include_one):
    ds = [d for d in divisors(n) if d < n and (include_one or d > 1)]
    return nx.check_planarity(divgraph(ds))[0]

if __name__ == '__main__':
    for inc in (True, False):
        bad = [n for n in range(2, 1001) if (not planar_n(n, inc)) != (n in NONPLANAR_1000)]
        print(f'include 1: {inc} -> mismatches vs poster list: {len(bad)} {bad[:10]}')
    # signature classification (with the convention that matched)
    inc = True
    # signature -> planar? using a representative with small primes
    primes = [2, 3, 5, 7, 11, 13]
    res = {}
    for k in range(1, 5):
        for exps in product(range(1, 6), repeat=k):
            if list(exps) != sorted(exps, reverse=True):
                continue
            n = 1
            for p, e in zip(primes, exps):
                n *= p ** e
            res[exps] = planar_n(n, inc)
    planar = sorted([s for s, v in res.items() if v], key=lambda s: (len(s), s))
    print('PLANAR signatures (exponent multisets, descending):', planar)
    # minimal non-planar (up-set generators)
    nonpl = [s for s, v in res.items() if not v]
    def leq(a, b):  # a <= b componentwise after padding
        if len(a) > len(b):
            return False
        return all(x <= y for x, y in zip(a, b))
    minimal = [s for s in nonpl if not any(t != s and leq(t, s) for t in nonpl)]
    print('MINIMAL non-planar signatures:', sorted(minimal, key=lambda s: (len(s), s)))
