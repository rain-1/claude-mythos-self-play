\\ Deep point sweeps on the 51-fibers. Any square 'a' is a SOLUTION to MO 514531.
default(parisize, 800000000);
sqchk(tag, p, q, M, pts) = {
  for(j = 1, #pts,
    if(#pts[j] >= 2 && pts[j][2] != 0 && issquare(pts[j][2]),
      print("SOLUTION! ", tag, " p=", p, " q=", q, " M=", M, " pt=", pts[j])));
}
{
  \\ pass A: all 863 survivors at H = 2*10^5
  my(v = readvec("surv_list.gp")[1]);
  for(i = 1, #v,
    my(p = v[i][1], q = v[i][2], M = v[i][3], pts);
    iferr(pts = hyperellratpoints(M - 'x^4, 2*10^5), e, pts = []);
    sqchk("A", p, q, M, pts);
    if(i % 50 == 0, print("passA ", i, "/", #v, " t=", getabstime()));
  );
  print("PASS_A_DONE ", getabstime());
}
{
  \\ pass B: favorites at H = 5*10^6
  my(v = readvec("fav_list.gp")[1]);
  for(i = 1, #v,
    my(p = v[i][1], q = v[i][2], M = v[i][3], pts);
    iferr(pts = hyperellratpoints(M - 'x^4, 5*10^6), e, pts = []);
    sqchk("B", p, q, M, pts);
    print("passB ", i, "/", #v, " p=", p, " q=", q, " npts=", #pts, " t=", getabstime());
  );
  print("PASS_B_DONE ", getabstime());
}
{
  \\ pass C: the primal fiber (1,1), M=50, very deep
  my(pts);
  pts = hyperellratpoints(50 - 'x^4, 4*10^7);
  print("passC M=50 npts=", #pts);
  print("passC pts=", pts);
  sqchk("C", 1, 1, 50, pts);
  print("PASS_C_DONE ", getabstime());
}
print("DEEP3_DONE");
quit
