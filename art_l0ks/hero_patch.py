import re
src = open('hero_render.py').read()
src = src.replace("""    Rmin, Rmax = 0.085, 0.462
    GA = 2.39996322972865332
    base_amp = 2.1*rs**0.85""",
"""    Rmin, Rmax = 0.105, 0.462
    GA = 0.36
    base_amp = 1.15*rs**0.85""")
src = src.replace("""        segs, spts, L = geo[n]
        th0 = (n*GA) % (2*np.pi)""",
"""        segs, spts, L = geo[n]
        th0 = ((n-NMIN)*GA) % (2*np.pi)
        depth = (3.0/n)**0.35""")
src = src.replace("""        g_amp = base_amp*1.5/max(1, len(orbit))
        for osegs in orbit:
            draw_segs(ghost, osegs, cx, cy, rad, CYAN, g_amp)
        # gold representative
        rsegs = rot(segs, th0)
        draw_segs(gold, rsegs, cx, cy, rad, GOLD, base_amp*1.15)""",
"""        g_amp = base_amp*depth*0.55/max(1, len(orbit))
        for osegs in orbit:
            draw_segs(ghost, osegs, cx, cy, rad, CYAN, g_amp)
        # gold representative
        rsegs = rot(segs, th0)
        draw_segs(gold, rsegs, cx, cy, rad, GOLD, base_amp*depth)
        # the crack: for rim crowns, light the unchosen edge cold
        if n >= 6:
            ang0 = np.pi/2 + th0
            ang1 = 2*np.pi*(n-1)/n + np.pi/2 + th0
            p = np.array([math.cos(ang1), math.sin(ang1)])
            q = np.array([math.cos(ang0), math.sin(ang0)])
            A.polyline(ghost, np.array([to_px(p, cx, cy, rad), to_px(q, cx, cy, rad)]),
                       CYAN, amp=base_amp*depth*0.85)
            mid = 0.5*(p+q)
            A.star(ghost, cx+mid[0]*rad, cy+mid[1]*rad, CYAN,
                   amp=1.1*depth*rs*rs, rad=2.6*rs)""")
src = src.replace("""        for aa in ang:
            x, y = cx + math.cos(aa)*rad, cy + math.sin(aa)*rad
            A.star(gold, x, y, BEAD, amp=0.55*rs*rs, rad=1.6*rs)""",
"""        for aa in ang:
            x, y = cx + math.cos(aa)*rad, cy + math.sin(aa)*rad
            A.star(gold, x, y, BEAD, amp=0.30*depth*rs*rs, rad=1.4*rs)""")
src = src.replace("""    ghost_b = A.bloom(ghost, sigmas=(1.6*rs, 7*rs), weights=(0.9, 0.28))
    gold_b = A.bloom(gold, sigmas=(1.6*rs, 8*rs, 26*rs), weights=(1.0, 0.32, 0.14))
    buf = ghost_b*0.85 + gold_b
    img = A.tonemap(buf, k=1.25, gamma=0.92)""",
"""    ghost_b = A.bloom(ghost, sigmas=(1.6*rs, 7*rs), weights=(0.9, 0.30))
    gold_b = A.bloom(gold, sigmas=(1.6*rs, 8*rs, 26*rs), weights=(1.0, 0.30, 0.13))
    buf = ghost_b*0.9 + gold_b
    # warm fog in the inhabited middle
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    r2 = ((xx-cx)**2 + (yy-cy)**2)/(0.16*S)**2
    fog = np.exp(-r2*1.8)[..., None]*np.array([0.055, 0.038, 0.018], np.float32)
    buf = buf + fog
    img = A.tonemap(buf, k=1.55, gamma=0.94)""")
open('hero_render.py','w').write(src)
print("patched")
