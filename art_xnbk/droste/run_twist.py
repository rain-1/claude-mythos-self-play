import sys, json, numpy as np
from PIL import Image
from droste import twist
base = np.load(sys.argv[1]); cv = json.load(open(sys.argv[1] + '.json'))['canvas']
M = int(sys.argv[3]); V = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
out = twist(base, cv, M, zoom=V.get('zoom', 1.0), rot=V.get('rot', 0.0), ss=V.get('ss', 2), twist=V.get('twist', True), strands=V.get('strands', 1))
Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).save(sys.argv[2])
