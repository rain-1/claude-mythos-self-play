Q(r) = 35534992*r^4 + 3306770731944*r^3 + 15172317493269316128*r^2 + 1093490321304049798772416*r + 18958669594580211381729967107;
Pc = -subst(Q(x), x, x - 36239);
gettime();
pts = hyperellratpoints(Pc, [7457*300000, 300000]);
print("D<=300000: ", gettime(), "ms  npts=", #pts);
for (i=1, #pts, print("PT: ", pts[i][1] - 36239, "  ", pts[i]));
print("DONE-SWEEP");
quit
