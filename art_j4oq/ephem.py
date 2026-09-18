"""ephem.py — geocentric planet paths from JPL DE421 (skyfield), ecliptic J2000 frame.
Caches cache/geo_<planet>_<y0>_<y1>.npz with daily-or-finer samples:
  t (JD), x,y,z geocentric ecliptic AU of the planet, sx,sy,sz of the Sun, lon_p, lon_s (deg)."""
import numpy as np, os, sys
from skyfield.api import load
from skyfield.framelib import ecliptic_J2000_frame

ts = load.timescale()
eph = load('cache/de421.bsp')
NAMES = dict(mercury='mercury', venus='venus', mars='mars', jupiter='jupiter barycenter', saturn='saturn barycenter', sun='sun')

def geo_path(planet, y0, y1, step_days=1.0):
    fn = f'cache/geo_{planet}_{y0}_{y1}_{step_days}.npz'
    if os.path.exists(fn):
        d = np.load(fn); return {k: d[k] for k in d.files}
    t0 = ts.utc(y0, 1, 1); t1 = ts.utc(y1, 1, 1)
    n = int((t1.tt - t0.tt) / step_days) + 1
    tt = ts.tt_jd(t0.tt + step_days * np.arange(n))
    earth = eph['earth']
    p = earth.at(tt).observe(eph[NAMES[planet]])   # astrometric (light-time corrected) geocentric
    s = earth.at(tt).observe(eph['sun'])
    xyz = p.frame_xyz(ecliptic_J2000_frame).au
    sxyz = s.frame_xyz(ecliptic_J2000_frame).au
    lat, lon, _ = p.frame_latlon(ecliptic_J2000_frame)
    slat, slon, _ = s.frame_latlon(ecliptic_J2000_frame)
    out = dict(t=tt.tt, x=xyz[0], y=xyz[1], z=xyz[2], sx=sxyz[0], sy=sxyz[1], sz=sxyz[2],
               lon=lon.degrees, lat=lat.degrees, slon=slon.degrees)
    np.savez(fn, **out); return out

if __name__ == '__main__':
    d = geo_path('venus', 1900, 2053, 0.5)
    r = np.hypot(d['x'], d['y'])
    print('n', len(d['t']), 'r range', r.min(), r.max())
    # elongation sign: east (evening) if venus lon - sun lon in (0,180)
    dl = (d['lon'] - d['slon'] + 180) % 360 - 180
    print('evening frac', (dl > 0).mean())
    # transits: inferior conjunction with |lat| small
    from skyfield.api import utc
    import datetime
    sep = np.degrees(np.arccos(np.clip((d['x']*d['sx']+d['y']*d['sy']+d['z']*d['sz'])/np.sqrt((d['x']**2+d['y']**2+d['z']**2)*(d['sx']**2+d['sy']**2+d['sz']**2)),-1,1)))
    idx = np.where((sep < 0.3) & (r < 0.5))[0]
    for i in idx:
        print('transit-ish', ts.tt_jd(d['t'][i]).utc_iso(), sep[i])
