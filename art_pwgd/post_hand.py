import json
P = {}
def put(k, x, y, mirror=True):
    P[k] = [x, y]
    if mirror:
        tr = {'R0': 'R1', 'M0': 'M1', 'L0': 'L1', 'V': 'E', 'V0': 'E1', 'V1': 'E0', 'V2': 'E2', 'I0': 'I1'}
        inv = {v: k_ for k_, v in tr.items()}
        if k in tr: P[tr[k]] = [-x, y]
        elif k in inv: P[inv[k]] = [-x, y]
        elif k.startswith('S0'): P['S1' + k[2:]] = [-x, y]
        elif k.startswith('S1'): P['S0' + k[2:]] = [-x, y]
put('BF', 0, 10.0)
put('R1', 3.2, 8.9); put('M', 0, 8.7)
put('R2', 0, 7.75); put('M1', 1.9, 7.35); put('M2', 0, 6.5)
# right wing: S0 chains (below R1), k = 2, 3, then the limit
dx, dy = 1.05, -0.95
heads = {'S0': (4.9, 7.95), 'S02': (3.55, 6.95), 'S01': (4.55, 6.45), 'S00': (3.2, 5.55)}
for f, (x, y) in heads.items():
    put(f + '^2', x, y); put(f + '^3', x + dx, y + dy); put(f, x + dx * 2.55, y + dy * 2.55)
put('D', -0.95, 5.55, False); put('L', 0.95, 5.55, False)
put('D1', -0.75, 4.45, False); put('L3', 0.0, 4.6, False)
put('N', 1.25, 4.15, False); put('N2', 0.75, 3.05, False)
put('L1', 1.6, 3.2); put('L2', 0.0, 2.15, False)
put('D2', -0.55, 1.75, False)
put('V', 2.5, 4.35); put('V0', 2.05, 2.25); put('V1', 4.25, 2.6); put('V2', 3.25, 1.35)
put('I', 0.0, 1.25, False); put('I1', 1.1, 0.85); put('I2', 0, 0.0, False)
json.dump(P, open('post_layout_hand.json', 'w'))
print(len(P))
