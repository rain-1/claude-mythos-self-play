import sys; sys.path.insert(0,'.')
from scene import *; from neck import EX
S=Scene(); cmap={'A':'strawberry','B':'butter','C':'mint','D':'sky','E':'lilac'}
ring(S, EX[4], cmap, -26, 0, 1.0)
ring(S, EX[4].replace('A',''), cmap, 26, 0, 1.0)
S.save('p1.bin')
