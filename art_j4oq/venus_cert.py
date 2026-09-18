"""venus_cert.py — certificates for HESPERUS IS PHOSPHORUS: transits, the 8-year drift of the pentagram,
greatest elongations, and the speed ratio that makes the inner loops dark."""
import numpy as np, json
from ephem import geo_path, ts
d = geo_path('venus', 1900, 2053, 0.5)
yr = 2000.0 + (d['t'] - 2451545.0) / 365.25
x, y, z = d['x'], d['y'], d['z']; sx, sy, sz = d['sx'], d['sy'], d['sz']
r = np.sqrt(x*x + y*y + z*z); rsun = np.sqrt(sx*sx + sy*sy + sz*sz)
sep = np.degrees(np.arccos(np.clip((x*sx + y*sy + z*sz) / (r * rsun), -1, 1)))
cert = {}
# inferior conjunctions: local minima of sep with r < 0.5
inf = [i for i in range(1, len(sep) - 1) if sep[i] < sep[i-1] and sep[i] <= sep[i+1] and r[i] < 0.5]
# refine each with a fine ephemeris (2-minute steps over +-1 day)
from skyfield.api import load
from skyfield.framelib import ecliptic_J2000_frame
eph = load('cache/de421.bsp'); earth = eph['earth']
rows = []
for i in inf:
    t0 = d['t'][i]
    tt = ts.tt_jd(t0 + np.linspace(-1, 1, 1441))
    e = earth.at(tt)
    pv = e.observe(eph['venus']).frame_xyz(ecliptic_J2000_frame).au; ps = e.observe(eph['sun']).frame_xyz(ecliptic_J2000_frame).au
    s_ = np.degrees(np.arccos(np.sum(pv * ps, 0) / (np.linalg.norm(pv, axis=0) * np.linalg.norm(ps, axis=0))))
    k = int(np.argmin(s_))
    lon = np.degrees(np.arctan2(pv[1, k], pv[0, k])) % 360
    rows.append(dict(date=tt[k].utc_iso()[:16], min_sep_deg=round(float(s_[k]), 4), transit=bool(s_[k] < 0.2667), geocentric_lon_deg=round(float(lon), 3), dist_au=round(float(np.linalg.norm(pv[:, k])), 4)))
cert['inferior_conjunctions'] = rows
cert['transits'] = [r_['date'] for r_ in rows if r_['transit']]
# drift of the pentagram: longitude of inferior conjunction n vs n+5 (one 8-year cycle later)
lons = np.array([r_['geocentric_lon_deg'] for r_ in rows]); dates = np.array([float(ts.utc(int(r_['date'][:4]), int(r_['date'][5:7]), int(r_['date'][8:10])).tt) for r_ in rows])
dl = ((lons[5:] - lons[:-5] + 180) % 360) - 180
dtt = dates[5:] - dates[:-5]
cert['cycle_drift_deg_per_8yr'] = dict(mean=round(float(dl.mean()), 3), std=round(float(dl.std()), 3), n=int(len(dl)))
cert['five_synodic_days'] = dict(mean=round(float(dtt.mean()), 2), eight_years=2921.94)
cert['full_turn_years'] = round(float(360 / abs(dl.mean()) * 8), 1)
# elongation extremes
el = (d['lon'] - d['slon'] + 180) % 360 - 180
cert['greatest_elongation_deg'] = dict(east_max=round(float(el.max()), 2), west_max=round(float(-el.min()), 2))
# geocentric speed at inferior vs superior conjunction (AU/day)
v = np.hypot(np.diff(x), np.diff(y)) / 0.5
cert['geocentric_speed_au_per_day'] = dict(min=round(float(v.min()), 5), max=round(float(v.max()), 5), ratio=round(float(v.max() / v.min()), 2))
cert['apparent_diameter_ratio'] = round(float(r.max() / r.min()), 2)
json.dump(cert, open('cert_venus.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in cert.items() if k != 'inferior_conjunctions'}, indent=1))
print(len(rows), 'inferior conjunctions; transits', cert['transits'])
