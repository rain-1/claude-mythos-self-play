import numpy as np, time
from PIL import Image
from petit import render
from cake import look, tonemap
lin=lambda c:(np.array(c)/255.)**2.2
S=np.zeros((2,64)); PCS=np.zeros((2,3,9))
# cake 0: disc r=0.45 (disc primitive)
S[0,:9]=[-0.6,0,0.30,0,1, 1,0,0,0.45]
r0=0.60826003*0.45; a0=0.66964559
p=np.array([-r0,0]); B=0.45*np.c_[np.cos([-a0,a0,np.pi]),np.sin([-a0,a0,np.pi])]
for i in range(3):
    d1=B[i]-p; d2=B[(i+1)%3]-p
    n1=np.array([d1[1],-d1[0]]); n1/=np.linalg.norm(n1); n2=np.array([-d2[1],d2[0]]); n2/=np.linalg.norm(n2)
    v=-(n1+n2); v/=np.linalg.norm(v)
    PCS[0,i]=[n1[0],n1[1],n1@p, n2[0],n2[1],n2@p, *(0.04*v), [0,1,1][i]]
# cake 1: square side 0.7, chords cut into thirds (congruent) as a test
h=0.35
S[1,:21]=[0.6,0,0.30,0,4, 0,1,0,h, 0,-1,0,h, 0,0,1,h, 0,0,-1,h]
PCS[1,0]=[1,0,-h/3, 0,0,1, -0.04,0, 2]
PCS[1,1]=[-1,0,h/3, 1,0,h/3, 0,0, 3]
PCS[1,2]=[-1,0,-h/3, 0,0,1, 0.04,0, 2]
T=np.array([1.6,0.9, *lin([214,226,250]), *lin([255,250,246])])
COL=lin([[250,190,205],[255,214,186],[200,235,215],[214,200,250]])
LC=lin([[255,236,200],[255,224,230],[240,232,255]])
L=np.array([-0.5,-0.4,0.75]); L/=np.linalg.norm(L)
cam=look([0,-2.6,2.4],[0,0,0.05],34)
t=time.time(); img=render(700,450,cam,S,PCS,T,COL,LC,L,1,3); print(time.time()-t)
Image.fromarray(tonemap(img)).save('pt.png')
