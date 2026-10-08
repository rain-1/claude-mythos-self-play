# Thin-film (soap) interference colours: reflectance of a water film of thickness d (nm)
# viewed at incidence angle, integrated against analytic CIE 1931 CMFs (Wyman-Sloan-Shirley 2013) under D65-ish white.
import numpy as np
LAM=np.linspace(380,780,81)
def _g(x,mu,s1,s2):
    s=np.where(x<mu,s1,s2); return np.exp(-0.5*((x-mu)/s)**2)
XB=1.056*_g(LAM,599.8,37.9,31.0)+0.362*_g(LAM,442.0,16.0,26.7)-0.065*_g(LAM,501.1,20.4,26.2)
YB=0.821*_g(LAM,568.8,46.9,40.5)+0.286*_g(LAM,530.9,16.3,31.1)
ZB=1.217*_g(LAM,437.0,11.8,36.0)+0.681*_g(LAM,459.0,26.0,13.8)
M=np.array([[3.2406,-1.5372,-0.4986],[-0.9689,1.8758,0.0415],[0.0557,-0.2040,1.0570]])
def film_rgb(d, cos_i=1.0, nf=1.33):
    """d: array of thicknesses (nm). Returns linear sRGB of the reflected light, normalised so the
    film's mean (incoherent) reflectance maps to ~0.5 grey."""
    d=np.asarray(d,dtype=np.float64)
    sin_t2=(1-np.asarray(cos_i)**2)/nf**2
    cos_t=np.sqrt(1-sin_t2)
    ph=(4*np.pi*nf*d*cos_t)[...,None]/LAM   # optical phase difference
    R=np.sin(ph/2)**2                        # with the half-wave flip: 0 at d->0 (black film)
    X=(R*XB).sum(-1); Y=(R*YB).sum(-1); Z=(R*ZB).sum(-1)
    n=YB.sum()*0.5
    xyz=np.stack([X,Y,Z],-1)/n
    rgb=xyz@M.T
    return rgb
if __name__=="__main__":
    from PIL import Image
    d=np.linspace(0,1600,1200)
    rgb=film_rgb(d)
    for mix in (0.0,0.35,0.55):
        c=np.clip(mix+(1-mix)*0.5*rgb,0,1)  # pastelise toward white
        img=(np.clip(c,0,1)**(1/2.2)*255).astype(np.uint8)
        Image.fromarray(np.repeat(img[None],80,0)).save(f'_film_strip_{int(mix*100)}.png')
