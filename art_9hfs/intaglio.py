"""intaglio.py — engraved security printing (banknote / bond certificate) as a medium.

Process, not filter:  paper -> pale offset TINTS (fine line guilloche, two inks blending like
iris printing) -> dark INTAGLIO plate (lathe-work rosettes, swelling-line tone engraving,
lettering; white-line work is CUT out of solid ink) -> one letterpress RED (serials).
Everything is a coverage layer in [0,1] with analytic anti-aliasing (distance to the line in
pixels), so there is no supersampling.  Unit u = S/4096; all sizes are given in u.
"""
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont

FONT = {'b': '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf',
        'r': '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
        'i': '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',
        'bi': '/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf',
        'm': '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'}

def aa(d, w):
    """coverage of a stroke of width w (px) at distance d (px) from its centre line"""
    return np.clip(w*0.5 - d + 0.5, 0, 1)

class Plate:
    def __init__(s, S, seed=0, W=None):
        s.S = S; s.W = W or S; s.u = S/4096.0; s.rng = np.random.default_rng(seed)
        s.L = {}
    def layer(s, name):
        if name not in s.L: s.L[name] = np.zeros((s.S, s.W), np.float32)
        return s.L[name]
    # ---- patches -------------------------------------------------------------------
    def box(s, x0, y0, x1, y1):
        x0 = int(max(0, np.floor(x0))); y0 = int(max(0, np.floor(y0)))
        x1 = int(min(s.W, np.ceil(x1))); y1 = int(min(s.S, np.ceil(y1)))
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        return (slice(y0, y1), slice(x0, x1)), xx + 0.5, yy + 0.5
    def put(s, name, sl, cov):
        L = s.layer(name); L[sl] = np.maximum(L[sl], cov.astype(np.float32))
    def cut(s, name, sl, cov):
        L = s.layer(name); L[sl] *= (1 - cov).astype(np.float32)
    # ---- primitives ----------------------------------------------------------------
    def level_lines(s, U, w, gx=None, gy=None):
        """lines along integer level sets of a field U (already in 'line index' units)"""
        if gx is None:
            gy, gx = np.gradient(U)
        g = np.sqrt(gx*gx + gy*gy) + 1e-6
        d = np.abs(U - np.round(U))/g
        return aa(d, w)
    def text(s, name, string, cx, cy, size, font='b', anchor='mm', cut=False, track=0, rot=0, stroke=0):
        """lettering; returns the mask bbox. size in px."""
        f = ImageFont.truetype(FONT[font], max(4, int(round(size))))
        if track:
            widths = [f.getlength(ch) for ch in string]
            Wt = int(sum(widths) + track*(len(string)-1)) + 8
        else:
            Wt = int(f.getlength(string)) + 8
        Ht = int(size*1.5) + 8
        im = Image.new('L', (Wt + 2*stroke + 8, Ht + 2*stroke), 0); dr = ImageDraw.Draw(im)
        if track:
            x = 4 + stroke
            for ch, wd in zip(string, widths):
                dr.text((x, Ht/2 + stroke), ch, 255, font=f, anchor='lm', stroke_width=stroke, stroke_fill=255); x += wd + track
        else:
            dr.text((4 + stroke, Ht/2 + stroke), string, 255, font=f, anchor='lm', stroke_width=stroke, stroke_fill=255)
        bb = im.getbbox()
        if bb is None: return None
        im = im.crop(bb)
        if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
        a = np.asarray(im, np.float32)/255.0
        h, w = a.shape
        ax = {'l': 0, 'm': w/2, 'r': w}[anchor[0]]; ay = {'t': 0, 'm': h/2, 'b': h}[anchor[1]]
        x0 = int(round(cx - ax)); y0 = int(round(cy - ay))
        xa, ya = max(0, x0), max(0, y0); xb, yb = min(s.W, x0+w), min(s.S, y0+h)
        if xb <= xa or yb <= ya: return None
        sub = a[ya-y0:yb-y0, xa-x0:xb-x0]; sl = (slice(ya, yb), slice(xa, xb))
        if cut: s.cut(name, sl, sub)
        else: s.put(name, sl, sub)
        return (xa, ya, xb, yb)
    def text_mask(s, string, size, font='b'):
        f = ImageFont.truetype(FONT[font], int(round(size)))
        Wt = int(f.getlength(string)) + 16; Ht = int(size*1.6)
        im = Image.new('L', (Wt, Ht), 0); ImageDraw.Draw(im).text((8, Ht/2), string, 255, font=f, anchor='lm')
        im = im.crop(im.getbbox()); return np.asarray(im, np.float32)/255.0
    # ---- lathe work ----------------------------------------------------------------
    def rosette_cov(s, xx, yy, cx, cy, R, bands, w, rim=True, hub=0.0):
        """bands = [(rho, amp, lobes, strands, phase)], radii as fractions of R.
        each strand r(th) = R(rho + amp cos(lobes th + 2 pi j/strands + phase))."""
        dx = xx - cx; dy = yy - cy
        r = np.sqrt(dx*dx + dy*dy) + 1e-6; th = np.arctan2(dy, dx)
        cov = np.zeros_like(r)
        for (rho, amp, n, J, ph) in bands:
            sel = (r > R*(rho - abs(amp)) - 3*w) & (r < R*(rho + abs(amp)) + 3*w)
            if not sel.any(): continue
            rs = r[sel]; ts = th[sel]; c = np.zeros_like(rs)
            for j in range(J):
                a = n*ts + 2*np.pi*j/J + ph
                rj = R*(rho + amp*np.cos(a)); drj = -R*amp*n*np.sin(a)
                d = np.abs(rs - rj)/np.sqrt(1 + (drj/rs)**2)
                c = np.maximum(c, aa(d, w))
            cov[sel] = np.maximum(cov[sel], c)
        if rim:
            for rr, ww in ((1.0, 2.2*w), (0.955, 0.9*w)):
                cov = np.maximum(cov, aa(np.abs(r - R*rr), ww))
        if hub:
            cov = np.maximum(cov, aa(np.abs(r - R*hub), 1.6*w))
        return cov, r, th
    def band_cov(s, sc, tc, half, strands, period, w, amp=0.86, ph=0.0, rails=True):
        """straight (or bent) guilloche band. sc = coordinate along, tc = across, |tc|<half."""
        cov = np.zeros_like(sc)
        k = 2*np.pi/period
        for j in range(strands):
            a = k*sc + 2*np.pi*j/strands + ph
            t0 = amp*half*np.cos(a); dt = -amp*half*k*np.sin(a)
            d = np.abs(tc - t0)/np.sqrt(1 + dt*dt)
            cov = np.maximum(cov, aa(d, w))
        if rails:
            cov = np.maximum(cov, aa(np.abs(np.abs(tc) - half), 1.8*w))
        return cov*(np.abs(tc) < half + 2*w)
    # ---- tone engraving --------------------------------------------------------------
    def engrave(s, T, xx, yy, pitch, ang=0.0, wave=0.0, wlen=200.0, cross=0.55, wmin=0.0, wmax=0.92):
        """swelling-line engraving of a tone T in [0,1] (1 = dark). pitch in px.
        second (cross) family comes in above tone `cross`."""
        ca, sa = np.cos(ang), np.sin(ang)
        p = xx*ca + yy*sa; q = -xx*sa + yy*ca
        U = (q + wave*np.sin(2*np.pi*p/wlen))/pitch
        g = np.sqrt(1 + (wave*2*np.pi/wlen*np.cos(2*np.pi*p/wlen))**2)/pitch
        d = np.abs(U - np.round(U))/g
        w1 = pitch*np.clip(wmin + (wmax - wmin)*np.clip(T/ max(cross, 1e-3), 0, 1)*0.62 + 0.38*(wmax-wmin)*np.clip((T-cross)/(1-cross+1e-6), 0, 1)*0, 0, 1)
        cov = aa(d, w1)*(T > 0.012)
        if cross < 1:
            T2 = np.clip((T - cross)/(1 - cross), 0, 1)
            ang2 = ang + np.pi*0.36
            c2, s2 = np.cos(ang2), np.sin(ang2)
            U2 = (-xx*s2 + yy*c2)/pitch
            d2 = np.abs(U2 - np.round(U2))*pitch
            cov = np.maximum(cov, aa(d2, pitch*0.6*T2)*(T2 > 0.02))
        return cov
    def engrave_field(s, T, U, wmin=0.0, wmax=0.9, gamma=1.0):
        """swelling lines along the integer level sets of U; local width = tone x local pitch"""
        gy, gx = np.gradient(U)
        g = np.sqrt(gx*gx + gy*gy) + 1e-6
        d = np.abs(U - np.round(U))/g
        w = (wmin + (wmax - wmin)*np.clip(T, 0, 1)**gamma)/g
        return aa(d, w)*(T > 0.01)
    # ---- printing ----------------------------------------------------------------------
    def render(s, inks, order, paper=(0.957, 0.937, 0.888), plate=None, relief=1.0):
        S, W, u = s.S, s.W, s.u; rng = s.rng
        # paper: laid tone, fibres, mottling
        n1 = ndi.gaussian_filter(rng.standard_normal((S, W)).astype(np.float32), 40*u)
        n1 /= n1.std() + 1e-6
        n2 = ndi.gaussian_filter(rng.standard_normal((S, W)).astype(np.float32), (0.7*u + 0.3, 5*u))
        n2 /= n2.std() + 1e-6
        n3 = rng.standard_normal((S, W)).astype(np.float32)
        tone = 1 + 0.012*n1 + 0.010*n2 + 0.008*n3
        rgb = np.empty((S, W, 3), np.float32)
        for c in range(3): rgb[..., c] = paper[c]*tone
        rgb[..., 2] *= 1 - 0.01*n1
        hsum = np.zeros((S, W), np.float32)
        for name in order:
            if name not in s.L: continue
            col, kind = inks[name]
            cov = s.L[name]
            if kind == 'intaglio':
                cov = ndi.gaussian_filter(cov, 0.35*u + 0.15)
                cov = np.clip(cov*1.08, 0, 1)
                # ink is not perfectly even: slightly starved in solids, plate tone elsewhere
                starve = 1 - 0.07*np.clip(ndi.gaussian_filter(cov, 6*u), 0, 1)*(0.5 + 0.5*n2)
                dens = cov*starve
                hsum += dens
            elif kind == 'offset':
                dens = ndi.gaussian_filter(cov, 0.3*u + 0.1)*(0.93 + 0.07*n1)
            else:  # letterpress
                c1 = ndi.gaussian_filter(cov, 0.5*u + 0.2)
                edge = np.clip(c1*(1 - c1)*4, 0, 1)
                dens = np.clip(c1*0.90 + 0.25*edge*c1 + 0.05*n3*c1, 0, 1)
            for c in range(3):
                rgb[..., c] *= 1 - dens*(1 - col[c])
        # intaglio relief: the ink stands on the paper; light from upper left
        if relief:
            h = ndi.gaussian_filter(hsum, 1.1*u + 0.3)
            k = max(1, int(round(1.2*u)))
            sh = np.roll(np.roll(h, k, 0), k, 1) - np.roll(np.roll(h, -k, 0), -k, 1)
            rgb *= (1 - 0.10*relief*sh)[..., None]
        if plate is not None:      # plate mark: a shallow pressed rectangle
            x0, y0, x1, y1 = plate
            yy, xx = np.mgrid[0:S, 0:W].astype(np.float32)
            dd = np.maximum(np.maximum(x0 - xx, xx - x1), np.maximum(y0 - yy, yy - y1))
            inside = np.clip(-dd/(3*u) + 0.5, 0, 1)
            rgb *= (1 - 0.022*inside)[..., None]
            lip = np.exp(-(dd/(2.5*u))**2)
            lightside = np.where((np.abs(xx - x0) < np.abs(xx - x1)) & (np.abs(yy - y0) < np.abs(yy - y1)), -1.0, 1.0)
            rgb *= (1 + 0.035*lip*lightside)[..., None]
        # gentle vignette of age at the sheet edge
        yy, xx = np.mgrid[0:S, 0:W].astype(np.float32)
        e = np.minimum(np.minimum(xx, W - xx), np.minimum(yy, S - yy))/(120*u)
        rgb *= (1 - 0.05*np.exp(-e))[..., None]
        return (np.clip(rgb, 0, 1)*255 + 0.5).astype(np.uint8)

