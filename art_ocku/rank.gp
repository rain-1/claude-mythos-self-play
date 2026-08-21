default(parisizemax, 4G);
a2 = -5833074784657799209713288129600;
a4 = 39727910629544917128945287152961161352250012701271680640000;
a6 = -103508734610592080142357362109071185998354210009583011061236514785521898934889963712000000;
E = ellinit([0,a2,0,a4,a6]);
print("disc sign / j: ", precision(E.j, 20));
[Em, ch] = ellminimalmodel(E);
print("minimal model: ", Em[1..5]);
print("torsion: ", elltors(Em));
rk = ellrank(Em, 2);
print("ellrank result: ", rk);
if (#rk >= 4 && #rk[4] > 0,
  for (i=1, #rk[4],
    print("point ", i, ": ", rk[4][i], "  height ", precision(ellheight(Em, rk[4][i]),15));
  );
);
