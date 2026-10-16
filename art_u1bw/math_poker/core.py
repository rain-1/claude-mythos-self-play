import os
os.environ.setdefault("OMP_NUM_THREADS","1"); os.environ.setdefault("OPENBLAS_NUM_THREADS","1"); os.environ.setdefault("MKL_NUM_THREADS","1")
import numpy as np

def grid(N):
    g=(np.arange(N)+0.5)/N
    H=(g[None,:]>g[:,None]).astype(float); H[np.arange(N),np.arange(N)]=0.5  # H[i,k]=P(z_k beats x_i)
    return g,H

def delta(S,H,lam):
    """Delta[x,y]=E[call]-E[fold] for player seeing (x,y); S[u,v]=sigma(u,v) symmetric."""
    N=S.shape[0]; F=1-S; HF=H*F; SH=S*H
    M = lam*(F@F.T) + (3*lam+2)*(HF@S.T + S@HF.T) - (1+lam)*(F@S.T+S@F.T) + (3*lam+3)*(SH@SH.T) - (1+lam)*(S@S.T)
    D = lam + M/N
    return 0.5*(D+D.T)

def regret(S,D):
    return np.mean(np.maximum(D,0)-S*D)

def logit(D,T):
    return 0.5*(1+np.tanh(D/(2*T)))

def solve(S0,H,lam,T0=0.2,T1=2e-4,iters=3000,alpha=0.3,tol=1e-10):
    S=S0.copy()
    Ts=np.geomspace(T0,T1,iters//2)
    for it in range(iters):
        T=Ts[min(it,len(Ts)-1)]
        D=delta(S,H,lam)
        Sn=(1-alpha)*S+alpha*logit(D,T)
        ch=np.abs(Sn-S).max(); S=Sn
        if it>=len(Ts) and ch<tol: break
    D=delta(S,H,lam)
    return S,D,regret(S,D),it

def solve2(S0,H,lam,T0=0.2,T1=1e-3,levels=30,maxit=600,tol=1e-9,c=3.0):
    S=S0.copy(); tot=0
    for T in np.geomspace(T0,T1,levels):
        a=min(0.5,c*T)
        for it in range(maxit):
            D=delta(S,H,lam); Sn=(1-a)*S+a*logit(D,T); ch=np.abs(Sn-S).max(); S=Sn; tot+=1
            if ch<tol*a: break
    D=delta(S,H,lam)
    return S,D,regret(S,D),tot,ch

from scipy.optimize import newton_krylov, anderson
def solve_nk(S0,H,lam,Ts=(0.02,0.01,0.005,0.0025,0.0012),damp_its=200,verbose=False):
    """damped logit iteration at Ts[0] to land in a basin, then Newton-Krylov continuation in T."""
    S=S0.copy(); T=Ts[0]; a=min(0.5,3*T)
    for it in range(damp_its):
        S=(1-a)*S+a*logit(delta(S,H,lam),T)
    ok=True
    for T in Ts:
        F=lambda X: X-logit(delta(X,H,lam),T)
        try:
            S=newton_krylov(F,S,f_tol=1e-9,maxiter=60,method='lgmres',verbose=verbose)
        except Exception as e:
            ok=False
            S=np.clip(S,0,1)
    S=np.clip(S,0,1); D=delta(S,H,lam)
    res=np.abs(S-logit(D,Ts[-1])).max()
    return S,D,regret(S,D),res,ok

def robust(S0,H,lam,T_start=0.01,T_end=1e-3,n_T=8,damp_its=400,alpha=None):
    S=S0.copy(); T=T_start; a=alpha if alpha else min(0.5,2*T)
    for it in range(damp_its):
        S=(1-a)*S+a*logit(delta(S,H,lam),T)
    for T in np.geomspace(T_start,T_end,n_T):
        F=lambda X: X-logit(delta(X,H,lam),T)
        try:
            S=newton_krylov(F,S,f_tol=1e-9,maxiter=40,method='lgmres')
        except Exception:
            S=np.clip(S,0,1); a=min(0.5,2*T)
            for it in range(1500):
                Sn=(1-a)*S+a*logit(delta(S,H,lam),T); ch=np.abs(Sn-S).max(); S=Sn
                if ch<1e-10: break
    S=np.clip(S,0,1); D=delta(S,H,lam)
    res=np.abs(S-logit(D,T_end)).max()
    return S,D,regret(S,D),res
