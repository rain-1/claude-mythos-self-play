exec(open('master.py').read().replace("if m > 6 or k == m: continue", "if m < 7 or m > 9 or k == m: continue"))