INKS = {'tintA': ((0.93, 0.66, 0.66), 'offset'),      # rose
        'tintB': ((0.60, 0.80, 0.78), 'offset'),      # aqua
        'tintC': ((0.94, 0.84, 0.55), 'offset'),      # straw
        'dark':  ((0.075, 0.105, 0.235), 'intaglio'), # indigo-black
        'red':   ((0.80, 0.14, 0.11), 'letterpress')}
ORDER = ['tintC', 'tintA', 'tintB', 'dark', 'red']

# five lathe settings; digit d uses DESIGN[d mod 5] — black-line for the low half of the
# digits, white-line (cut from solid ink) for the high half.
DESIGNS = [
    [(0.775, 0.175, 8, 8, 0.0), (0.50, 0.075, 16, 4, 0.0)],
    [(0.775, 0.175, 12, 6, 0.0), (0.50, 0.075, 6, 6, 0.5)],
    [(0.775, 0.175, 5, 10, 0.0), (0.50, 0.075, 10, 5, 0.0)],
    [(0.775, 0.175, 16, 4, 0.0), (0.50, 0.075, 8, 8, 0.3)],
    [(0.775, 0.175, 6, 12, 0.0), (0.50, 0.075, 24, 3, 0.0)],
    [(0.775, 0.175, 3, 14, 0.0), (0.50, 0.075, 9, 6, 0.0)],
    [(0.775, 0.175, 10, 7, 0.0), (0.50, 0.075, 5, 9, 0.0)],
    [(0.775, 0.175, 4, 13, 0.0), (0.50, 0.075, 12, 5, 0.0)],
    [(0.775, 0.175, 20, 4, 0.0), (0.50, 0.075, 7, 7, 0.0)],
]
GLYPH = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ'

