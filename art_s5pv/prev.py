import numpy as np,sys
from PIL import Image
pre,W,H=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
a=np.fromfile(pre+'_cam.f32',np.float32).reshape(H,W,3)
from scipy.ndimage import gaussian_filter
a=gaussian_filter(a,(1,1,0))
M=np.array([[3.2406,-1.5372,-0.4986],[-0.9689,1.8758,0.0415],[0.0557,-0.2040,1.0570]])
rgb=a@M.T
Y=a[...,1];s=np.percentile(Y[Y>0],99.0)
rgb=np.clip(rgb/s,0,None);rgb=1-np.exp(-1.5*rgb)
Image.fromarray((np.clip(rgb,0,1)**(1/2.2)*255).astype(np.uint8)).save(pre+'.png')
