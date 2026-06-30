import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from figkit import annotate
import time

def inversion_distribution(n):
    """coeffs of q-factorial [n]_q! = prod_{i=1}^n (1+q+...+q^{i-1}); coeff[k]=#perms with k inversions."""
    poly=np.array([1.0])
    for i in range(1,n+1):
        block=np.ones(i)
        poly=np.convolve(poly,block)
    return poly   # length n(n-1)/2 + 1

def render(S=1600, seed=0):
    t0=time.time()
    W=S; H=int(S*0.62); 
    field=np.zeros((H,W,3))
    ns=[5,8,13,21,34]
    cols=[(0.95,0.40,0.45),(0.95,0.65,0.30),(0.55,0.85,0.35),(0.30,0.78,0.85),(0.65,0.55,0.95)]
    def plot_curve(xsN,ysN,col,wd=2.0):
        xp=(xsN*(W-1)).astype(float); yp=((1-ysN)*(H-1)).astype(float)
        for a in range(len(xp)-1):
            x0,y0,x1,y1=xp[a],yp[a],xp[a+1],yp[a+1]
            L=int(max(2,abs(x1-x0)+abs(y1-y0)))
            tt=np.linspace(0,1,L)
            xs=x0+(x1-x0)*tt; ys=y0+(y1-y0)*tt
            ix=np.clip(xs.astype(int),0,W-2); iy=np.clip(ys.astype(int),0,H-2)
            for ox in (0,1):
              for oy in (0,1):
                np.add.at(field.reshape(-1,3),(iy+oy)*W+(ix+ox),np.array(col)*0.5)
    for n,col in zip(ns,cols):
        c=inversion_distribution(n)
        mean=n*(n-1)/4
        # center & scale: x in [-3,3] std units
        var=n*(2*n+5)*(n-1)/72
        sd=np.sqrt(var)
        k=np.arange(len(c))
        xsN=( (k-mean)/sd/6.5 +0.5 )
        ysN=c/c.max()
        m=(xsN>=0)&(xsN<=1)
        plot_curve(xsN[m],ysN[m],col)
    # limiting Gaussian (dashed bright)
    xx=np.linspace(0,1,800); g=np.exp(-0.5*(((xx-0.5)*6.5))**2)
    plot_curve(xx,g,(1,1,1))
    field/=np.percentile(field[field>0],99.5); field=np.clip(field,0,1)
    img=field.copy()
    for kk in range(3): img[...,kk]+=0.6*gaussian_filter(field[...,kk],2.0)+0.3*gaussian_filter(field[...,kk],6)
    img=np.clip(img*1.15,0,1)
    out=Image.fromarray((img*255).astype(np.uint8))
    dr=ImageDraw.Draw(out)
    try: fnt=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",int(S*0.016))
    except: fnt=ImageFont.load_default()
    for i,(n,col) in enumerate(zip(ns,cols)):
        dr.text((int(W*0.03),int(H*0.05)+i*int(S*0.022)),f"n = {n}",font=fnt,fill=tuple(int(v*255) for v in col))
    dr.text((int(W*0.03),int(H*0.05)+len(ns)*int(S*0.022)),"Gaussian",font=fnt,fill=(235,235,235))
    body=("How many of the n! permutations have exactly k inversions (pairs out of order)? The counts are the "
          "coefficients of the q-factorial [n]_q! = (1)(1+q)(1+q+q^2)...(1+...+q^(n-1)) - the MAHONIAN distribution. "
          "Each curve is the exact distribution for one n, centred and scaled to unit width; as n grows it converges to "
          "a Gaussian (mean n(n-1)/4, variance n(n-1)(2n+5)/72) - a central limit theorem for disorder, since "
          "inv(sigma) is a sum of nearly-independent indicator variables (the Lehmer digits).")
    fig=annotate(out,"FIGURE 4 - MAHONIAN STATISTICS","Counting Disorder: Inversions",body,accent=(120,200,150))
    fig.save("04_mahonian.png"); print("saved",fig.size,"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
