default(parisizemax, 8G);
\r rank2_pre.gp
print("--- divisibility of seed ---");
for (k=2, 6, my(Gp); my(res = ellisdivisible(E, seed, k, &Gp)); print("divisible by ",k,": ", res, if(res, Str("  -> ", Gp), "")));
print("--- higher effort rank hunt ---");
rk = ellrank(E, 5, [seed]);
print("ellrank effort5: ", rk[1..3]);
for (i=1, #rk[4], print("pt ", i, " height ", precision(ellheight(E, rk[4][i]), 15), " : ", rk[4][i]));
print("DONE-RANK3");
quit
