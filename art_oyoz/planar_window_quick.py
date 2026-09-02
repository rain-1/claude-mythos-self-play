"""window-only rerun (no certificate) so the chart can be drawn while the 1e12 certificate finishes."""
import numpy as np, json
from planar_window import window_sigs, planar_flags
from planar_race import count_planar
A, W = 26_800_000, 200_000
om, em, e2 = window_sigs(A, W); fl = planar_flags(om, em, e2)
P = count_planar(A - 1)[0] + np.cumsum(fl.astype(np.int64)); Ns = np.arange(A, A + W, dtype=np.int64); D = 2 * P - Ns
assert D[0] > 0
first_neg = int(Ns[np.argmax(D < 0)]); first_tie = int(Ns[np.argmax(D <= 0)])
sgn = np.sign(D); nz = sgn != 0; s_nz = sgn[nz]; N_nz = Ns[nz]
ch = np.nonzero(s_nz[1:] != s_nz[:-1])[0]; changes = [(int(N_nz[i + 1]), int(s_nz[i + 1])) for i in ch]
last = int(Ns[np.nonzero(D > 0)[0][-1]])
around = (Ns >= first_neg - 2000) & (Ns <= first_neg + 2000)
json.dump(dict(first_tie=first_tie, first_neg=first_neg, changes=changes, last_planar_lead_in_window=last,
               zoom_N=Ns[around].tolist(), zoom_D=D[around].tolist(), certified_to=None), open('planar_window.json', 'w'))
print(first_tie, first_neg, last, len(changes), 'D at', A + W - 1, int(D[-1]))
