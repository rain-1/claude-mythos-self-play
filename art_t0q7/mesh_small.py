#!/usr/bin/env python3
"""MO 514559 mesh game: t(x,y,z), move = remove >=1 from exactly two piles.

Grundy g(x,y,z) = mex over three quadrant sets:
  {g(x',y',z): x'<x, y'<y} u {g(x',y,z'): x'<x, z'<z} u {g(x,y',z'): y'<y, z'<z}

Prefix-OR bitsets (python ints), processed by total sum. N^3 states.
"""
import numpy as np, sys, time

def solve(N):
    g = np.zeros((N, N, N), np.int16)
    # Qz[z][x][y] = OR of bits g(x',y',z) for x'<x,y'<y ; likewise Qy (fixed y: vary x,z), Qx
    Qz = [[[0]*N for _ in range(N)] for _ in range(N)]  # [z][x][y]
    Qy = [[[0]*N for _ in range(N)] for _ in range(N)]  # [y][x][z]
    Qx = [[[0]*N for _ in range(N)] for _ in range(N)]  # [x][y][z]
    t0 = time.time()
    for s in range(0, 3*N-2):
        for x in range(max(0, s-2*N+2), min(N, s+1)):
            for y in range(max(0, s-x-N+1), min(N, s-x+1)):
                z = s-x-y
                if z < 0 or z >= N: continue
                # update prefix tables for this (x,y,z)
                if x >= 1 and y >= 1:
                    Qz[z][x][y] = Qz[z][x-1][y] | Qz[z][x][y-1] | (1 << int(g[x-1, y-1, z]))
                if x >= 1 and z >= 1:
                    Qy[y][x][z] = Qy[y][x-1][z] | Qy[y][x][z-1] | (1 << int(g[x-1, y, z-1]))
                if y >= 1 and z >= 1:
                    Qx[x][y][z] = Qx[x][y-1][z] | Qx[x][y][z-1] | (1 << int(g[x, y-1, z-1]))
                m = Qz[z][x][y] | Qy[y][x][z] | Qx[x][y][z]
                g[x, y, z] = ((m+1) & ~m).bit_length() - 1
    print(f"N={N} solved in {time.time()-t0:.1f}s, max g = {g.max()}", file=sys.stderr)
    return g

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    g = solve(N)
    np.save(f"mesh_g_{N}.npy", g)
    # sanity: t(x,y,0) should be min(x,y)
    xy = np.minimum.outer(np.arange(N), np.arange(N))
    print("t(x,y,0)==min(x,y):", np.array_equal(g[:, :, 0], xy))
    # symmetry check
    print("symmetric:", np.array_equal(g, g.transpose(1,0,2)) and np.array_equal(g, g.transpose(2,1,0)))
    # print the z=9 slice like the poster's table (x,y = 0..24)
    K = min(N, 25)
    print("t(x,y,9):")
    for x in range(K):
        print(" ".join(f"{g[x,y,9]:3d}" for y in range(K)))
