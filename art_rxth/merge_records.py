"""Merge collatz census candidate files -> global record lists; verify vs b-file."""
import sys, glob

cands = {'F': [], 'S': []}
for f in sorted(glob.glob('run*_cand.txt')) + sorted(glob.glob('test1e9_cand.txt')):
    for line in open(f):
        t, n, v = line.split()
        cands[t].append((int(n), int(v)))
out = open('collatz_records.txt', 'w')
NMAX = 0
for t in 'FS':
    seen = sorted(set(cands[t]))
    best = 0; recs = []
    for n, v in seen:
        if v > best:
            best = v; recs.append((n, v))
    NMAX = max(NMAX, seen[-1][0] if seen else 0)
    print(f"{t}: {len(recs)} records (from {len(seen)} candidates)")
    for n, v in recs:
        out.write(f"{t} {n} {v}\n")
    if t == 'F':
        bf = [int(l.split()[1]) for l in open('b006877.txt') if l.strip() and not l.startswith('#')]
        # bound: our census is contiguous to the max chunk end; use 1e11 nominal
        B = 10**11
        bfle = [x for x in bf if x <= B]
        ours = [1] + [n for n, _ in recs if n <= B]
        ok = ours == bfle
        print(f"  vs A006877 b-file below 1e11: {'EXACT MATCH' if ok else 'MISMATCH'} ({len(bfle)} records)")
        if not ok:
            print('   b-file:', bfle[:80]); print('   ours  :', ours[:80])
    if t == 'S':
        fset = {n for n, _ in cands['F']}
        srec = [n for n, _ in recs]
        frec_all = []
        best2 = 0
        for n, v in sorted(set(cands['F'])):
            if v > best2: best2 = v; frec_all.append(n)
        same = srec == frec_all
        print(f"  shortcut record set == delay record set on census range: {same}")
        if not same:
            ss, fs_ = set(srec), set(frec_all)
            print('   S only:', sorted(ss-fs_)[:10]); print('   F only:', sorted(fs_-ss)[:10])
out.close()
print("wrote collatz_records.txt")
