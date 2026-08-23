import numpy as np, math
from steiner import census, enum_all_full
c = census(8)
fe = enum_all_full(c['V'])
print(f"n=8: DP={c['len']:.10f} rim={c['rim']:.10f} full-enum={fe:.10f}")
