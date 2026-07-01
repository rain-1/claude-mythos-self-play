import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from pipedreams import reduced_pipe_dreams, trace_pipes, inv
from figkit import annotate
import colorsys, time

def render(w=(1,4,5,3,2), S=1700):
    t0=time.time(); n=len(w)
    PDs=reduced_pipe_dreams(w)
    PDs=sorted(PDs, key=lambda D: sorted(D))
    m=len(PDs); cols=3; rows=(m+cols-1)//cols
    SS=2; W=S; H=int(S*rows/cols*0.92)+int(S*0.02)
    img=Image.new("RGB",(W*SS,H*SS),(9,10,15)); dr=ImageDraw.Draw(img)
    pw=W*SS/cols; ph=W*SS/cols*0.92
    u=pw*0.72/n   # cell size
    hues=[colorsys.hls_to_rgb((k/n*0.9)%1,0.6,0.95) for k in range(n)]
    pcol=[tuple(int(255*c) for c in h) for h in hues]
    for idx,D in enumerate(PDs):
        pr,pc=divmod(idx,cols)
        ox=pc*pw+pw*0.14; oy=pr*ph+ph*0.16
        # grid cell centers: cell (i,j) top-left at (ox+(j-1)*u, oy+(i-1)*u)
        def C(i,j): return (ox+(j-0.5)*u, oy+(i-0.5)*u)
        def edgept(i,j,side):
            cx,cy=C(i,j); h=u/2
            return {'L':(cx-h,cy),'R':(cx+h,cy),'U':(cx,cy-h),'D':(cx,cy+h)}[side]
        # draw tiles faint (staircase boundary)
        # pipes
        pipes=trace_pipes(D,n)
        for start in range(1,n+1):
            path=pipes[start]; col=pcol[start-1]
            pts=[edgept(path[0][0],path[0][1],'L')]
            for (i,j,d) in path:
                cx,cy=C(i,j)
                pts.append((cx,cy))
            # last exit
            li,lj,ld=path[-1]
            pts.append(edgept(li,lj,'U' if ld=='U' else 'R'))
            dr.line(pts,fill=col,width=max(2,int(SS*2.4)),joint='curve')
        # cross markers
        for (i,j) in D:
            cx,cy=C(i,j); r=u*0.11
            dr.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(250,250,255))
    arr=np.asarray(img).astype(np.float32)/255
    g=arr.copy()
    for k in range(3): g[...,k]+=0.28*gaussian_filter(arr[...,k],SS*1.2)
    out=Image.fromarray((np.clip(g,0,1)*255).astype(np.uint8)).resize((W,H),Image.LANCZOS)
    body=("A permutation, drawn as plumbing. A PIPE DREAM lays n pipes on a triangular board so that the pipe entering "
          "row i leaves at column w(i); at a '+' tile two pipes CROSS, elsewhere they bounce past in an elbow. A pipe "
          "dream is REDUCED when no two pipes cross twice - then its crosses, read along diagonals, spell a reduced word "
          f"for w. Shown: all {m} reduced pipe dreams of w = {''.join(map(str,w))} (each has exactly inv(w) = {inv(w)} "
          "crosses, white dots). Summed with monomial weights they build the SCHUBERT POLYNOMIAL of w; the longest "
          "permutation has just one (the full staircase of crosses). Ladder and chute moves turn any one into any other.")
    fig=annotate(out,"FIGURE 19 - PIPE DREAMS","A Permutation as Plumbing",body,accent=(110,205,225))
    fig.save("19_pipedreams.png"); print("saved",fig.size,"m",m,"t=%.1f"%(time.time()-t0))

if __name__=="__main__": render()
