"""Colourise the Ronkin order map: each amoeba complement component flat-coloured by
its integer lattice-point order (i,j) via a 3-fold barycentric hue; the tropical curve
(discontinuity of the order label / ridge of the Monge-Ampere measure) drawn dark."""
import numpy as np
from PIL import Image
from scipy import ndimage

A = np.array([[0.0, np.sqrt(3)/2],[-1.0, 0.5]])

def bary_color(i,j,d):
    """3-fold symmetric colour from barycentric (i,j,k=d-i-j)."""
    k=d-i-j
    a=np.clip(i/d,0,1); b=np.clip(j/d,0,1); c=np.clip(k/d,0,1)
    s=a+b+c+1e-9; a,b,c=a/s,b/s,c/s
    # three anchor colours at the triangle corners (cool jewel triad)
    C_i=np.array([210,150,60])   # gold  (i corner)
    C_j=np.array([60,150,200])   # azure (j corner)
    C_k=np.array([170,80,190])   # violet(k corner)
    col=a[...,None]*C_i+b[...,None]*C_j+c[...,None]*C_k
    return col

def build_image(field_npz, S=2048, tag='ronkin_color', disp_half=None):
    z=np.load(field_npz)
    N,gx,gy=z['N'],z['gx'],z['gy']; xr=z['xr']; yr=z['yr']; d=int(z['d']); half=float(z['half'])
    if disp_half is not None: half=disp_half
    Ng=N.shape[0]
    # order label = rounded gradient, clipped to Newton triangle
    oi=np.clip(np.round(gx),0,d); oj=np.clip(np.round(gy),0,d)
    oi=np.minimum(oi,d-0*oj);
    bad=oi+oj>d
    # where outside triangle, project to nearest valid (keep for colour only)
    oj=np.where(bad, np.clip(d-oi,0,d), oj)
    col=bary_color(oi,oj,d)                      # (Ng,Ng,3) in (x,y) grid, indexed [ix,iy]
    # Monge-Ampere spine: gradient magnitude of the order label (edges) -> dark seam
    lab=oi*(d+1)+oj
    edge=ndimage.grey_dilation(lab,size=3)!=ndimage.grey_erosion(lab,size=3)
    edge=ndimage.gaussian_filter(edge.astype(float),0.7)
    # also darken by how 'amoeba' a pixel is: non-integer gradient => on the amoeba
    frac=np.hypot(gx-np.round(gx),gy-np.round(gy))   # 0 in holes, >0 on amoeba
    amoeba=np.clip(frac/0.5,0,1)
    # compose in (x,y) grid: col is [ix,iy]; make an image [row=y,col=x]
    imgxy=col.transpose(1,0,2)[::-1]              # row=y (up), col=x
    edgeI=edge.transpose(1,0)[::-1]; amI=amoeba.transpose(1,0)[::-1]
    # warp (x,y) image into symmetric UV frame
    us=np.linspace(-half,half,S); vs=np.linspace(-half,half,S)
    UU,VV=np.meshgrid(us,vs)
    Ainv=np.linalg.inv(A); XY=Ainv@np.vstack([UU.ravel(),VV.ravel()])
    Xg=XY[0].reshape(S,S); Yg=XY[1].reshape(S,S)
    # map (x,y)->grid index
    def to_idx(Xg,Yg):
        cxi=(Xg-xr[0])/(xr[1]-xr[0])*(Ng-1)
        cyi=(Yg-yr[0])/(yr[1]-yr[0])*(Ng-1)
        # imgxy has row=y flipped: row index = (Ng-1) - cyi
        row=(Ng-1)-cyi; colx=cxi
        return row,colx
    row,colx=to_idx(Xg,Yg)
    warp=np.stack([row,colx])
    out=np.zeros((S,S,3))
    for ch in range(3):
        out[...,ch]=ndimage.map_coordinates(imgxy[...,ch],warp,order=1,mode='nearest')
    edgeW=ndimage.map_coordinates(edgeI,warp,order=1,mode='nearest')
    amW=ndimage.map_coordinates(amI,warp,order=1,mode='nearest')
    # darken flesh(amoeba) region toward deep base; keep holes bright flat colour
    base=np.array([8,9,20.])
    out=out*(1-0.72*amW[...,None])+base*(0.72*amW[...,None])
    # dark seam on tropical curve
    out=out*(1-0.85*edgeW[...,None])
    Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(f'{tag}.png')
    print(tag,'saved')

if __name__=='__main__':
    import sys
    build_image(sys.argv[1], S=int(sys.argv[2]) if len(sys.argv)>2 else 1000,
                tag=sys.argv[3] if len(sys.argv)>3 else 'ronkin_color')
