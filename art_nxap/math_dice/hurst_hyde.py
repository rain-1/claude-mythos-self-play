# Fair point of the Hurst-Hyde (arXiv:2609.01643) modified-CSA model for the pentagonal prism,
# plus linear interpolation of their measured base proportions (their Table 1), target 2/7.
import mpmath as mp
mp.mp.dps = 30
from prism_fair import fair_L_exact
def csa_base(hr):   # both bases, h/r = full height / circumradius
    n=5; h=mp.mpf(hr)/2; a=mp.cos(mp.pi/n)
    cap = 2*mp.pi - 2*n*mp.asin(mp.sin(mp.pi/n)*h/mp.sqrt(h*h+a*a))
    return 2*cap/(4*mp.pi)
def PB(hr, A=mp.mpf('1.46'), p=mp.mpf('2.33')):
    x = mp.log(A/mp.mpf(hr)); g = csa_base(hr)
    return g/(g + (1-g)/mp.e**(x*p))
t = mp.mpf(2)/7
print("CSA fair h/r:", mp.nstr(mp.findroot(lambda q: csa_base(q)-t, 1.7),12), " (closed form", mp.nstr(fair_L_exact(5),12),")")
for A,p in (("1.46","2.33"),("1.46","2.31"),("1.46","2.30")):
    print("Hurst-Hyde model fair h/r (a=%s,p=%s):"%(A,p), mp.nstr(mp.findroot(lambda q: PB(q,mp.mpf(A),mp.mpf(p))-t, 1.6),6))
data = [("8",7.930,10.877,3985,4509),("10",9.908,9.709,3701,5451),("11",11.140,8.886,1491,2879),
        ("12",11.828,8.843,2276,5070),("13",12.650,8.457,512,1545),("DS",16.313,11.005,715,2056),
        ("AD",15.413,9.986,890,2921),("F",12.973,8.297,630,2131),("14",13.840,8.167,1049,4734),
        ("16",15.813,7.633,601,5091),("18",17.848,7.182,280,4681)]
pts = sorted((h/r, k/n, lab) for lab,h,r,k,n in data)
for q,pr,lab in pts: print(lab, round(q,4), round(pr,4), "CSA", round(float(csa_base(q)),4))
for (q1,p1,_),(q2,p2,_) in zip(pts,pts[1:]):
    if (p1-float(t))*(p2-float(t))<=0:
        print("empirical crossing of 2/7 between h/r", round(q1,4), round(q2,4), "-> linear interp", round(q1+(float(t)-p1)*(q2-q1)/(p2-p1),4))
