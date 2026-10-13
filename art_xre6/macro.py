import sys, numpy as np; sys.path.insert(0,'.')
from scene import *; from neck import EX
import scene
for k in scene.GLASS: scene.GLASS[k]=tuple(0.6*v for v in scene.GLASS[k])
S=Scene(); cmap={'A':'strawberry','B':'butter','C':'mint','D':'sky','E':'lilac'}
N=EX[5]
R=ring(S, N, cmap, 0, 0, 1.0, gap=1.06, rot=float(sys.argv[1]) if len(sys.argv)>1 else 0)
S.save('macro.bin'); print(R)
