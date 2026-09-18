"""wanderers_cert.py — retrograde loops per planet 2000-2030 and their sizes vs the Sun's circle (2 AU across)."""
import numpy as np, json
from ephem import geo_path
cert = {}
for p in ['mercury', 'venus', 'mars', 'jupiter', 'saturn']:
    d = geo_path(p, 2000, 2031, 0.25)
    lon = np.unwrap(np.radians(d['lon'])); rate = np.diff(lon)
    retro = rate < 0
    starts = np.where(retro[1:] & ~retro[:-1])[0]; ends = np.where(~retro[1:] & retro[:-1])[0]
    ends = ends[ends > starts[0]]; n = min(len(starts), len(ends))
    x, y = d['x'], d['y']
    # loop size: for outer planets, the extent of the geocentric path over one synodic period, radially: max r - min r  ~ 2 AU
    r = np.hypot(x, y)
    cert[p] = dict(retrograde_episodes=int(len(starts)), mean_retro_days=round(float(np.mean((ends[:n] - starts[:n]) * 0.25)), 1),
                   r_min_au=round(float(r.min()), 3), r_max_au=round(float(r.max()), 3), r_span_au=round(float(r.max() - r.min()), 3))
cert['note'] = 'geocentric = heliocentric + (Sun as seen from Earth): every geocentric path is the heliocentric one with the Sun-circle (radius 1 AU) added at every moment, so each retrograde loop is a copy of the Sun-circle bent by the planet-s own slow drift. r_span over 30 years includes the planet-s eccentricity.'
json.dump(cert, open('cert_wanderers.json', 'w'), indent=1); print(json.dumps(cert, indent=1))
