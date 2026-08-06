"""Generate the iterated-downdate spectral flow for the render (MO 513954)."""
import numpy as np
from inertia_verify import cascade, inertia_eig

rng = np.random.default_rng(513954)
n = 120
npos, nneg, nzer = 66, 42, 12
Q, _ = np.linalg.qr(rng.normal(0, 1, (n, n)))
lam = np.concatenate([np.sort(rng.uniform(0.35, 3.2, npos))[::-1],
                      -np.sort(rng.uniform(0.35, 3.2, nneg))[::-1],
                      np.zeros(nzer)])
M0 = (Q * lam) @ Q.T

flow = []
hist, Mend = cascade(M0, rng, record_flow=flow, s_samples=61)
assert len(hist) == npos + nneg
assert np.abs(Mend).max() < 1e-7
signs = [h['i0'][0] - h['i1'][0] and (1 if h['Delta'] > 0 else -1) or (1 if h['Delta'] > 0 else -1)
         for h in hist]
signs = [1 if h['Delta'] > 0 else -1 for h in hist]
print("stages:", len(hist), " +deaths:", signs.count(1), " -deaths:", signs.count(-1))
print("inertia path:", [h['i0'] for h in hist[:5]], "...", hist[-1]['i1'])

# stack: (stage, s_samples, n) eigenvalues
E = np.array([evs for (_, _, evs) in flow])            # (S, 61, n)
inert = np.array([h['i0'] for h in hist] + [hist[-1]['i1']])
np.savez_compressed("cascade_flow.npz", E=E, signs=np.array(signs), inert=inert,
                    Delta=np.array([h['Delta'] for h in hist]))
print("saved cascade_flow.npz", E.shape)
