\\ Stage 2: for each locally-soluble fiber (p,q,M) of x^4+y^4+z^4=51t^4:
\\   - ellrank of Jacobian E_M: y^2 = x^3 + 4M x  (alarm-guarded)
\\   - hyperellratpoints on D_M: a^2 = M - v^4, height H1; flag square a
\\ POSITIVE CONTROL first: the N=17 surface fiber M = 17*583^4 - 758^4
\\ must show rank>=1 and a point with square a (Tomita's solution).
H1 = 1200;
control() = {
  my(M = 17*583^4 - 758^4, E, r, pts, ok=0);
  E = ellinit([0,0,0,4*M,0]);
  r = ellrank(E);
  pts = hyperellratpoints(M - 'x^4, 800);
  for(i=1, #pts,
    if(#pts[i] >= 2 && issquare(pts[i][2]) && pts[i][2] != 0, ok=1;
      print("CONTROL point v=", pts[i][1], " a=", pts[i][2], " sqrt_a=", sqrtint(numerator(pts[i][2]))/sqrtint(denominator(pts[i][2])))));
  print("CONTROL M=", M, " rank=", r, " pts=", #pts, " square_found=", ok);
}
control();
{
  my(v = readvec("surv_list.gp")[1]);
  for(i = 1, #v,
    my(p = v[i][1], q = v[i][2], M = v[i][3], E, r, pts, sq = 0, err = 0);
    E = ellinit([0,0,0,4*M,0]);
    iferr(alarm(12, r = ellrank(E)), e, r = [-1,-1]; err = 1);
    if(type(r) == "t_STR" || r == 0, r = [-1,-1]; err = 1);
    iferr(pts = hyperellratpoints(M - 'x^4, H1), e, pts = []; err = 1);
    for(j = 1, #pts,
      if(#pts[j] >= 2 && pts[j][2] != 0 && issquare(pts[j][2]),
        sq = 1;
        print("SOLUTION! p=", p, " q=", q, " M=", M, " v=", pts[j][1], " a=", pts[j][2])));
    print("FIBER p=", p, " q=", q, " M=", M, " rlow=", r[1], " rhigh=", r[2],
          " npts=", #pts, " sq=", sq, " err=", err);
  );
}
print("STAGE2_DONE");
quit
