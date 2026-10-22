"""Verify the linear (in t) ternary families found by famsearch2.py:
   sum_i (A_i x + B_i + w_i t)^3 == alpha + 3 beta t  identically in x,t, all A_i != 0.
Writes families.json with the verified families sorted by modulus 3|beta|."""
import json, sympy as sp
x, t = sp.symbols('x t')
fams = json.load(open('fam_z10.json'))
out = []
for mod, res, H, Ap, B, w, al, be in fams:
    e = sp.expand(sum((Ap[i]*x + B[i] + w[i]*t)**3 for i in range(6)))
    assert e == al + 3*be*t, (e, al, be)
    assert all(a != 0 for a in Ap)
    out.append({'modulus': mod, 'residue': res, 'alpha': al, 'beta': be,
                'A': Ap, 'B': B, 'w': w, 'height_at_t0': H})
out.sort(key=lambda d: (d['modulus'], d['residue']))
json.dump(out, open('families.json', 'w'), indent=1)
for d in out[:8]:
    print(d['modulus'], d['residue'], 'A=', d['A'], 'B=', d['B'], 'w=', d['w'])
print(len(out), 'families verified')
