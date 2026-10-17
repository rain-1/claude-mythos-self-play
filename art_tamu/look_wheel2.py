import numpy as np
from PIL import Image
D=np.loadtxt('math_collatz/dens.txt'); B=240
P=D[:,1:4].reshape(-1,B,3)   # octave 8..31
octs=np.arange(8,8+P.shape[0])
F=np.fft.rfft(P,axis=1); F[:,61:,:]=0; Ps=np.fft.irfft(F,n=B,axis=1)
for k in [12,16,20,24,28,31]:
    i=k-8; a=Ps[i,:,2]-Ps[i,:,2].mean(); b=Ps[-1,:,2]-Ps[-1,:,2].mean()
    print(k,'corr with oct31 %.3f'%(a@b/np.sqrt(a@a*b@b)),'std %.4f'%a.std())
S=1200; yy,xx=np.mgrid[0:S,0:S]; dx=(xx-S/2)/(S/2); dy=(yy-S/2)/(S/2); r=np.hypot(dx,dy); th=(np.arctan2(dx,-dy)/(2*np.pi))%1
oc=np.clip(12+(r-0.2)/0.78*20,12,31.999); io=oc.astype(int)-8; ib=(th*B).astype(int)%B
Z=Ps[io,ib,:]; Z=(Z-Ps[4:].mean((0,1)))/Ps[4:].std((0,1))
cols=np.array([[0.55,0.85,0.75],[0.75,0.65,0.92],[1.0,0.72,0.62]])
w=np.exp(2*Z); w/=w.sum(-1,keepdims=True); img=w@cols; img[(r<0.2)|(r>0.98)]=1
Image.fromarray((img*255).astype(np.uint8)).save('/tmp/claude-0/-home-user-claude-mythos-self-play/cb461e3e-8d57-5230-8c79-a9f7980093db/scratchpad/wheel2.png')
