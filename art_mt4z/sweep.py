"""d-sweep certificates for MO 513737: on random smooth floors (h=0 at the
shore), count level-tripod solution curves and isolated level-square rests
as the table side d varies.  Key questions: does a level equilateral triangle
exist for EVERY d (empirically: are there always curves)?  do level squares
ever fail to exist?"""
import json, time
import numpy as np
import table_lib as tl

results = {}
for seed in [42, 7, 23]:
    T = tl.make_terrain(seed=seed)
    for d in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]:
        t0 = time.time()
        Rc = d / np.sqrt(3)
        cmax = 1.0 - Rc
        if cmax <= 0.03:
            continue
        cx, cy, th, k = tl.tri_curve_points(T, d, ngrid=170, ntheta=200)
        seeds_arr = np.stack([cx, cy, th], axis=1)
        comps = tl.trace_tri_curves(T, d, seeds_arr, cmax, step=0.005)
        ntri = len(comps)
        nclosed = sum(1 for c in comps if c['closed'])
        scx, scy, sth, sk = tl.sq_level_points(T, d, ngrid=110, ntheta=144)
        nsq = len(scx)
        results[f's{seed}_d{d:.1f}'] = dict(seed=seed, d=d, tri_components=ntri,
                                            tri_closed=nclosed, tri_seeds=len(cx),
                                            level_squares=nsq,
                                            sq_heights=[float(x) for x in sk])
        print(f'seed {seed} d={d:.1f}: tri curves {ntri} ({nclosed} closed, '
              f'{len(cx)} seeds), level squares {nsq}   [{time.time()-t0:.0f}s]',
              flush=True)
json.dump(results, open('sweep_results.json', 'w'), indent=1)
print('saved sweep_results.json')
