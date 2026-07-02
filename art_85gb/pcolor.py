import numpy as np

def cyclic_palette(name='iri'):
    # curated cyclic anchor colours (linear-ish RGB 0..1), looped
    P = {
      'iri': [(0.02,0.05,0.18),(0.05,0.35,0.55),(0.15,0.75,0.62),(0.95,0.85,0.35),
              (0.95,0.45,0.25),(0.75,0.20,0.55),(0.30,0.12,0.55),(0.02,0.05,0.18)],
      'thinfilm':[(0.10,0.02,0.30),(0.10,0.45,0.75),(0.25,0.85,0.75),(0.85,0.92,0.55),
                  (0.98,0.70,0.30),(0.90,0.30,0.45),(0.45,0.15,0.65),(0.10,0.02,0.30)],
    }
    return np.array(P[name])

def phase_to_rgb(phase, pal):
    # phase in [-pi,pi] -> [0,1) index into looped palette, linear interp
    u = (phase/(2*np.pi)+0.5) % 1.0
    n = len(pal)-1
    f = u*n
    i = np.floor(f).astype(int); t = (f-i)[...,None]
    i = np.clip(i,0,n-1)
    c = pal[i]*(1-t)+pal[i+1]*t
    return c

def tonemap(amp, k=1.0, gamma=0.85, p=99.6):
    a = amp/np.percentile(amp, p)
    v = 1-np.exp(-k*a)
    return np.clip(v,0,1)**gamma

def compose(Pe, pal, k=2.2, gamma=0.8, sat_hi=0.85, desat_lo=0.55):
    amp = np.abs(Pe)
    v = tonemap(amp, k=k, gamma=gamma)
    hue = phase_to_rgb(np.angle(Pe), pal)   # HxWx3
    # brightness-modulated: multiply hue by value; blaze to white at very high amp
    white = np.clip((v-sat_hi)/(1-sat_hi),0,1)[...,None]
    rgb = hue*v[...,None]
    rgb = rgb*(1-white)+ (0.6+0.4*hue)*white*v[...,None]  # push toward light near peaks
    # lift shadow slightly toward palette-dark navy (already dark)
    return np.clip(rgb,0,1)

def smoothstep(a,b,x):
    t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)

def compose_v3(Pe, pal, base=(0.02,0.06,0.11), k=2.4, gamma=1.05,
               sat_lo=0.06, sat_hi=0.55, blaze=0.86, blaze_soft=0.9):
    amp=np.abs(Pe)
    p=np.percentile(amp,99.6)
    a=amp/p
    v=np.clip(1-np.exp(-k*a),0,1)**gamma
    hue=phase_to_rgb(np.angle(Pe),pal)
    sat=smoothstep(sat_lo,sat_hi,a)[...,None]
    basec=np.array(base)[None,None,:]
    color=basec*(1-sat)+hue*sat
    rgb=color*v[...,None]
    # white-hot blaze at true peaks
    w=smoothstep(blaze,blaze_soft,v)[...,None]
    rgb=rgb*(1-w)+ (0.75+0.25*hue)*w*v[...,None]
    return np.clip(rgb,0,1)
