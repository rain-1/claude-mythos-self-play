import numpy as np
from PIL import Image
W=1600; Hr=14
N=W
img=np.ones((Hr*40, W,3))
pal=np.array([[1,1,1],[1,.8,.6],[.6,.85,1],[.8,.7,1],[.7,.95,.7],[1,.7,.85],[1,.95,.6],[.6,.6,.9]])
def digits(n):
    ds=[]; b=2
    while n>0:
        d=n%b; ds.append(d); n//=b; b=d+2
    return ds
for n in range(N):
    ds=digits(n*1)
    for j,d in enumerate(ds[:Hr]):
        img[j*40:(j+1)*40, n]=pal[min(d,7)]
Image.fromarray((img*255).astype(np.uint8)).save('proto/snow_tapestry.png')
print(digits(23), digits(40319))
