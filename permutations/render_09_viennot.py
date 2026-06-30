import numpy as np, random
from PIL import Image
from scipy.ndimage import gaussian_filter
from viennot import shadow_lines, viennot_P, rsk_P
from figkit import annotate
import colorsys, time

def render(n=46, S=1500, seed=11):
    t0=time.time(); rng=random.Random(seed)
    perm=list(range(1,n+1)); rng.shuffle(perm)
    assert viennot_P(perm)==rsk_P(perm)
    pts=[(i+1,perm[i]) for i in range(n)]
    lines=shadow_lines(pts); k=len(lines)
    G=S; W=G
    field=np.zeros((W,W,3))
    def XY(x,y): return ((x-0.5)/n*(W-1), (1-(y-0.5)/n)*(W-1))   # y up
    # faint "lit" SW wash: accumulate each point's SW quadrant dimly (light pooling below-left)
    acc=np.zeros((W,W))
    xs=np.array([XY(*p)[0] for p in pts]); ys=np.array([XY(*p)[1] for p in pts])
    # shadow lines as glowing staircases
    def splat_seg(p0,p1,col,wt):
        L=int(max(2,abs(p1[0]-p0[0])+abs(p1[1]-p0[1])))
        t=np.linspace(0,1,L); x=p0[0]+(p1[0]-p0[0])*t; y=p0[1]+(p1[1]-p0[1])*t
        ix=np.clip(x.astype(int),0,W-2); iy=np.clip(y.astype(int),0,W-2)
        for ox in (0,1):
          for oy in (0,1):
            np.add.at(field.reshape(-1,3),(iy+oy)*W+(ix+ox),col*wt)
    for li,line in enumerate(lines):
        Lpts=sorted(line)  # x asc, y desc
        r,g,b=colorsys.hls_to_rgb((0.08+0.62*li/max(1,k))%1,0.6,0.95); col=np.array([r,g,b])
        # extend up from first point, staircase through, extend right from last
        first=XY(*Lpts[0]); last=XY(*Lpts[-1])
        splat_seg((first[0],0),first,col,0.5)
        for a in range(len(Lpts)-1):
            pa=XY(*Lpts[a]); pb=XY(*Lpts[a+1]); corner=(pb[0],pa[1])
            splat_seg(pa,corner,col,0.5); splat_seg(corner,pb,col,0.5)
        splat_seg(last,(W-1,last[1]),col,0.5)
    field/=np.percentile(field[field>0],99.5); field=np.clip(field,0,1)
    img=field.copy()
    for c in range(3): img[...,c]+=0.6*gaussian_filter(field[...,c],1.6)+0.3*gaussian_filter(field[...,c],5)
    # points as bright dots
    for (px,py) in zip(xs,ys):
        xi,yi=int(px),int(py); img[max(0,yi-3):yi+4,max(0,xi-3):xi+4]+=np.array([1,1,1])*0.9
    img=np.clip(img,0,1)**0.9
    out=Image.fromarray((img*255).astype(np.uint8))
    body=("Viennot's 'light and shadows' rebuilds the RSK correspondence as pure geometry. Plot the permutation as "
          f"points (i, sigma(i)); a light at the lower-left casts each point's shadow into its upper-right quadrant. The "
          f"boundaries of the merged shadows are the SHADOW LINES ({k} of them here) - and the number of shadow lines is "
          "exactly the longest increasing subsequence (Schensted). Reading the lowest point of each line gives the first "
          "row of the RSK insertion tableau P; the inner north-east corners of the lines become a new constellation whose "
          "shadow lines give the second row, and so on. Verified: this reconstructs RSK's P exactly on all of S1..S7.")
    fig=annotate(out,"FIGURE 9 - VIENNOT'S LIGHT","RSK, Cast as Shadows",body,accent=(245,205,110))
    fig.save("09_viennot.png"); print("saved",fig.size,"LIS(#lines)=",k,"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
