"""Conway nimber arithmetic engine.

Nim-addition  a (+) b  = a XOR b.
Nim-multiplication (x) defined by the mex genesis
    a (x) b = mex { a'(x)b  XOR  a(x)b'  XOR  a'(x)b'  :  a'<a, b'<b }
On nimbers < 2^(2^k) this is the finite field GF(2^(2^k)).

We build the 256x256 small table STRAIGHT FROM THE MEX DEFINITION
(no field shortcuts) so it is a ground-truth certificate, then use the
Fermat-power decomposition for fast vectorized big products:
  For F a Fermat 2-power (2,4,16,256,65536):
    x (x) F     = x*F            for x < F      ("F is a new symbol")
    F (x) F     = 3F/2 = F XOR F/2
  Writing i = a*F+b, j = c*F+d  (a,b,c,d < F, F=256):
    i(x)j = (a(x)c)(x)(F XOR F/2)  XOR  (a(x)d XOR b(x)c)(x)F  XOR  b(x)d
          = [(a(x)c) (x) F]  XOR  [(a(x)c)(x)(F/2)]  XOR ...
    with (z)(x)F = z*F for z<F.
"""
import numpy as np, time

F = 256

def build_small_table_mex(n=F):
    """n x n nim-multiplication table from the raw mex definition. O(n^4)-ish but n=256 ok in numpy."""
    T = np.zeros((n, n), dtype=np.int64)
    for a in range(1, n):
        Ta = T[:a]          # rows a' < a  (each full length n)
        for b in range(1, n):
            # excluded set: T[a',b] ^ T[a,b'] ^ T[a',b'] over a'<a, b'<b
            ex = Ta[:, b][:, None] ^ T[a, :b][None, :] ^ Ta[:, :b]
            seen = np.zeros(ex.size + 1, dtype=bool)
            vals = ex[ex <= ex.size]
            seen[vals] = True
            T[a, b] = np.argmin(seen)   # mex = first False
    return T

t0 = time.time()
try:
    T = np.load('small_table.npy')
    print('loaded cached small table')
except FileNotFoundError:
    T = build_small_table_mex()
    np.save('small_table.npy', T)
    print(f'built 256x256 mex table in {time.time()-t0:.1f}s')

# ---- fast vectorized product for arrays of nimbers < 65536 ----
Tsmall = T.astype(np.int32)

def nmul(i, j):
    """vectorized nim-multiplication of int arrays with values < 65536."""
    i = np.asarray(i, dtype=np.int32); j = np.asarray(j, dtype=np.int32)
    a, b = i >> 8, i & 255
    c, d = j >> 8, j & 255
    ac = Tsmall[a, c]
    cross = Tsmall[a, d] ^ Tsmall[b, c]
    # (ac)(x)(256 XOR 128): ac<256 so ac(x)256 = ac*256; ac(x)128 via small table
    return (ac << 8) ^ Tsmall[ac, 128] ^ (cross << 8) ^ Tsmall[b, d]

if __name__ == '__main__':
    rng = np.random.default_rng(1)
    # --- verification battery ---
    # 1. known Fermat-square values  F(x)F = 3F/2
    for k, Fk in enumerate([2, 4, 16, 256]):
        v = int(nmul(Fk, Fk))
        assert v == 3 * Fk // 2, (Fk, v)
    print('Fermat rule F(x)F=3F/2: OK for F=2,4,16,256')
    # 2. small-table row spot checks vs OEIS A051775 (nim-mult table read by antidiagonals)
    known_row2 = [0,2,3,1,8,10,11,9,12,14,15,13,4,6,7,5]   # 2 (x) n for n=0..15
    assert [int(nmul(2, n)) for n in range(16)] == known_row2
    known_row3 = [0,3,1,2,12,15,13,14,4,7,5,6,8,11,9,10]
    assert [int(nmul(3, n)) for n in range(16)] == known_row3
    print('rows 2,3 match known nim-multiplication values: OK')
    # 3. Latin square property on the full small table (rows & cols are permutations of 0..255 when restricted? 
    #    actually row a of GF(256)-closed part: {a(x)b : b<256} = 0..255 iff a<256 nonzero}
    for a in [1, 2, 37, 100, 255]:
        row = nmul(np.full(256, a), np.arange(256))
        assert sorted(row.tolist()) == list(range(256))
    print('Latin-square rows (bijectivity of x -> a(x)x in GF(256)): OK')
    # 4. field axioms, random: associativity + distributivity in GF(2^16)
    x, y, z = (rng.integers(0, 65536, 20000, dtype=np.int32) for _ in range(3))
    assert np.array_equal(nmul(nmul(x, y), z), nmul(x, nmul(y, z)))
    assert np.array_equal(nmul(x, y ^ z), nmul(x, y) ^ nmul(x, z))
    assert np.array_equal(nmul(x, y), nmul(y, x))
    print('associativity, distributivity, commutativity (20000 random triples): OK')
    # 5. closure: GF(2^2^k) closed under (x)
    for Fk in [2, 4, 16, 256]:
        g = np.arange(Fk)
        prod = nmul(g[:, None], g[None, :])
        assert prod.max() < Fk
    print('subfield closure GF(2),GF(4),GF(16),GF(256): OK')
    # 6. multiplicative group of GF(2^16) is cyclic of order 65535; find a generator
    def order(a):
        o, p = 1, int(nmul(a, a) if False else a)
        p = a
        seen = 1
        # fast: use exponentiation by squaring with factored 65535 = 3*5*17*257
        return None
    def npow(a, e):
        r, base = 1, int(a)
        while e:
            if e & 1: r = int(nmul(r, base))
            base = int(nmul(base, base))
            e >>= 1
        return r
    fac = [3, 5, 17, 257]
    def is_generator(a):
        if npow(a, 65535) != 1: return False
        return all(npow(a, 65535 // p) != 1 for p in fac)
    g = next(a for a in range(256, 600) if is_generator(a))
    print(f'generator of GF(2^16)*: g = {g}')
    # 7. build dlog table
    dlog = np.full(65536, -1, dtype=np.int64)
    p = 1
    for k in range(65535):
        assert dlog[p] == -1
        dlog[p] = k
        p = int(nmul(p, g))
    assert p == 1 and (dlog[1:] >= 0).all()
    np.save('dlog.npy', dlog); np.save('gen.npy', np.array([g]))
    print('dlog table: every nonzero nimber = g^k uniquely, k in 0..65534: OK')
    # 8. THE JEWEL FACT: subfield GF(2^2^k) = integers < 2^2^k  = subgroup of index (65535/(2^2^k-1))
    for Fk, m in [(4, 3), (16, 15), (256, 255)]:
        idx = np.where(dlog % (65535 // m) == 0)[0]
        elems = np.sort(np.concatenate([idx]))
        assert np.array_equal(elems, np.arange(1, Fk)), (Fk, elems[:20])
    print('JEWEL: order-m subgroup of dlog multiples == exactly the integers 1..2^2^k-1, for m=3,15,255: OK')
    print(f'total {time.time()-t0:.1f}s')
