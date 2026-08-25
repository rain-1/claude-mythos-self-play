import json
from cloth_anneal import anneal_warm
d = json.load(open("cloth_anneal_512.json"))
anneal_warm(512, 70000, 704, 21, d["sigma"], "512b")
