"""E8 mandala spinning animation. The mandala has 30-fold symmetry, so a 12°
(2pi/30) rotation is a seamless loop -> endless spin."""
import numpy as np, sys, math, time
sys.path.insert(0,'e8')
import mandala
from PIL import Image

def main(S=600, ss=2, N=60, out="e8/anim_e8_mandala.gif"):
    P,rad,ring_idx,nring,E,R=mandala.setup()
    frames=[]; t0=time.time()
    for f in range(N):
        ang=2*math.pi/30 * f/N
        im=mandala.render(P,ring_idx,nring,E,S=S,ss=ss,ang=ang,edge_bright=0.22,pt_bright=1.15)
        frames.append(im.convert("P",palette=Image.ADAPTIVE,colors=128))
        if f%10==0: print("frame",f,round(time.time()-t0,1))
    frames[0].save(out,save_all=True,append_images=frames[1:],duration=60,loop=0,optimize=True,disposal=2)
    print("saved",out,round(time.time()-t0,1))

if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=="preview":
        main(S=300,ss=1,N=20,out="e8/_anim_prev.gif")
    else:
        main()
