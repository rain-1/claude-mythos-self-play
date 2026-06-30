import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, gaussian_filter1d
from eg import uniform_syt_staircase, word_from_Q, trajectories
from greatcircle import build_great_circle
from figkit import annotate
import colorsys, time, sys

def render(n=66, S=1600, seed=5):
    t0=time.time(); rng=np.random.default_rng(seed)
    Q=uniform_syt_staircase(n,rng); w=word_from_Q(Q)
    pos=trajectories(w,n); L=pos.shape[1]-1; th=np.pi*np.arange(L+1)/L
    H=(pos-(n-1)/2)/((n-1)/2); Hs=gaussian_filter1d(H,sigma=L*0.02,axis=1)
    circles=[]; r2=[]
    for k in range(n):
        h=Hs[k]; a=h[0]; b=np.sum((h-a*np.cos(th))*np.sin(th))/np.sum(np.sin(th)**2)
        m=a*np.cos(th)+b*np.sin(th); sr=np.sum((h-m)**2); stot=np.sum((h-h.mean())**2)
        r2.append(1-sr/stot if stot>1e-9 else 1.0)
        amp2=a*a+b*b
        if amp2>1: f=np.sqrt(0.999/amp2); a*=f; b*=f
        circles.append((a,b,k))
    r2=np.array(r2)
    print("median R2",np.median(r2),"mean",r2.mean(),"t=%.1f"%(time.time()-t0))
    # camera rotation
    def rotm(ax,ay):
        cx,sx=np.cos(ax),np.sin(ax); cy,sy=np.cos(ay),np.sin(ay)
        Rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]); Ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
        return Ry@Rx
    R=rotm(-0.42,0.6)
    W=S; acc=np.zeros((W,W,3)); rad=0.46*W
    def splat(P3, col, bright):
        Pr=P3@R.T
        x=(0.5+Pr[:,0]*0.46)*(W-1); y=(0.5-Pr[:,1]*0.46)*(W-1); z=Pr[:,2]
        depth=(z+1)/2
        ix=np.clip(x.astype(int),0,W-2); iy=np.clip(y.astype(int),0,W-2)
        b=bright*(0.25+0.75*depth)[:,None]*col
        for ox in (0,1):
          for oy in (0,1): np.add.at(acc.reshape(-1,3),(iy+oy)*W+(ix+ox),b)
    # faint sphere grid
    for lat in np.linspace(-1,1,9):
        r=np.sqrt(max(0,1-lat*lat)); t=np.linspace(0,2*np.pi,240)
        splat(np.stack([r*np.cos(t),np.full_like(t,lat),r*np.sin(t)],1),np.array([0.3,0.32,0.4]),0.06)
    for lon in np.linspace(0,np.pi,9):
        t=np.linspace(0,2*np.pi,240)
        splat(np.stack([np.sin(t)*np.cos(lon),np.cos(t),np.sin(t)*np.sin(lon)],1),np.array([0.3,0.32,0.4]),0.06)
    # great circles
    tt_full=np.linspace(0,2*np.pi,420); tt_arc=np.linspace(0,np.pi,260)
    for i,(a,b,k) in enumerate(circles):
        u,v=build_great_circle(a,b, 2*np.pi*i/n)
        r,g,bb=colorsys.hls_to_rgb((k/n*0.92)%1,0.6,0.95); col=np.array([r,g,bb])
        Cf=np.cos(tt_full)[:,None]*u+np.sin(tt_full)[:,None]*v
        splat(Cf,col,0.10)                                   # full circle faint
        Ca=np.cos(tt_arc)[:,None]*u+np.sin(tt_arc)[:,None]*v
        splat(Ca,col,0.45)                                   # trajectory arc bright
    acc/=np.percentile(acc[acc>0],99.7); acc=np.clip(acc,0,1)
    img=acc.copy()
    for c in range(3): img[...,c]+=0.55*gaussian_filter(acc[...,c],1.5)+0.3*gaussian_filter(acc[...,c],6)
    img=np.clip(img,0,1)**0.9
    out=Image.fromarray((img*255).astype(np.uint8))
    body=("The deepest fact about sorting networks, made visible. Each wire's trajectory in the uniform random network "
          "(Figure 6) is, in the limit, a SINE curve (verified: median R^2 = %.2f against h(t)=a cos t + b sin t). And "
          "every sine curve is the SHADOW of a great circle: projecting a great circle cos(t)u + sin(t)v onto a fixed "
          "axis gives R sin(t+phi). So the whole sorting network is the flattened shadow of a sphere woven from great "
          "circles - one per wire, lifted here from the actual trajectories (the lifts are exact great circles: on the "
          "unit sphere and through the origin to 1e-16). This 'Archimedean' sphere picture, conjectured by "
          "Angel-Holroyd-Romik-Virag and proved by Dauvergne, is where a random shuffle turns out to be hiding a "
          "perfectly round, perfectly classical object."%np.median(r2))
    fig=annotate(out,"FIGURE 12 - THE ARCHIMEDEAN SPHERE","A Shuffle Is the Shadow of a Sphere",body,accent=(150,210,245))
    fig.save("12_great_circles.png"); print("saved",fig.size,"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render(seed=int(sys.argv[1]) if len(sys.argv)>1 else 5)
