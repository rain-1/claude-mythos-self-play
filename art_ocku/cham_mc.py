# Monte-Carlo validation of the solver's transition/absorption conventions.
import numpy as np, sys
rng = np.random.default_rng(1)
def sim(r,b,g,n):
    wins = np.zeros(3)  # R,G,B
    for _ in range(n):
        rr,bb,gg = r,b,g
        while rr and bb and gg:
            wRB, wBG, wGR = rr*bb, bb*gg, gg*rr
            u = rng.random()*(wRB+wBG+wGR)
            if u < wRB: rr,bb = rr+1,bb-1
            elif u < wRB+wBG: bb,gg = bb+1,gg-1
            else: rr,gg = rr-1,gg+1
        if bb==0: wins[1]+=1     # green wins
        elif gg==0: wins[0]+=1   # red wins
        else: wins[2]+=1         # blue wins
    return wins/n
w = sim(1,1,10,200000)
print("MC  (1,1,10):  P_R=%.5f P_G=%.5f P_B=%.5f" % (w[0],w[1],w[2]))
w2 = sim(3,4,5,200000)
print("MC  (3,4,5):   P_R=%.5f P_G=%.5f P_B=%.5f" % (w2[0],w2[1],w2[2]))
