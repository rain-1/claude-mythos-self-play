\\ exact root numbers of E_M: y^2 = x^3 + 4M x for all survivor fibers, both surfaces
{
  my(v = readvec("surv_list.gp")[1], w, cnt = vector(2));
  for(i = 1, #v,
    w = ellrootno(ellinit([0,0,0,4*v[i][3],0]));
    if(w == -1, cnt[1]++, cnt[2]++);
    print("RN51 p=", v[i][1], " q=", v[i][2], " w=", w));
  print("SUMMARY51 odd(w=-1)=", cnt[1], " even(w=+1)=", cnt[2]);
}
{
  my(v = readvec("surv17_list.gp")[1], w, cnt = vector(2));
  for(i = 1, #v,
    w = ellrootno(ellinit([0,0,0,4*v[i][3],0]));
    if(w == -1, cnt[1]++, cnt[2]++);
    print("RN17 p=", v[i][1], " q=", v[i][2], " w=", w));
  print("SUMMARY17 odd(w=-1)=", cnt[1], " even(w=+1)=", cnt[2]);
}
\\ ladder points for the 36 favorite 51-fibers at H=1e5 (for the hero's smoke threads)
{
  my(v = readvec("fav_list.gp")[1], pts);
  for(i = 1, #v,
    pts = hyperellratpoints(v[i][3] - 'x^4, 10^5);
    print("LAD p=", v[i][1], " q=", v[i][2], " M=", v[i][3], " pts=", pts));
  print("LADDERS_DONE");
}
quit
