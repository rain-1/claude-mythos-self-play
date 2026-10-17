import numpy as np
from PIL import Image
D=np.loadtxt('math_collatz/dens.txt'); B=240
x=D[:,0]; P=D[:,1:4]
m=(x>=10)
x=x[m]; P=P[m]
k0=x.min()
S=1200; yy,xx=np.mgrid[0:S,0:S]; cx=cy=S/2
dx=(xx-cx)/(S/2); dy=(yy-cy)/(S/2); r=np.hypot(dx,dy); th=(np.arctan2(dx,-dy)/(2*np.pi))%1
oc=10+ (r-0.15)/0.83*22   # octave
X=np.floor(oc)+th
i=np.clip(((X-k0)*B).astype(int),0,len(x)-1)
Z=(P-P.mean(0))/P.std(0)
cols=np.array([[0.55,0.85,0.75],[0.75,0.65,0.92],[1.0,0.72,0.62]])
w=np.exp(1.6*Z); w/=w.sum(1,keepdims=True)
C=w@cols
img=C[i]; img[(r<0.15)|(r>0.98)]=1
Image.fromarray((img*255).astype(np.uint8)).save('/tmp/claude-0/-home-user-claude-mythos-self-play/cb461e3e-8d57-5230-8c79-a9f7980093db/scratchpad/wheel.png')
