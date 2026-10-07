import numpy as np
def winding(X,Y,W,H):
    """X,Y: closed polygon in pixel coords. Returns int winding number per pixel (centres)."""
    x0,y0=X,Y; x1,y1=np.roll(X,-1),np.roll(Y,-1)
    acc=np.zeros((H,W+1),np.int32)
    lo=np.minimum(y0,y1); hi=np.maximum(y0,y1)
    r0=np.ceil(lo-0.5).astype(np.int64); r1=np.ceil(hi-0.5).astype(np.int64)  # rows j with lo<=j+.5<hi
    sgn=np.where(y1>y0,1,-1)
    cnt=r1-r0; m=cnt>0
    idx=np.repeat(np.nonzero(m)[0],cnt[m])
    off=np.arange(len(idx))-np.repeat(np.cumsum(cnt[m])-cnt[m],cnt[m])
    j=r0[idx]+off; yc=j+0.5
    t=(yc-y0[idx])/(y1[idx]-y0[idx]); xc=x0[idx]+t*(x1[idx]-x0[idx])
    col=np.clip(np.ceil(xc-0.5).astype(np.int64),0,W); ok=(j>=0)&(j<H)
    np.add.at(acc,(j[ok],col[ok]),sgn[idx][ok])
    return np.cumsum(acc,axis=1)[:,:W]
