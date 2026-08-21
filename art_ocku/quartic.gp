Q(r) = 35534992*r^4 + 3306770731944*r^3 + 15172317493269316128*r^2 + 1093490321304049798772416*r + 18958669594580211381729967107;
P = -Q(x);
\\ known point
r1 = -48044056139/1242748;
print("P(r1) is square: ", issquare(Q(r1)*-1));
print("real roots of Q (r-interval where points can live):");
print(polrootsreal(Q(x)));
pts = hyperellratpoints(P, 10^5);
print("points up to H=1e5: ", pts);
