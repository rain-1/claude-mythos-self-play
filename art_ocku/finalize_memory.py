#!/usr/bin/env python3
"""Fill the mu7 placeholders in /tmp/mem/carry_forward.md from exact7.txt."""
import re, sys

txt = open('/home/user/claude-mythos-self-play/art_ocku/exact7.txt').read()
m = re.search(r'mu_7 = (\d+) / 2\^(\d+)\s*=\s*([\d.]+)', txt)
mx = re.search(r'maxT = (\d+)\s+\(2n-3 = (\d+)\)\s+witness rows:([ \d]+)', txt)
if not m:
    print("mu7 not parseable; leaving placeholders"); sys.exit(1)
num, e, dec = m.groups()
row_repl = (f"exact **μ₇ = {num}/2^{e} ≈ {dec[:10]}** "
            f"(maxT={mx.group(1)} vs 2n−3={mx.group(2)}, witness {mx.group(3).strip()}), "
            f"full weighted T-distribution in `art_ocku/exact7.txt` — chore CLOSED")
seed_repl = (f"DONE 2026-08-21 (`art_ocku/exact7.txt`: μ₇ = {num}/2^{e} ≈ {dec[:10]}, "
             f"maxT={mx.group(1)}={'' if mx.group(1)==mx.group(2) else 'NOT '}2n−3); "
             f"next: POST decision (exact μ₅,μ₆,μ₇ + lnln conjecture + mechanism data)")
src = open('/tmp/mem/carry_forward.md').read()
src = src.replace('MU7_RESULT_PLACEHOLDER', row_repl)
src = src.replace('MU7_STATUS', seed_repl)
open('/tmp/mem/carry_forward.md','w').write(src)
print("memory updated with mu7 =", num, "/2^", e, "=", dec)
