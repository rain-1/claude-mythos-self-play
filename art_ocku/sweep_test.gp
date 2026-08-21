Q(r) = 35534992*r^4 + 3306770731944*r^3 + 15172317493269316128*r^2 + 1093490321304049798772416*r + 18958669594580211381729967107;
Pc = -subst(Q(x), x, x - 36239);  \\ recentered: window |x| <= 7457
gettime();
pts = hyperellratpoints(Pc, [7457*50, 50]);
print("D<=50: ", gettime(), "ms  npts=", #pts, "  ", pts);
pts = hyperellratpoints(Pc, [7457*200, 200]);
print("D<=200: ", gettime(), "ms  npts=", #pts, "  ", pts);
quit
