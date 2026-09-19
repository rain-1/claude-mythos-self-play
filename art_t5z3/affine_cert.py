"""affine_cert.py — transversality certificate for the dimension count (MO 515243 notes).

At a known two-piece affine dissection (regular pentagon, axis cut, m = 0; and the m = 2 zigzag), form the
residual map  R(Q, cut, φ) = (φ(v_i) − v'_{π(i)})_i ∈ ℝ^{2·nv}  over the polygon's own coordinates (2n),
the cut parameters and φ's six entries, and compute its Jacobian rank by finite differences.
Full rank 2·nv means the incidence variety is a smooth manifold of dimension (2n + cut + 6) − 2·nv = 2n + 4 − n
= n + 4 there, so its projection to the 2n-dimensional space of n-gons has measure zero for n ≥ 5:
generic pentagons near the regular one admit no dissection of that combinatorial type.
"""
import json
import numpy as np
import affine as af


def residual_vector(Qflat, cutparams, phi, spec):
    n = spec['n']; Q = Qflat.reshape(n, 2)
    pc, i, qc, j, m = spec['pc'], spec['i'], spec['qc'], spec['j'], spec['m']
    k = 0
    if pc:
        p = Q[i]
    else:
        p = Q[i] + (Q[(i + 1) % n] - Q[i]) * cutparams[k]; k += 1
    if qc:
        q = Q[j]
    else:
        q = Q[j] + (Q[(j + 1) % n] - Q[j]) * cutparams[k]; k += 1
    bps = cutparams[k:k + 2 * m].reshape(m, 2)
    P1, P2, _, _ = af.pieces(Q, p, i, q, j, bps, pc, qc)
    rev, r = spec['rev'], spec['r']
    P2r = P2[::-1] if rev else P2
    Y = np.roll(P2r, -r, axis=0)
    A = phi[:4].reshape(2, 2); b = phi[4:]
    return (P1 @ A.T + b - Y).ravel()


def jacobian_rank(Q, cutparams, phi, spec, h=1e-6):
    x0 = np.concatenate([Q.ravel(), cutparams, phi])
    nQ = Q.size; nc = len(cutparams)

    def f(x):
        return residual_vector(x[:nQ], x[nQ:nQ + nc], x[nQ + nc:], spec)
    r0 = f(x0)
    J = np.zeros((len(r0), len(x0)))
    for k in range(len(x0)):
        e = np.zeros(len(x0)); e[k] = h
        J[:, k] = (f(x0 + e) - f(x0 - e)) / (2 * h)
    s = np.linalg.svd(J, compute_uv=False)
    return len(r0), len(x0), s, float(np.abs(r0).max())


if __name__ == '__main__':
    out = {}
    d = json.load(open('cache/affine_search_part1.json'))
    for name in ('regular_pentagon', 'affine_regular_pentagon'):
        Q = np.array(d[name]['Q']); n = len(Q)
        for mkey, best in d[name]['best_by_m'].items():
            m = int(mkey)
            if best['residual'] > 1e-12 or m % 2:
                continue
            pc, i, qc, j = best['p_corner'], best['i'], best['q_corner'], best['j']
            p = np.array(best['p']); q = np.array(best['q']); bps = np.array(best['bps']).reshape(m, 2)
            # recover the cut parameters (edge fractions) from p, q
            cut = []
            if not pc:
                e = Q[(i + 1) % n] - Q[i]; cut.append(float((p - Q[i]) @ e / (e @ e)))
            if not qc:
                e = Q[(j + 1) % n] - Q[j]; cut.append(float((q - Q[j]) @ e / (e @ e)))
            cut = np.array(cut + list(bps.ravel()))
            corr = best['corr']
            phi = np.concatenate([np.array(corr['A']).ravel(), np.array(corr['b'])])
            spec = dict(n=n, pc=pc, i=i, qc=qc, j=j, m=m, rev=corr['rev'], r=corr['r'])
            neq, nunk, s, res = jacobian_rank(Q, cut, phi, spec)
            rank = int((s > 1e-7 * s[0]).sum())
            print(f'{name} m={m}: equations {neq}, unknowns {nunk} (polygon {2 * n} + cut {len(cut)} + map 6), '
                  f'residual {res:.1e}, Jacobian rank {rank}, smallest singular value {s[-1]:.3e} -> '
                  f'incidence dim {nunk - rank}, polygon space dim {2 * n}')
            out[f'{name}_m{m}'] = dict(equations=neq, unknowns=nunk, rank=rank, sv_min=float(s[-1]), sv_max=float(s[0]),
                                       residual=res, incidence_dim=nunk - rank, polygon_dim=2 * n)
    json.dump(out, open('cache/affine_cert.json', 'w'), indent=1)
