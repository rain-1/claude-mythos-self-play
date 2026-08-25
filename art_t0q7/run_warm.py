import json, sys
from cloth_anneal import anneal_warm
which = sys.argv[1]
if which == "256b":
    d = json.load(open("cloth_anneal_256_3_rev.json"))
    anneal_warm(256, 60000, 768, 11, d["sigma"], "256b")
elif which == "512":
    import numpy as np
    n = 512
    anneal_warm(n, 60000, 640, 12, list(range(n-1, -1, -1)), "512")
