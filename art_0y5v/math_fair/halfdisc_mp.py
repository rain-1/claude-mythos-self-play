# Non-congruent fair chord-pair partition of the unit half-disc (y>=0, radius 1), to 30 digits.
# right piece: diameter [a,1], arc [0,th1], chord (cos th1,sin th1)-(a,0); left piece: arc [th2,pi], diameter [-1,b], chord (b,0)-(cos th2,sin th2)
import mpmath as mp
mp.mp.dps=40
def F(a,b,t1,t2):
    c1=mp.sqrt((mp.cos(t1)-a)**2+mp.sin(t1)**2); c2=mp.sqrt((mp.cos(t2)-b)**2+mp.sin(t2)**2)
    AR=(t1-a*mp.sin(t1))/2; AL=(mp.pi-t2+b*mp.sin(t2))/2
    PR=(1-a)+t1+c1; PL=(mp.pi-t2)+(b+1)+c2; PM=(a-b)+(t2-t1)+c1+c2
    return [AR-mp.pi/6,AL-mp.pi/6,PR-PM,PL-PM]
def solve(g):
    x=mp.findroot(F,g); a,b,t1,t2=x
    c1=mp.sqrt((mp.cos(t1)-a)**2+mp.sin(t1)**2)
    return x,(1-a)+t1+c1
k=1/mp.sqrt(2)
import math
g1=(0.0612320952*k, -0.4481248855*k, math.atan2(1.2509211198,0.6596941352), math.atan2(1.3819688733,-0.3002699340))
x,P=solve(g1)
print('non-congruent solution: a,b,th1,th2 =');[print('  ',mp.nstr(v,32)) for v in x]
print('  common perimeter',mp.nstr(P,32),' residual',mp.nstr(max(abs(v) for v in F(*x)),3))
a,b,t1,t2=x
# corner angles of pieces (interior angles in degrees)
def ang(u,v): return mp.degrees(mp.acos((u[0]*v[0]+u[1]*v[1])/mp.sqrt((u[0]**2+u[1]**2)*(v[0]**2+v[1]**2))))
P1=(mp.cos(t1),mp.sin(t1)); P2=(mp.cos(t2),mp.sin(t2))
# right piece corners: at (a,0) between diameter dir (1,0) and chord dir P1-(a,0); at P1 between chord and arc tangent (-sin t1,cos t1) reversed
print('right piece: angle at (a,0)=',mp.nstr(ang((1,0),(P1[0]-a,P1[1])),20),' at P1=',mp.nstr(ang((a-P1[0],-P1[1]),(mp.sin(t1),-mp.cos(t1))),20),' at (1,0)=90')
print('left piece: angle at (b,0)=',mp.nstr(ang((-1,0),(P2[0]-b,P2[1])),20),' at P2=',mp.nstr(ang((b-P2[0],-P2[1]),(-mp.sin(t2),mp.cos(t2))),20),' at (-1,0)=90')
print('middle piece: angles at (a,0),(b,0)=',mp.nstr(180-ang((1,0),(P1[0]-a,P1[1])),20),mp.nstr(180-ang((-1,0),(P2[0]-b,P2[1])),20),
      ' at P1,P2=',mp.nstr(180-ang((a-P1[0],-P1[1]),(mp.sin(t1),-mp.cos(t1))),20),mp.nstr(180-ang((b-P2[0],-P2[1]),(-mp.sin(t2),mp.cos(t2))),20))
print('arc lengths: right',mp.nstr(t1,20),' middle',mp.nstr(t2-t1,20),' left',mp.nstr(mp.pi-t2,20))
print('diameter parts: right',mp.nstr(1-a,20),' middle',mp.nstr(a-b,20),' left',mp.nstr(1+b,20))
# symmetric solution
xs,Ps=solve((0.30,-0.30,1.33,math.pi-1.33)); print('mirror-symmetric chord solution a,b,th1,th2:',[mp.nstr(v,20) for v in xs],' perimeter',mp.nstr(Ps,20))
