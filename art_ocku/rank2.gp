default(parisizemax, 6G);
E = ellinit([0,-5833074784657799209713288129600,0,39727910629544917128945287152961161352250012701271680640000,-103508734610592080142357362109071185998354210009583011061236514785521898934889963712000000]);
seed = [13875154685373552385034825805345921700/2128681,16800900899486015150600343733776556742192714633883985000/3105745579];
print("seed on curve: ", ellisoncurve(E, seed));
print("seed height: ", precision(ellheight(E, seed), 15));
print("torsion: ", elltors(E)[1]);
rk = ellrank(E, 2, [seed]);
print("ellrank: ", rk);
if (#rk[4] > 0, for (i=1, #rk[4], print("gen ", i, ": ", rk[4][i]); print("   height ", precision(ellheight(E, rk[4][i]), 15))));
print("DONE-RANK");
quit
