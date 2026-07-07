import numpy as np, time
import hero_ot as H

def main():
    t0=time.time()
    S_lloyd=720; N=5600; seed=4
    mu=H.build_mu(S_lloyd)
    s=H.sample_from_mu(N,S_lloyd,mu,seed)
    s=H.lloyd(s,S_lloyd,mu,iters=34)
    print("sites %.1fs"%(time.time()-t0),flush=True)
    H.render(s,4096,pal='ember',glow=0.34,wallk=0.09,
             save='/home/user/claude-mythos-self-play/art_bcm8/01_where_the_mass_goes.png')
    print("HERO done %.1fs"%(time.time()-t0),flush=True)

if __name__=='__main__':
    main()
