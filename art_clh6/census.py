"""Assemble the door census: first keys, all keys <= B, shut doors.
Compares against hzy's MO-comment claims and flags NEW openings
(doors with no key below 1e7 -- publicly 'no known factor' -- that
our scan to 1e10 opens)."""
import json, sys
sys.path.insert(0, '/home/user/claude-mythos-self-play/art_clh6')
SC = '/tmp/claude-0/-home-user-claude-mythos-self-play/df482f23-d1ae-562a-8002-f98face66e54/scratchpad/'

def load(path):
    out = []
    for line in open(path):
        s, p = line.split()
        out.append((int(s), int(p)))
    return out

hits = load(SC + 'smallp_hits.txt') + load(SC + 'full_hits.txt')
doors = {s: [] for s in range(-999, 1000, 2)}
for s, p in hits:
    if s % 2 != 0:              # even doors trivially open at p=2; census is odd-only
        doors[s].append(p)
for s in doors:
    doors[s] = sorted(set(doors[s]))

first = {s: (doors[s][0] if doors[s] else None) for s in doors}
shut = sorted([s for s in doors if not doors[s]], key=abs)
B = 10 ** 10

print("=== CENSUS: doors t+s, odd |s|<=999, primes <= 1e10 ===")
print("shut doors (no prime key <= 1e10):", len(shut))
print(shut)
print()
# hzy's MO-comment list: within +-100, no known factor below 1e7:
# +3, +21, +51, +93, -39, -87 ("...", list possibly incomplete)
hzy = [3, 21, 51, 93, -39, -87]
mine100_shut_at_1e7 = sorted([s for s in doors if abs(s) <= 100 and
                              (first[s] is None or first[s] > 10 ** 7)], key=abs)
print("doors |s|<=100 with no key <= 1e7 (hzy claimed ~6):", mine100_shut_at_1e7)
print("matches hzy's partial list?", set(hzy) <= set(mine100_shut_at_1e7))
new_open = {s: first[s] for s in mine100_shut_at_1e7 if first[s] is not None}
print("NEW OPENINGS (|s|<=100, publicly shut at 1e7, our key <= 1e10):", new_open)
print()
allnew = {s: first[s] for s in doors if first[s] is not None and first[s] > 10 ** 7}
print("all doors opened only above 1e7:", len(allnew))
for s, p in sorted(allnew.items(), key=lambda kv: -kv[1])[:20]:
    print(f"   s={s:+5d}  first key {p:,}")
print()
big = sorted(doors, key=lambda s: -(first[s] or 10 ** 18))
print("door +1 sealed by theorem: keys found =", doors[1], "(must be [])")
assert doors[1] == []
counts = {s: len(doors[s]) for s in doors}
import statistics
print("keys per door: mean %.2f max %d" % (statistics.mean(counts.values()), max(counts.values())))
json.dump({str(s): doors[s] for s in doors}, open(SC + 'census.json', 'w'))
print("wrote census.json")