def medallion(P, cx, cy, R, d, base, numeral=True, w=None, font='b'):
    """one digit as a lathe-work medallion: black-line if d < base/2, white-line otherwise"""
    u = P.u; w = w or 2.3*u
    h = base//2; k = d % h if base % 2 == 0 else d % ((base+1)//2)
    neg = (d >= h) if base % 2 == 0 else (d >= (base+1)//2)
    sl, xx, yy = P.box(cx - R - 6*u, cy - R - 6*u, cx + R + 6*u, cy + R + 6*u)
    cov, r, th = P.rosette_cov(xx, yy, cx, cy, R, DESIGNS[k % len(DESIGNS)], w, hub=0.385)
    disc = aa(r - R, 0)            # 1 inside
    disc = np.clip(R - r + 0.5, 0, 1)
    for t in ('tintA', 'tintB', 'tintC'):
        if t in P.L: P.cut(t, sl, disc*0.75)
    hub = np.clip(R*0.385 - r + 0.5, 0, 1)
    if not neg:
        P.cut('dark', sl, disc)
        P.put('dark', sl, cov)
    else:
        P.cut('dark', sl, disc)
        cov, r, th = P.rosette_cov(xx, yy, cx, cy, R, DESIGNS[k % len(DESIGNS)], w*0.62, hub=0.385)
        solid = disc*(1 - cov*0.97)
        P.put('dark', sl, solid)
    if numeral:
        g = GLYPH[d]
        if not neg:
            P.cut('dark', sl, np.clip(R*0.375 - r + 0.5, 0, 1)*0)   # hub stays open
            P.text('dark', g, cx, cy, R*0.60, font)
        else:
            P.text('dark', g, cx, cy, R*0.60, font, cut=True)
    return neg
