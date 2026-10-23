# High-precision mirror-symmetric Y-solution of the disc.
# Reduced system (c=0): t - r sin t = 2pi/3 ,  sqrt(1+r^2-2r cos t) = 1 - r + 3 r sin t
import mpmath as mp
mp.mp.dps=50
def sys(r,t): return [t-r*mp.sin(t)-2*mp.pi/3, mp.sqrt(1+r*r-2*r*mp.cos(t))-(1-r+3*r*mp.sin(t))]
r,t=mp.findroot(sys,(mp.mpf('0.60826'),mp.mpf('2.47195')))
print('r  =',mp.nstr(r,40)); print('t1 =',mp.nstr(t,40))
print('arcs: 2pi-2t1 =',mp.nstr(2*mp.pi-2*t,40),' t1 (twice)')
d0=1-r; d1=mp.sqrt(1+r*r-2*r*mp.cos(t))
print('seg lengths d0=1-r=',mp.nstr(d0,30),' d1=d2=',mp.nstr(d1,30))
print('common perimeter =',mp.nstr(t+d0+d1,30),' check',mp.nstr(2*mp.pi-2*t+2*d1,30))
A1=(mp.cos(t),mp.sin(t))
ang=mp.atan2(A1[1],A1[0]-r); print('angle at p between seg0 and seg1 (deg)=',mp.nstr(ang*180/mp.pi,30),' third angle',mp.nstr(360-2*ang*180/mp.pi,30))
print('area check', mp.nstr((t+ r*0 - r*mp.sin(t))/2 - mp.pi/3,5))
for name,val in [('r',r),('t1',t),('d1',d1),('perim',t+d0+d1),('sin t1',mp.sin(t)),('cos t1',mp.cos(t)),('r^2',r*r)]:
    print(name, mp.identify(val,['pi','sqrt(3)']), mp.identify(val))
